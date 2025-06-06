import psycopg2
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QHBoxLayout, QPushButton,
                             QLineEdit, QTableWidget, QTableWidgetItem, QMessageBox,
                             QDialog, QFormLayout, QDialogButtonBox, QHeaderView,
                             QComboBox, QDateEdit, QSizePolicy, QApplication,
                             QLabel, QStyledItemDelegate)
from PyQt5.QtCore import Qt, QDate

def get_db_connection():
    return psycopg2.connect(
        host="localhost",
        database="SAMPLE",
        user="postgres",
        password="123"
    )

class StoragePage(QWidget):
    def __init__(self, container_count=9):
        super().__init__()
        self.container_count = container_count
        self.items = []
        self.init_ui()
        self.load_items_from_db()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(10)

        title_label = QLabel("Storage Inventory")
        title_label.setStyleSheet("""
            background-color: #FFE1D3;
            padding: 10px;
            border-radius: 10px;
            font-weight: bold;
            font-size: 22px;
        """)
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)

        control_layout = QHBoxLayout()
        self.search_bar = QLineEdit()
        self.search_bar.setFixedHeight(45)
        self.search_bar.setFixedWidth(400)
        self.search_bar.setStyleSheet("""
            QLineEdit {
                background-color: #FFF0F5;
                border: 2px solid #D295BF;
                border-radius: 5px;
                padding: 8px 12px;
                font-size: 16px;
                color: #333;
            }
            QLineEdit:focus {
                border: 2px solid #BA74AD;
                background-color: #FFE9F1;
            }
        """)
        self.search_bar.setPlaceholderText("Search item...")
        self.search_bar.textChanged.connect(self.search_items)

        add_btn = QPushButton("Add Item")
        add_btn.setFixedWidth(150)
        add_btn.setStyleSheet("background-color: #D295BF; color: white; padding: 13px 20px; font-size: 16px;")
        add_btn.clicked.connect(self.add_item)

        control_layout.addWidget(self.search_bar)
        control_layout.addStretch()
        control_layout.addWidget(add_btn)
        main_layout.addLayout(control_layout)

        self.table = QTableWidget(0, 7)
        self.table.setHorizontalHeaderLabels(["Name", "Quantity", "Dosage", "Unit", "Expiry Date", "Status", "Actions"])
        font = self.table.font()
        font.setPointSize(13)
        self.table.setFont(font)
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #FFF5F0;
            }
            QTableWidget::item {
                font-size: 18px;
            }
            QHeaderView::section {
                font-size: 20px;
                font-weight: bold;
                background-color: #FFE1D3;
                border: 1px solid #D295BF;
            }
            QTableCornerButton::section {
                background-color: #FFE1D3;
                border: 1px solid #D295BF;
            }
        """)
        header = self.table.horizontalHeader()
        header.setSectionsMovable(False)
        for i in range(7):
            header.setSectionResizeMode(i, QHeaderView.Stretch)
        self.table.setItemDelegateForColumn(0, WordWrapDelegate(self.table))
        self.table.setSortingEnabled(False)
        main_layout.addWidget(self.table)

    def load_items_from_db(self):
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("""
                SELECT invitem_id, invitem_name, invitem_quantity, invitem_dosage, invitem_unit, 
                       invitem_expiry_date, invitem_status
                FROM inventory_item
                ORDER BY invitem_id
            """)
            self.items = []
            for row in cur.fetchall():
                self.items.append({
                    'id': row[0],
                    'name': row[1],
                    'quantity': str(row[2]),
                    'dosage': row[3] or '',
                    'unit': row[4] or '',
                    'expiry': row[5].strftime("%Y-%m-%d") if row[5] else '',
                    'status': row[6] or ''
                })
            cur.close()
            conn.close()
            self.refresh_table()
        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"Failed to load inventory: {e}")

    def add_item(self):
        dialog = ItemDialog()
        if dialog.exec_() == QDialog.Accepted:
            new_item = {
                'name': dialog.name_edit.text(),
                'quantity': dialog.quantity_edit.text(),
                'dosage': dialog.dosage_edit.text(),
                'unit': dialog.unit_edit.text(),
                'expiry': dialog.expiry_edit.date().toString("yyyy-MM-dd"),
                'status': dialog.status_combo.currentText()
            }
            try:
                conn = get_db_connection()
                cur = conn.cursor()
                cur.execute("""
                    INSERT INTO inventory_item (invitem_name, invitem_quantity, invitem_dosage, invitem_unit, invitem_expiry_date, invitem_status)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    RETURNING invitem_id
                """, (new_item['name'], new_item['quantity'], new_item['dosage'], new_item['unit'], new_item['expiry'],
                      new_item['status']))
                new_item['id'] = cur.fetchone()[0]
                conn.commit()
                cur.close()
                conn.close()
                self.load_items_from_db()
            except Exception as e:
                QMessageBox.critical(self, "Database Error", f"Failed to add item: {e}")

    def edit_item(self, row):
        item = self.items[row]
        expiry_date = QDate.fromString(item['expiry'], "yyyy-MM-dd")
        dialog = ItemDialog(
            name=item['name'],
            quantity=item['quantity'],
            dosage=item['dosage'],
            unit=item['unit'],
            expiry=expiry_date,
            status=item['status']
        )
        if dialog.exec_() == QDialog.Accepted:
            updated_item = {
                'name': dialog.name_edit.text(),
                'quantity': dialog.quantity_edit.text(),
                'dosage': dialog.dosage_edit.text(),
                'unit': dialog.unit_edit.text(),
                'expiry': dialog.expiry_edit.date().toString("yyyy-MM-dd"),
                'status': dialog.status_combo.currentText()
            }
            try:
                conn = get_db_connection()
                cur = conn.cursor()
                cur.execute("""
                    UPDATE inventory_item 
                    SET invitem_name=%s, invitem_quantity=%s, invitem_dosage=%s, invitem_unit=%s, 
                        invitem_expiry_date=%s, invitem_status=%s, updated_at=NOW()
                    WHERE invitem_id=%s
                """, (updated_item['name'], updated_item['quantity'], updated_item['dosage'], updated_item['unit'],
                      updated_item['expiry'], updated_item['status'], item['id']))
                conn.commit()
                cur.close()
                conn.close()
                self.load_items_from_db()
            except Exception as e:
                QMessageBox.critical(self, "Database Error", f"Failed to update item: {e}")

    def delete_item(self, row):
        item_id = self.items[row]['id']
        reply = QMessageBox.question(self, 'Delete Item',
                                     f"Are you sure you want to delete '{self.items[row]['name']}'?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                conn = get_db_connection()
                cur = conn.cursor()
                cur.execute("DELETE FROM inventory_item WHERE invitem_id=%s", (item_id,))
                conn.commit()
                cur.close()
                conn.close()
                self.load_items_from_db()
            except Exception as e:
                QMessageBox.critical(self, "Database Error", f"Failed to delete item: {e}")

    def refresh_table(self):
        self.table.setRowCount(0)
        for idx, item in enumerate(self.items):
            self.table.insertRow(idx)

            # Make all columns non-editable
            for col, val in enumerate(
                    [item['name'], item['quantity'], item['dosage'], item['unit'], item['expiry'], item['status']]):
                item_obj = QTableWidgetItem(val)
                item_obj.setFlags(item_obj.flags() & ~Qt.ItemIsEditable)
                self.table.setItem(idx, col, item_obj)

            # Buttons
            edit_btn = QPushButton("Edit")
            delete_btn = QPushButton("Delete")
            edit_btn.setStyleSheet("""
                QPushButton {
                    background-color: #a3d5ff;
                    padding: 5px;
                    font-size: 16px;
                    border-radius: 5px;
                }
                QPushButton:hover {
                    background-color: #8cc0f0;
                }
            """)
            delete_btn.setStyleSheet("""
                QPushButton {
                    background-color: #ff9999;
                    padding: 5px;
                    font-size: 16px;
                    border-radius: 5px;
                }
                QPushButton:hover {
                    background-color: #e08888;
                }
            """)
            edit_btn.clicked.connect(lambda _, row=idx: self.edit_item(row))
            delete_btn.clicked.connect(lambda _, row=idx: self.delete_item(row))

            btn_layout = QHBoxLayout()
            btn_layout.addWidget(edit_btn)
            btn_layout.addWidget(delete_btn)
            btn_layout.setContentsMargins(0, 0, 0, 0)
            btn_layout.setSpacing(5)

            btn_widget = QWidget()
            btn_widget.setLayout(btn_layout)
            self.table.setCellWidget(idx, 6, btn_widget)

    def search_items(self):
        query = self.search_bar.text().lower()
        for row in range(self.table.rowCount()):
            item_name = self.table.item(row, 0).text().lower()
            is_visible = query in item_name
            self.table.setRowHidden(row, not is_visible)

class WordWrapDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)

    def paint(self, painter, option, index):
        option.displayAlignment = Qt.AlignLeft | Qt.AlignVCenter
        option.textElideMode = Qt.ElideNone
        super().paint(painter, option, index)

    def sizeHint(self, option, index):
        option.textElideMode = Qt.ElideNone
        return super().sizeHint(option, index)

class ItemDialog(QDialog):
    def __init__(self, name="", quantity="", dosage="", unit="", expiry=None, status="Available"):
        super().__init__()
        self.setWindowTitle("Item Details")
        self.setFixedSize(500, 450)
        self.setStyleSheet("""
            QDialog {
                background-color: #FFF5F0;
            }
            QLabel {
                font-size: 18px;
                font-weight: bold;
                padding: 5px;
            }
            QLineEdit, QComboBox, QDateEdit {
                font-size: 18px;
                padding: 10px;
                border: 2px solid #D295BF;
                border-radius: 8px;
                min-height: 30px;
            }
            QPushButton {
                font-size: 16px;
                padding: 8px 16px;
            }
        """)

        layout = QFormLayout(self)
        layout.setVerticalSpacing(15)
        layout.setHorizontalSpacing(20)

        self.name_edit = QLineEdit(name)
        self.name_edit.setPlaceholderText("Enter item name (eg., Paracetamol)")
        self.name_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        layout.addRow(QLabel("Name:"), self.name_edit)

        quantity_layout = QHBoxLayout()
        self.quantity_edit = QLineEdit(quantity)
        self.quantity_edit.setPlaceholderText("Enter quantity (eg., 10)")
        self.quantity_edit.setFixedHeight(50)

        self.minus_btn = QPushButton("-")
        self.minus_btn.setFixedSize(45, 45)
        self.plus_btn = QPushButton("+")
        self.plus_btn.setFixedSize(45, 45)

        btns_widget = QWidget()
        btns_layout = QHBoxLayout()
        btns_layout.setContentsMargins(10, 4, 0, 4)
        btns_layout.setSpacing(8)
        btns_layout.addWidget(self.minus_btn)
        btns_layout.addWidget(self.plus_btn)
        btns_widget.setLayout(btns_layout)

        quantity_layout.addWidget(self.quantity_edit)
        quantity_layout.addWidget(btns_widget, alignment=Qt.AlignVCenter)

        layout.addRow(QLabel("Quantity:"), quantity_layout)

        self.plus_btn.clicked.connect(self.increment_quantity)
        self.minus_btn.clicked.connect(self.decrement_quantity)

        self.dosage_edit = QLineEdit(dosage)
        self.dosage_edit.setPlaceholderText("Enter dosage (eg., 500g, 60ml)")
        self.dosage_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        layout.addRow(QLabel("Dosage:"), self.dosage_edit)

        self.unit_edit = QLineEdit(unit)
        self.unit_edit.setPlaceholderText("Enter unit (eg., Tablet, Capsule, ml)")
        self.unit_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        layout.addRow(QLabel("Unit:"), self.unit_edit)

        self.expiry_edit = QDateEdit()
        self.expiry_edit.setCalendarPopup(True)
        self.expiry_edit.setDate(expiry if expiry else QDate.currentDate().addYears(1))
        self.expiry_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.expiry_edit.setStyleSheet("padding: 8px;")
        layout.addRow(QLabel("Expiry Date:"), self.expiry_edit)

        self.status_combo = QComboBox()
        self.status_combo.addItems(["Available", "Not Available"])
        self.status_combo.setCurrentText(status if status in ["Available", "Not Available"] else "Available")
        self.status_combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        layout.addRow(QLabel("Status:"), self.status_combo)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.setStyleSheet("""
            QPushButton {
                min-width: 100px;
                min-height: 30px;
                font-size: 18px;
            }
        """)
        buttons.accepted.connect(self.validate_input)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

    def validate_input(self):
        if not self.name_edit.text().strip():
            QMessageBox.warning(self, "Error", "Please enter an item name")
            return
        if not self.quantity_edit.text().strip():
            QMessageBox.warning(self, "Error", "Please enter a quantity")
            return
        try:
            float(self.quantity_edit.text())
        except ValueError:
            QMessageBox.warning(self, "Error", "Quantity must be a number")
            return
        if not self.unit_edit.text().strip():
            QMessageBox.warning(self, "Error", "Please enter a unit")
            return
        self.accept()

    def increment_quantity(self):
        try:
            value = float(self.quantity_edit.text()) if self.quantity_edit.text() else 0
            value += 1
            self.quantity_edit.setText(str(int(value)) if value.is_integer() else str(value))
        except ValueError:
            self.quantity_edit.setText("1")

    def decrement_quantity(self):
        try:
            value = float(self.quantity_edit.text()) if self.quantity_edit.text() else 0
            value -= 1
            if value < 0:
                value = 0
            self.quantity_edit.setText(str(int(value)) if value.is_integer() else str(value))
        except ValueError:
            self.quantity_edit.setText("0")