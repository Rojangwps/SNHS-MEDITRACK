from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox, QDateEdit,
    QPushButton, QMessageBox, QFormLayout, QTableWidget, QHeaderView,
    QTableWidgetItem, QDialog
)
from PyQt5.QtCore import QDate, Qt
import psycopg2

def get_db_connection():
    return psycopg2.connect(
        host="localhost",
        database="MediTrackSNHS",
        user="postgres",
        password="Mylovemondejar"
    )

class MedicationPage(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 60)
        layout.setSpacing(16)

        title = QLabel("Medication Records")
        title.setStyleSheet("""
            font-size: 28px;
            font-weight: bold;
            background: #FDD1B0;
            border-radius: 10px;
            padding: 10px;
            color: #3a2b23;
        """)
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        search_row = QHBoxLayout()
        search_row.setSpacing(12)
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search medication records...")
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
        self.search_bar.textChanged.connect(self.search_table)

        add_btn = QPushButton("Add Medication")
        add_btn.setFixedWidth(180)
        add_btn.setStyleSheet("background-color: #D295BF; color: white; font-weight: bold; padding: 15px; border-radius: 10px; font-size: 18px;")
        add_btn.clicked.connect(self.add_medication_dialog)
        
        search_row.addWidget(self.search_bar)
        search_row.addStretch(1)
        search_row.addWidget(add_btn)
        layout.addLayout(search_row)

        self.table = QTableWidget()
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels([
            "Student ID", "Student Name", "Medication", "Dosage", "Frequency", "Start Date", "End Date", "Notes", "Actions"
        ])
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
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSortingEnabled(False)
        header = self.table.horizontalHeader()
        for i in range(self.table.columnCount()):
            header.setSectionResizeMode(i, QHeaderView.Stretch)
        layout.addWidget(self.table)
        self.setLayout(layout)
        self.load_data()

    def load_data(self):
        self.table.setRowCount(0)
        self.raw_rows = []
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("""
                SELECT m.med_id, m.stud_id, 
                       s.stud_lname || ', ' || s.stud_fname || 
                       CASE WHEN s.stud_mname IS NOT NULL AND s.stud_mname <> '' THEN ' ' || s.stud_mname ELSE '' END AS stud_fullname, 
                       m.med_name, m.med_dosage, m.med_frequency,
                       m.med_start_date, m.med_end_date, m.notes
                FROM medication m
                LEFT JOIN student s ON m.stud_id = s.stud_id
                ORDER BY m.med_start_date DESC
            """)
            rows = cur.fetchall()
            self.raw_rows = rows  # Save for searching
            self.display_rows(rows)
            cur.close()
            conn.close()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load medication data: {e}")

    def display_rows(self, rows):
        self.table.setRowCount(len(rows))
        for row_idx, row in enumerate(rows):
            self.table.setVerticalHeaderItem(row_idx, QTableWidgetItem(str(row_idx + 1)))
            for col_idx, val in enumerate(row[1:]):  # skip med_id
                self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(val) if val is not None else ""))
            # --- Action Buttons ---
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
            edit_btn.clicked.connect(lambda _, r=row: self.edit_medication_dialog(r))
            delete_btn.clicked.connect(lambda _, med_id=row[0]: self.delete_medication(med_id))
            btn_layout = QHBoxLayout()
            btn_layout.addWidget(edit_btn)
            btn_layout.addWidget(delete_btn)
            btn_layout.setContentsMargins(0,0,0,0)
            btn_layout.setSpacing(5)
            btn_widget = QWidget()
            btn_widget.setLayout(btn_layout)
            btn_widget.setStyleSheet("background-color: #FFF5F0; border-radius: 6px;")
            self.table.setCellWidget(row_idx, 8, btn_widget)

    def search_table(self):
        query = self.search_bar.text().lower()
        filtered = []
        for row in self.raw_rows:
            # row = (med_id, stud_id, stud_fullname, med_name, med_dosage, med_frequency, med_start_date, med_end_date, notes)
            if (query in str(row[1]).lower() or    # Student ID
                query in str(row[2]).lower() or    # Student Name
                query in str(row[3]).lower() or    # Medication Name
                query in str(row[4]).lower() or    # Dosage
                query in str(row[5]).lower() or    # Frequency
                query in str(row[6]).lower() or    # Start Date
                query in str(row[7]).lower() or    # End Date
                query in str(row[8]).lower()):     # Notes
                filtered.append(row)
        self.display_rows(filtered)

    def add_medication_dialog(self):
        dialog = AddMedicationDialog(self)
        if dialog.exec_():
            self.load_data()

    def edit_medication_dialog(self, row):
        dialog = EditMedicationDialog(self, row)
        if dialog.exec_():
            self.load_data()

    def delete_medication(self, med_id):
        confirm = QMessageBox.question(self, "Delete Medication", "Are you sure you want to delete this record?",
                                       QMessageBox.Yes | QMessageBox.No)
        if confirm == QMessageBox.Yes:
            try:
                conn = get_db_connection()
                cur = conn.cursor()
                cur.execute("DELETE FROM medication WHERE med_id=%s", (med_id,))
                conn.commit()
                cur.close()
                conn.close()
                self.load_data()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete medication: {e}")

class AddMedicationDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Medication")
        self.setMinimumWidth(550)
        self.setMinimumHeight(500)
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        self.setLayout(layout)
        self.setStyleSheet("""
            QDialog {
                background-color: #FFF5F0;
            }
            QLabel {
                font-size: 18px;
                font-weight: bold;
                padding: 5px;
                background-color: #FFF5F0;
            }
            QLineEdit, QComboBox, QDateEdit {
                font-size: 18px;
                padding: 10px;
                border: 2px solid #D295BF;
                border-radius: 8px;
                min-height: 30px;
                background-color: #FFFFFF;
            }
            QPushButton {
                font-size: 16px;
                padding: 8px 16px;
            }
        """)

        form_layout = QFormLayout()
        form_layout.setLabelAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        form_layout.setFormAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        form_layout.setSpacing(16)

        self.stud_id = QLineEdit()
        self.stud_id.setPlaceholderText("Enter Student LRN/ID")
        form_layout.addRow("Student ID", self.stud_id)

        self.med_name = QLineEdit()
        self.med_name.setPlaceholderText("e.g. Paracetamol")
        form_layout.addRow("Medication Name", self.med_name)

        self.med_dosage = QLineEdit()
        self.med_dosage.setPlaceholderText("e.g. 500mg, 5ml")
        form_layout.addRow("Dosage", self.med_dosage)

        self.med_frequency = QComboBox()
        self.med_frequency.addItems(["Select frequency...", "Once a day", "Twice a day", "Thrice a day", "As needed"])
        form_layout.addRow("Frequency", self.med_frequency)

        self.med_start_date = QDateEdit(QDate.currentDate())
        self.med_start_date.setCalendarPopup(True)
        form_layout.addRow("Start Date", self.med_start_date)

        self.med_end_date = QDateEdit(QDate.currentDate())
        self.med_end_date.setCalendarPopup(True)
        form_layout.addRow("End Date", self.med_end_date)

        self.notes = QLineEdit()
        self.notes.setPlaceholderText("Any notes (optional)")
        self.notes.setFixedHeight(50)
        form_layout.addRow("Notes", self.notes)

        layout.addLayout(form_layout)

        btn_row = QHBoxLayout()
        save_btn = QPushButton("Save Medication")
        save_btn.setStyleSheet("""
            QPushButton {
                background:#BA74AD; color:white; font-size: 17px; font-weight:bold;
                padding: 10px 26px; border-radius: 10px; min-width:160px;
            }
            QPushButton:hover { background: #d295bf; }
        """)
        save_btn.clicked.connect(self.save_and_accept)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background:#b0b0b0; color:white; font-size: 17px;
                padding: 10px 26px; border-radius: 10px; min-width:120px;
            }
            QPushButton:hover { background: #888;}
        """)
        cancel_btn.clicked.connect(self.reject)
        btn_row.addWidget(save_btn)
        btn_row.addWidget(cancel_btn)
        layout.addLayout(btn_row)

    def save_and_accept(self):
        sid = self.stud_id.text().strip()
        name = self.med_name.text().strip()
        dosage = self.med_dosage.text().strip()
        freq = self.med_frequency.currentText()
        sdate = self.med_start_date.date().toString("yyyy-MM-dd")
        edate = self.med_end_date.date().toString("yyyy-MM-dd")
        notes = self.notes.text().strip()

        if not sid or not name or not dosage or self.med_frequency.currentIndex() == 0:
            QMessageBox.warning(self, "Missing Information", "Please fill all required fields.")
            return
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO medication (stud_id, med_name, med_dosage, med_frequency, med_start_date, med_end_date, notes)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (sid, name, dosage, freq, sdate, edate, notes))
            conn.commit()
            cur.close()
            conn.close()
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"Could not save medication: {e}")

class EditMedicationDialog(QDialog):
    def __init__(self, parent=None, row=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Medication")
        self.setMinimumWidth(550)
        self.setMinimumHeight(500)
        self.med_id = row[0] if row else None
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        self.setLayout(layout)
        self.setStyleSheet("""
            QDialog {
                background-color: #FFF5F0;
            }
            QLabel {
                font-size: 18px;
                font-weight: bold;
                padding: 5px;
                background-color: #FFF5F0;
            }
            QLineEdit, QComboBox, QDateEdit {
                font-size: 18px;
                padding: 10px;
                border: 2px solid #D295BF;
                border-radius: 8px;
                min-height: 30px;
                background-color: #FFFFFF;
            }
            QPushButton {
                font-size: 16px;
                padding: 8px 16px;
            }
        """)

        form_layout = QFormLayout()
        form_layout.setLabelAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        form_layout.setFormAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        form_layout.setSpacing(16)

        self.stud_id = QLineEdit()
        self.stud_id.setPlaceholderText("Enter Student LRN/ID")
        form_layout.addRow("Student ID", self.stud_id)

        self.med_name = QLineEdit()
        self.med_name.setPlaceholderText("e.g. Paracetamol")
        form_layout.addRow("Medication Name", self.med_name)

        self.med_dosage = QLineEdit()
        self.med_dosage.setPlaceholderText("e.g. 500mg, 5ml")
        form_layout.addRow("Dosage", self.med_dosage)

        self.med_frequency = QComboBox()
        self.med_frequency.addItems(["Select frequency...", "Once a day", "Twice a day", "Thrice a day", "As needed"])
        form_layout.addRow("Frequency", self.med_frequency)

        self.med_start_date = QDateEdit(QDate.currentDate())
        self.med_start_date.setCalendarPopup(True)
        form_layout.addRow("Start Date", self.med_start_date)

        self.med_end_date = QDateEdit(QDate.currentDate())
        self.med_end_date.setCalendarPopup(True)
        form_layout.addRow("End Date", self.med_end_date)

        self.notes = QLineEdit()
        self.notes.setPlaceholderText("Any notes (optional)")
        form_layout.addRow("Notes", self.notes)

        layout.addLayout(form_layout)

        btn_row = QHBoxLayout()
        save_btn = QPushButton("Save Changes")
        save_btn.setStyleSheet("""
            QPushButton {
                background:#BA74AD; color:white; font-size: 17px; font-weight:bold;
                padding: 10px 26px; border-radius: 10px; min-width:160px;
            }
            QPushButton:hover { background: #d295bf; }
        """)
        save_btn.clicked.connect(self.save_and_accept)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background:#b0b0b0; color:white; font-size: 17px;
                padding: 10px 26px; border-radius: 10px; min-width:120px;
            }
            QPushButton:hover { background: #888;}
        """)
        cancel_btn.clicked.connect(self.reject)
        btn_row.addWidget(save_btn)
        btn_row.addWidget(cancel_btn)
        layout.addLayout(btn_row)

        if row:
            self.stud_id.setText(str(row[1]))
            self.med_name.setText(str(row[3]))
            self.med_dosage.setText(str(row[4]))
            ix = self.med_frequency.findText(str(row[5]))
            self.med_frequency.setCurrentIndex(ix if ix > 0 else 0)
            if row[6] and str(row[6]) != "None":
                self.med_start_date.setDate(QDate.fromString(str(row[6]), "yyyy-MM-dd"))
            if row[7] and str(row[7]) != "None":
                self.med_end_date.setDate(QDate.fromString(str(row[7]), "yyyy-MM-dd"))
            self.notes.setText(str(row[8]))

    def save_and_accept(self):
        sid = self.stud_id.text().strip()
        name = self.med_name.text().strip()
        dosage = self.med_dosage.text().strip()
        freq = self.med_frequency.currentText()
        sdate = self.med_start_date.date().toString("yyyy-MM-dd")
        edate = self.med_end_date.date().toString("yyyy-MM-dd")
        notes = self.notes.text().strip()

        if not sid or not name or not dosage or self.med_frequency.currentIndex() == 0:
            QMessageBox.warning(self, "Missing Information", "Please fill all required fields.")
            return
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("""
                UPDATE medication
                SET stud_id=%s, med_name=%s, med_dosage=%s, med_frequency=%s,
                    med_start_date=%s, med_end_date=%s, notes=%s, updated_at=NOW()
                WHERE med_id=%s
            """, (sid, name, dosage, freq, sdate, edate, notes, self.med_id))
            conn.commit()
            cur.close()
            conn.close()
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"Could not save medication: {e}")
