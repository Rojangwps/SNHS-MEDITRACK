import psycopg2
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QHBoxLayout, QPushButton, QLineEdit,
    QTableWidget, QTableWidgetItem, QMessageBox, QDialog, QFormLayout,
    QDialogButtonBox, QHeaderView, QComboBox, QDateEdit, QSizePolicy,
    QStyledItemDelegate
)
from PyQt5.QtCore import Qt, QDate, QPoint
import sys

def get_db_connection():
    return psycopg2.connect(
        host="localhost",
        database="MediTrackSNHS",
        user="postgres",
        password="Mylovemondejar"
    )

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

        # Connect signals
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

class StorageHistoryDialog(QDialog):
    def __init__(self, history_rows, all_items=False, cell_center_pos=None):
        super().__init__()
        self.setWindowTitle("Storage Item History" if not all_items else "Storage History (All Items)")
        self.setMinimumSize(1200, 600)
        self.resize(1500, 700)
        self.setStyleSheet("""
            QDialog {
                background-color: #FDE1D3;
            }
            QLabel#Header {
                font-size: 34px;
                font-weight: bold;
                background: transparent;
                padding: 40px 0 20px 0;
            }
            QTableWidget {
                background: #fff6f0;
                font-size: 18px;
            }
            QHeaderView::section {
                font-size: 19px;
                font-weight: bold;
                background: #FFE1D3;
                border: 1px solid #D295BF;
            }
            QPushButton#BackBtn {
                font-size: 20px;
                background-color: #ffe599;
                color: #333;
                border-radius: 8px;
                padding: 12px 38px;
            }
        """)

        vbox = QVBoxLayout(self)
        vbox.setContentsMargins(36, 36, 36, 36)
        vbox.setSpacing(16)

        header = QLabel("Storage Item History" if not all_items else "Storage History (All Items)")
        header.setObjectName("Header")
        header.setAlignment(Qt.AlignCenter)
        vbox.addWidget(header)

        table = QTableWidget()
        table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        if all_items:
            table.setColumnCount(9)
            table.setHorizontalHeaderLabels([
                "Date", "Action", "Item", "Qty Before", "Qty After", "Change", "Student ID", "Student Name", "Details"
            ])
        else:
            table.setColumnCount(8)
            table.setHorizontalHeaderLabels([
                "Date", "Action", "Qty Before", "Qty After", "Change", "Student ID", "Student Name", "Details"
            ])
        table.setRowCount(len(history_rows))
        for i, row in enumerate(history_rows):
            for j, value in enumerate(row):
                table.setItem(i, j, QTableWidgetItem(str(value) if value is not None else ""))
                item = QTableWidgetItem(str(value) if value is not None else "")
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                table.setItem(i, j, item)
                
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        table.setMinimumHeight(400)
        vbox.addWidget(table, stretch=1)

        btns = QHBoxLayout()
        btns.addStretch(1)
        back_btn = QPushButton("Back")
        back_btn.setObjectName("BackBtn")
        back_btn.clicked.connect(self.reject)
        btns.addWidget(back_btn)
        vbox.addLayout(btns)

        # Center dialog on the specified cell or widget
        if cell_center_pos:
            # Ensure dialog is shown so geometry is correct
            self.show()
            self.repaint()
            self.raise_()
            QApplication.processEvents()
            # Move dialog so its center matches the cell_center_pos
            geo = self.frameGeometry()
            geo.moveCenter(cell_center_pos)
            self.move(geo.topLeft())

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
            font-size: 28px;
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
        add_btn.setStyleSheet("background-color: #D295BF; color: white; font-weight: bold; padding: 15px; border-radius: 10px; font-size: 18px;")
        add_btn.clicked.connect(self.add_item)

        history_btn = QPushButton("View Storage History")
        history_btn.setFixedWidth(235)
        history_btn.setStyleSheet("background-color: #5DADE2; color: white;font-weight: bold; padding: 15px; border-radius: 10px; font-size: 18px;")
        history_btn.clicked.connect(self.show_history_all)

        control_layout.addWidget(self.search_bar)
        control_layout.addStretch()
        control_layout.addWidget(add_btn)
        control_layout.addWidget(history_btn)
        main_layout.addLayout(control_layout)

        self.table = QTableWidget(0, 8)
        self.table.setHorizontalHeaderLabels([
            "Name", "Quantity", "Dosage", "Unit", "Expiry Date", "Status", "Actions", "History"
        ])
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
        for i in range(8):
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
                """, (new_item['name'], new_item['quantity'], new_item['dosage'], new_item['unit'], new_item['expiry'], new_item['status']))
                new_item['id'] = cur.fetchone()[0]
                self.log_storage_history(new_item['id'], "added", 0, int(new_item['quantity']), int(new_item['quantity']), None, None, "New item added")
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
                qty_before = int(item['quantity'])
                qty_after = int(updated_item['quantity'])
                qty_change = qty_after - qty_before
                cur.execute("""
                    UPDATE inventory_item 
                    SET invitem_name=%s, invitem_quantity=%s, invitem_dosage=%s, invitem_unit=%s, 
                        invitem_expiry_date=%s, invitem_status=%s, updated_at=NOW()
                    WHERE invitem_id=%s
                """, (updated_item['name'], updated_item['quantity'], updated_item['dosage'], updated_item['unit'],
                      updated_item['expiry'], updated_item['status'], item['id']))
                self.log_storage_history(item['id'], "updated", qty_before, qty_after, qty_change, None, None, "Item updated")
                conn.commit()
                cur.close()
                conn.close()
                self.load_items_from_db()
            except Exception as e:
                QMessageBox.critical(self, "Database Error", f"Failed to update item: {e}")

    def delete_item(self, row):
        item_id = self.items[row]['id']
        qty_before = int(self.items[row]['quantity'])
        reply = QMessageBox.question(self, 'Delete Item',
                                     f"Are you sure you want to delete '{self.items[row]['name']}'?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                conn = get_db_connection()
                cur = conn.cursor()
                cur.execute("DELETE FROM inventory_item WHERE invitem_id=%s", (item_id,))
                self.log_storage_history(item_id, "deleted", qty_before, 0, -qty_before, None, None, "Item deleted")
                conn.commit()
                cur.close()
                conn.close()
                self.load_items_from_db()
            except Exception as e:
                QMessageBox.critical(self, "Database Error", f"Failed to delete item: {e}")

    def student_exists(self, student_id):
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("SELECT 1 FROM student WHERE stud_id=%s", (student_id,))
            exists = cur.fetchone() is not None
            cur.close()
            conn.close()
            return exists
        except Exception:
            return False

    def dispense_item(self, row):
        item = self.items[row]
        dialog = DispenseDialog(int(item['quantity']), self.student_exists)
        if dialog.exec_() == QDialog.Accepted:
            qty, student_id, disp_date, notes = dialog.get_data()
            qty_before = int(item['quantity'])
            qty_after = qty_before - qty
            if qty <= 0 or qty > qty_before:
                QMessageBox.warning(self, "Invalid quantity", "Check quantity to dispense.")
                return
            try:
                conn = get_db_connection()
                cur = conn.cursor()
                cur.execute(
                    "UPDATE inventory_item SET invitem_quantity=%s, updated_at=NOW() WHERE invitem_id=%s",
                    (qty_after, item['id'])
                )
                self.log_storage_history(
                    item['id'],
                    "dispensed",
                    qty_before,
                    qty_after,
                    -qty,
                    dispensed_to_student_id=student_id,
                    dispensed_date=disp_date,
                    details=notes
                )
                conn.commit()
                cur.close()
                conn.close()
                self.load_items_from_db()
            except Exception as e:
                QMessageBox.critical(self, "Database Error", f"Failed to dispense: {e}")

    def log_storage_history(self, invitem_id, action, qty_before, qty_after, change, dispensed_to_student_id=None, dispensed_date=None, details=None):
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO storage_history (invitem_id, action, quantity_before, quantity_after, change, dispensed_to_student_id, dispensed_date, details)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (invitem_id, action, qty_before, qty_after, change, dispensed_to_student_id, dispensed_date, details))
            conn.commit()
            cur.close()
            conn.close()
        except Exception as e:
            print("Storage history logging error:", e)

    def refresh_table(self):
        self.table.setRowCount(0)
        for idx, item in enumerate(self.items):
            self.table.insertRow(idx)
            for col, val in enumerate([item['name'], item['quantity'], item['dosage'], item['unit'], item['expiry'], item['status']]):
                item_obj = QTableWidgetItem(val)
                item_obj.setFlags(item_obj.flags() & ~Qt.ItemIsEditable)
                self.table.setItem(idx, col, item_obj)

            edit_btn = QPushButton("Edit")
            delete_btn = QPushButton("Delete")
            dispense_btn = QPushButton("Dispense")
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
            dispense_btn.setStyleSheet("""
                QPushButton {
                    background-color: #7dcea0;
                    padding: 5px;
                    font-size: 16px;
                    border-radius: 5px;
                }
                QPushButton:hover {
                    background-color: #51956b;
                }
            """)
            edit_btn.clicked.connect(lambda _, row=idx: self.edit_item(row))
            delete_btn.clicked.connect(lambda _, row=idx: self.delete_item(row))
            dispense_btn.clicked.connect(lambda _, row=idx: self.dispense_item(row))

            btn_layout = QHBoxLayout()
            btn_layout.addWidget(edit_btn)
            btn_layout.addWidget(delete_btn)
            btn_layout.addWidget(dispense_btn)
            btn_layout.setContentsMargins(0, 0, 0, 0)
            btn_layout.setSpacing(5)
            btn_widget = QWidget()
            btn_widget.setLayout(btn_layout)
            btn_widget.setStyleSheet("background-color: #FFF5F0;")
            self.table.setCellWidget(idx, 6, btn_widget)

            history_btn = QPushButton("History")
            history_btn.setFixedWidth(90)  # Adjust width as you like
            history_btn.setFixedHeight(30)  # Adjust height for vertical centering

            history_widget = QWidget()
            history_layout = QHBoxLayout()
            history_layout.setContentsMargins(0, 0, 0, 1)
            history_layout.setSpacing(0)
            history_layout.addStretch()  # optional: for full center effect
            history_layout.addWidget(history_btn, alignment=Qt.AlignCenter)
            history_widget.setStyleSheet("background-color: #FFF5F0;")
            history_layout.addStretch()  # optional
            history_widget.setLayout(history_layout)
            history_btn.setStyleSheet("""
                QPushButton {
                    background-color: #ffe599;
                    padding: 5px;
                    font-size: 16px;
                    border-radius: 5px;
                    min-width: 120px; 
                    max-width: 120px;
                }
                QPushButton:hover {
                    background-color: #eedd82;
                }
            """)
            # Pass the button widget to show_history for centering
            history_btn.clicked.connect(lambda _, invitem_id=item['id'], btn=history_btn: self.show_history(invitem_id, btn))
            self.table.setCellWidget(idx, 7, history_widget)

    def search_items(self):
        query = self.search_bar.text().lower()
        for row in range(self.table.rowCount()):
            row_text = ""
            for col in range(self.table.columnCount()):
                item = self.table.item(row, col)
                if item is not None:
                    row_text += item.text().lower() + " "
            is_visible = query in row_text
            self.table.setRowHidden(row, not is_visible)

    def show_history(self, invitem_id, cell_widget=None):
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("""
                SELECT sh.created_at, sh.action, sh.quantity_before, sh.quantity_after, sh.change, 
                    sh.dispensed_to_student_id,
                    COALESCE(s.stud_fname || ' ' || s.stud_lname, '') AS stud_name,
                    sh.details
                FROM storage_history sh
                LEFT JOIN student s ON sh.dispensed_to_student_id = s.stud_id
                WHERE sh.invitem_id=%s
                ORDER BY sh.created_at DESC
            """, (invitem_id,))
            rows = cur.fetchall()
            cur.close()
            conn.close()
            # Center dialog over the main window (StoragePage)
            main_rect = self.geometry()
            global_center = self.mapToGlobal(main_rect.center())
            dialog = StorageHistoryDialog(rows, all_items=False, cell_center_pos=global_center)
            dialog.exec_()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to show history: {e}")

    def show_history_all(self):
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("""
                SELECT sh.created_at, sh.action, ii.invitem_name, sh.quantity_before, sh.quantity_after, sh.change, 
                       sh.dispensed_to_student_id,
                       COALESCE(s.stud_fname || ' ' || s.stud_lname, '') AS stud_name,
                       sh.details
                FROM storage_history sh
                LEFT JOIN inventory_item ii ON sh.invitem_id = ii.invitem_id
                LEFT JOIN student s ON sh.dispensed_to_student_id = s.stud_id
                ORDER BY sh.created_at DESC
            """)
            rows = cur.fetchall()
            cur.close()
            conn.close()
            # Center dialog over the main window
            main_rect = self.geometry()
            global_center = self.mapToGlobal(main_rect.center())
            dialog = StorageHistoryDialog(rows, all_items=True, cell_center_pos=global_center)
            dialog.exec_()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to show all history: {e}")

class DispenseDialog(QDialog):
    def __init__(self, max_qty, student_exists_func, parent=None):
        super().__init__(parent)
        self.student_exists_func = student_exists_func
        self.max_qty = max_qty
        self.setWindowTitle("Dispense Medicine")
        self.setFixedSize(500, 370)
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

        # --- Quantity Row with + and - buttons ---
        quantity_layout = QHBoxLayout()
        self.qty_edit = QLineEdit()
        self.qty_edit.setPlaceholderText(f"Enter quantity (Max: {max_qty})")
        self.qty_edit.setFixedHeight(50)

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

        quantity_layout.addWidget(self.qty_edit)
        quantity_layout.addWidget(btns_widget, alignment=Qt.AlignVCenter)

        # Connect signals
        self.plus_btn.clicked.connect(self.increment_quantity)
        self.minus_btn.clicked.connect(self.decrement_quantity)

        layout.addRow(QLabel("Quantity:"), quantity_layout)

        # --- Other Fields ---
        self.student_id_edit = QLineEdit()
        self.student_id_edit.setPlaceholderText("Student LRN/ID number")
        self.student_id_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self.date_edit = QDateEdit(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.date_edit.setStyleSheet("padding: 8px;")

        self.notes_edit = QLineEdit()
        self.notes_edit.setPlaceholderText("Dispense notes (optional)")
        self.notes_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        layout.addRow(QLabel("Student ID:"), self.student_id_edit)
        layout.addRow(QLabel("Date:"), self.date_edit)
        layout.addRow(QLabel("Notes:"), self.notes_edit)

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

    def increment_quantity(self):
        try:
            value = int(self.qty_edit.text()) if self.qty_edit.text() else 0
            value += 1
            if value > self.max_qty:
                value = self.max_qty
            self.qty_edit.setText(str(value))
        except ValueError:
            self.qty_edit.setText("1")

    def decrement_quantity(self):
        try:
            value = int(self.qty_edit.text()) if self.qty_edit.text() else 0
            value -= 1
            if value < 1:
                value = 1
            self.qty_edit.setText(str(value))
        except ValueError:
            self.qty_edit.setText("1")

    def validate_input(self):
        try:
            value = int(self.qty_edit.text())
            if value <= 0 or value > self.max_qty:
                raise ValueError
        except Exception:
            QMessageBox.warning(self, "Error", f"Please enter a valid quantity (1-{self.max_qty})")
            return
        student_id_text = self.student_id_edit.text().strip()
        if not student_id_text:
            QMessageBox.warning(self, "Error", "Please enter a student ID number")
            return
        if not self.student_exists_func(student_id_text):
            QMessageBox.warning(self, "Error", "Student ID not found in the database.")
            return
        self.accept()

    def get_data(self):
        return (
            int(self.qty_edit.text()),
            self.student_id_edit.text().strip(),
            self.date_edit.date().toString("yyyy-MM-dd"),
            self.notes_edit.text()
        )

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = StoragePage()
    window.setWindowTitle("Storage Inventory System")
    window.show()
    sys.exit(app.exec_())
