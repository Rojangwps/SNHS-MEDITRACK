import psycopg2
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QHBoxLayout, QPushButton, QLineEdit,
    QTableWidget, QTableWidgetItem, QMessageBox, QDialog, QFormLayout,
    QDialogButtonBox, QHeaderView, QComboBox, QDateEdit, QSizePolicy,
    QStyledItemDelegate
)
from PyQt5.QtCore import Qt, QDate
import sys

def get_db_connection():
    return psycopg2.connect(
        host="localhost",
        database="SAMPLE",
        user="postgres",
        password="123"
    )

class StorageFormDialog(QDialog):
    def __init__(self, mode="Add", item=None, save_callback=None):
        super().__init__()
        self.setWindowTitle(f"{mode} Storage Item")
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
            QFormLayout > QLabel {
                font-size: 20px;
                background: transparent;
            }
            QLineEdit, QComboBox, QDateEdit {
                font-size: 18px;
                background: #fff6f0;
                border: 2px solid #d295bf;
                border-radius: 6px;
                padding: 10px;
                min-height: 36px;
            }
            QPushButton {
                font-size: 20px;
                padding: 12px 38px;
                border-radius: 8px;
            }
            QPushButton#SaveBtn {
                background-color: #d295bf;
                color: white;
            }
            QPushButton#BackBtn {
                background-color: #ffe599;
                color: #333;
            }
        """)
        self.setMinimumSize(800, 650)
        self.save_callback = save_callback

        vbox = QVBoxLayout(self)
        vbox.setContentsMargins(40, 40, 40, 40)
        vbox.setSpacing(15)

        header = QLabel(f"{mode} Storage Item")
        header.setObjectName("Header")
        header.setAlignment(Qt.AlignCenter)
        vbox.addWidget(header)

        form = QFormLayout()
        form.setSpacing(18)

        self.name_edit = QLineEdit(item['name'] if item else "")
        self.name_edit.setPlaceholderText("Item Name (e.g., Paracetamol)")
        form.addRow("Name*", self.name_edit)

        self.quantity_edit = QLineEdit(str(item['quantity']) if item else "")
        self.quantity_edit.setPlaceholderText("Quantity (e.g., 10)")
        form.addRow("Quantity*", self.quantity_edit)

        self.dosage_edit = QLineEdit(item['dosage'] if item else "")
        self.dosage_edit.setPlaceholderText("Dosage (e.g., 500mg, 60ml)")
        form.addRow("Dosage", self.dosage_edit)

        self.unit_edit = QLineEdit(item['unit'] if item else "")
        self.unit_edit.setPlaceholderText("Unit (e.g., Tablet, Capsule, ml)")
        form.addRow("Unit*", self.unit_edit)

        self.expiry_edit = QDateEdit()
        self.expiry_edit.setCalendarPopup(True)
        self.expiry_edit.setDate(
            QDate.fromString(item['expiry'], "yyyy-MM-dd") if item and item['expiry'] else QDate.currentDate().addYears(1)
        )
        form.addRow("Expiry Date", self.expiry_edit)

        self.status_combo = QComboBox()
        self.status_combo.addItems(["Available", "Not Available"])
        if item and item['status']:
            idx = self.status_combo.findText(item['status'])
            if idx >= 0:
                self.status_combo.setCurrentIndex(idx)
        form.addRow("Status*", self.status_combo)

        vbox.addLayout(form)
        vbox.addStretch(1)

        # Bottom Button Bar
        btns = QHBoxLayout()
        btns.addStretch(1)
        back_btn = QPushButton("Back")
        back_btn.setObjectName("BackBtn")
        back_btn.clicked.connect(self.reject)
        btns.addWidget(back_btn)
        save_btn = QPushButton("Save" if mode == "Add" else "Update")
        save_btn.setObjectName("SaveBtn")
        save_btn.clicked.connect(self.handle_save)
        btns.addWidget(save_btn)
        vbox.addLayout(btns)

    def handle_save(self):
        # Basic validation
        if not self.name_edit.text().strip():
            QMessageBox.warning(self, "Error", "Please enter an item name.")
            return
        if not self.quantity_edit.text().strip():
            QMessageBox.warning(self, "Error", "Please enter a quantity.")
            return
        try:
            float(self.quantity_edit.text())
        except ValueError:
            QMessageBox.warning(self, "Error", "Quantity must be a number.")
            return
        if not self.unit_edit.text().strip():
            QMessageBox.warning(self, "Error", "Please enter a unit.")
            return

        item = {
            'name': self.name_edit.text().strip(),
            'quantity': self.quantity_edit.text().strip(),
            'dosage': self.dosage_edit.text().strip(),
            'unit': self.unit_edit.text().strip(),
            'expiry': self.expiry_edit.date().toString("yyyy-MM-dd"),
            'status': self.status_combo.currentText()
        }
        if self.save_callback:
            self.save_callback(item)
        self.accept()

class StorageHistoryDialog(QDialog):
    def __init__(self, history_rows):
        super().__init__()
        self.setWindowTitle("Storage Item History")
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
        self.setMinimumSize(1100, 500)
        vbox = QVBoxLayout(self)
        vbox.setContentsMargins(36, 36, 36, 36)

        header = QLabel("Storage Item History")
        header.setObjectName("Header")
        header.setAlignment(Qt.AlignCenter)
        vbox.addWidget(header)

        table = QTableWidget()
        table.setColumnCount(8)
        table.setHorizontalHeaderLabels([
            "Date", "Action", "Qty Before", "Qty After", "Change", "Student ID", "Student Name", "Details"
        ])
        table.setRowCount(len(history_rows))
        for i, row in enumerate(history_rows):
            for j, value in enumerate(row):
                table.setItem(i, j, QTableWidgetItem(str(value) if value is not None else ""))
        vbox.addWidget(table)

        # Bottom bar with back button
        btns = QHBoxLayout()
        btns.addStretch(1)
        back_btn = QPushButton("Back")
        back_btn.setObjectName("BackBtn")
        back_btn.clicked.connect(self.reject)
        btns.addWidget(back_btn)
        vbox.addLayout(btns)

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

        history_btn = QPushButton("View Storage History")
        history_btn.setFixedWidth(200)
        history_btn.setStyleSheet("background-color: #a3d5ff; color: #333; padding: 13px 20px; font-size: 16px;")
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
        def save_callback(new_item):
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
                self.log_storage_history(new_item['id'], "added", 0, int(new_item['quantity']), int(new_item['quantity']), None, None, "New item added")
                conn.commit()
                cur.close()
                conn.close()
                self.load_items_from_db()
            except Exception as e:
                QMessageBox.critical(self, "Database Error", f"Failed to add item: {e}")
        dialog = StorageFormDialog(mode="Add", save_callback=save_callback)
        dialog.exec_()

    def edit_item(self, row):
        item = self.items[row]
        def save_callback(updated_item):
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
        dialog = StorageFormDialog(mode="Edit", item=item, save_callback=save_callback)
        dialog.exec_()

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
            self.table.setCellWidget(idx, 6, btn_widget)

            history_btn = QPushButton("History")
            history_btn.setStyleSheet("""
                QPushButton {
                    background-color: #ffe599;
                    padding: 5px;
                    font-size: 16px;
                    border-radius: 5px;
                }
                QPushButton:hover {
                    background-color: #eedd82;
                }
            """)
            history_btn.clicked.connect(lambda _, invitem_id=item['id']: self.show_history(invitem_id))
            self.table.setCellWidget(idx, 7, history_btn)

    def search_items(self):
        query = self.search_bar.text().lower()
        for row in range(self.table.rowCount()):
            item_name = self.table.item(row, 0).text().lower()
            is_visible = query in item_name
            self.table.setRowHidden(row, not is_visible)

    def show_history(self, invitem_id):
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
            dialog = StorageHistoryDialog(rows)
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
            # Show as a dialog (add item name column)
            # Reuse dialog or make a new one with an extra column as needed
            class AllHistoryDialog(StorageHistoryDialog):
                def __init__(self, all_rows):
                    super().__init__([])
                    self.setWindowTitle("Storage History (All Items)")
                    self.layout().removeWidget(self.layout().itemAt(1).widget())
                    table = QTableWidget()
                    table.setColumnCount(9)
                    table.setHorizontalHeaderLabels([
                        "Date", "Action", "Item", "Qty Before", "Qty After", "Change", "Student ID", "Student Name", "Details"
                    ])
                    table.setRowCount(len(all_rows))
                    for i, row in enumerate(all_rows):
                        for j, value in enumerate(row):
                            table.setItem(i, j, QTableWidgetItem(str(value) if value is not None else ""))
                    self.layout().insertWidget(1, table)
            dialog = AllHistoryDialog(rows)
            dialog.exec_()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to show all history: {e}")

class DispenseDialog(QDialog):
    def __init__(self, max_qty, student_exists_func, parent=None):
        super().__init__(parent)
        self.student_exists_func = student_exists_func
        self.setWindowTitle("Dispense Medicine")
        layout = QFormLayout(self)
        self.qty_edit = QLineEdit()
        self.qty_edit.setPlaceholderText(f"Max: {max_qty}")
        self.student_id_edit = QLineEdit()
        self.student_id_edit.setPlaceholderText("Student LRN/ID number")
        self.date_edit = QDateEdit(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)
        self.notes_edit = QLineEdit()
        layout.addRow("Quantity:", self.qty_edit)
        layout.addRow("Student ID:", self.student_id_edit)
        layout.addRow("Date:", self.date_edit)
        layout.addRow("Notes:", self.notes_edit)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.validate_input)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

    def validate_input(self):
        try:
            value = int(self.qty_edit.text())
            if value <= 0:
                raise ValueError
        except Exception:
            QMessageBox.warning(self, "Error", "Please enter a valid quantity")
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
