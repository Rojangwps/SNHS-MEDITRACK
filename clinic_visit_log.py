from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QPushButton,
    QMessageBox, QHBoxLayout, QLineEdit, QDialog, QFormLayout, QDateEdit, QTimeEdit, QFileDialog, QHeaderView
)
from PyQt5.QtCore import Qt, QDate, QTime
import psycopg2
import csv

def get_db_connection():
    return psycopg2.connect(
        host="localhost",
        database="MediTrackSNHS",
        user="postgres",
        password="Mylovemondejar"
    )

class ClinicVisitLog(QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("ClinicVisitLogBg")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        title = QLabel("Clinic Visit Log")
        title.setStyleSheet("""
            font-size: 28px;
            font-weight: bold;
            background: #FFE1D3;
            border-radius: 10px;
            padding: 10px;
            color: #3a2b23;
        """)
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Top controls
        control_layout = QHBoxLayout()
        self.search_box = QLineEdit()
        self.search_box.setFixedHeight(45)
        self.search_box.setFixedWidth(400)
        self.search_box.setStyleSheet("""
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
        self.search_box.setPlaceholderText("Search visit log...")
        self.search_box.textChanged.connect(self.search_table)

        self.add_btn = QPushButton("Add")
        self.add_btn.setFixedWidth(120)
        self.add_btn.setFixedHeight(45)
        self.add_btn.setStyleSheet("background-color: #D295BF; color: white; font-weight: bold; padding: 15px; border-radius: 10px; font-size: 18px;")
        
        self.edit_btn = QPushButton("Edit")
        self.edit_btn.setFixedWidth(120)
        self.edit_btn.setFixedHeight(45)
        self.edit_btn.setStyleSheet("background-color: #F7CA18; color: white; font-weight: bold; padding: 15px; border-radius: 10px; font-size: 18px;")
        
        self.export_btn = QPushButton("Export CSV")
        self.export_btn.setFixedWidth(160)
        self.export_btn.setFixedHeight(45)
        self.export_btn.setStyleSheet("background-color: #5DADE2; color: white; font-weight: bold; border-radius: 10px; font-size: 18px;")

        control_layout.addWidget(self.search_box)
        control_layout.addStretch()
        control_layout.addWidget(self.add_btn)
        control_layout.addWidget(self.edit_btn)
        control_layout.addWidget(self.export_btn)
        layout.addLayout(control_layout)

        self.add_btn.clicked.connect(self.add_record)
        self.edit_btn.clicked.connect(self.edit_record)
        self.export_btn.clicked.connect(self.export_csv)

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(
            ["Student ID", "Student Name", "Visit Date", "Reason", "Time In", "Time Out"]
        )
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #FFF5F0;
            }
            QTableWidget::item {
                font-size: 18px;
                font-weight: Bold;
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
        self.table.horizontalHeader().setStretchLastSection(True)
        header = self.table.horizontalHeader()
        for i in range(self.table.columnCount()):
            header.setSectionResizeMode(i, QHeaderView.Stretch)
        layout.addWidget(self.table)
        self.load_data()

        self.setStyleSheet("""
            QWidget#ClinicVisitLogBg {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #FED6C8, stop:1 #F9E6DC);
            }
        """)

    def load_data(self):
        self.table.setRowCount(0)
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("""
                SELECT v.stud_id, 
                       s.stud_lname || ', ' || s.stud_fname || 
                       CASE WHEN s.stud_mname IS NOT NULL AND s.stud_mname <> '' THEN ' ' || s.stud_mname ELSE '' END AS stud_fullname,
                       v.cvl_date, v.cvl_reason, v.cvl_time_in, v.cvl_time_out
                FROM clinic_visit_log v
                LEFT JOIN student s ON v.stud_id = s.stud_id
                ORDER BY v.cvl_date DESC
            """)
            self.rows = cur.fetchall()
            self.display_rows(self.rows)
            cur.close()
            conn.close()
        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"Error loading clinic visit log:\n{e}")

    def display_rows(self, rows):
        self.table.setRowCount(len(rows))
        for row_idx, row in enumerate(rows):
            for col_idx, val in enumerate(row):
                self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(val) if val is not None else ""))

    def search_table(self):
        query = self.search_box.text().lower()
        filtered = []
        for row in self.rows:
            if (query in str(row[0]).lower() or
                query in str(row[1]).lower() or
                query in str(row[2]).lower() or
                query in str(row[3]).lower() or
                query in str(row[4]).lower() or
                query in str(row[5]).lower()):
                filtered.append(row)
        self.display_rows(filtered)

    def add_record(self):
        dialog = AddClinicVisitDialog(self)
        if dialog.exec_():
            data = dialog.get_data()
            try:
                conn = get_db_connection()
                cur = conn.cursor()
                cur.execute(
                    "INSERT INTO clinic_visit_log (stud_id, cvl_date, cvl_reason, cvl_time_in, cvl_time_out) VALUES (%s, %s, %s, %s, %s)",
                    (data[0], data[2], data[3], data[4], data[5])
                )
                conn.commit()
                cur.close()
                conn.close()
                self.load_data()
            except Exception as e:
                QMessageBox.critical(self, "Database Error", f"Error adding record:\n{e}")

    def edit_record(self):
        selected = self.table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, "Edit Record", "Please select a row to edit.")
            return
        stud_id = self.table.item(selected, 0).text()
        stud_name = self.table.item(selected, 1).text()
        cvl_date = self.table.item(selected, 2).text()
        cvl_reason = self.table.item(selected, 3).text()
        cvl_time_in = self.table.item(selected, 4).text()
        cvl_time_out = self.table.item(selected, 5).text()

        def safe_get_time(val):
            t = QTime.fromString(str(val), "HH:mm:ss")
            if not t.isValid():
                t = QTime.fromString(str(val), "HH:mm")
            return t if t.isValid() else QTime.currentTime()

        record = (stud_id, stud_name, cvl_date, cvl_reason, cvl_time_in, cvl_time_out)
        dialog = EditClinicVisitDialog(self, record=record)
        dialog.cvl_time_in.setTime(safe_get_time(cvl_time_in))
        dialog.cvl_time_out.setTime(safe_get_time(cvl_time_out))
        if dialog.exec_():
            new_data = dialog.get_data()
            try:
                conn = get_db_connection()
                cur = conn.cursor()
                cur.execute(
                    "UPDATE clinic_visit_log SET stud_id=%s, cvl_date=%s, cvl_reason=%s, cvl_time_in=%s, cvl_time_out=%s WHERE stud_id=%s AND cvl_date=%s AND cvl_time_in=%s",
                    (new_data[0], new_data[2], new_data[3], new_data[4], new_data[5], stud_id, cvl_date, cvl_time_in)
                )
                conn.commit()
                cur.close()
                conn.close()
                self.load_data()
            except Exception as e:
                QMessageBox.critical(self, "Database Error", f"Error editing record:\n{e}")

    def export_csv(self):
        try:
            path, _ = QFileDialog.getSaveFileName(self, "Export CSV", "", "CSV Files (*.csv)")
            if not path:
                return
            with open(path, "w", newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(["Student ID", "Student Name", "Visit Date", "Reason", "Time In", "Time Out"])
                for row_idx in range(self.table.rowCount()):
                    rowdata = []
                    for col_idx in range(self.table.columnCount()):
                        item = self.table.item(row_idx, col_idx)
                        rowdata.append(item.text() if item else "")
                    writer.writerow(rowdata)
            QMessageBox.information(self, "Export CSV", f"Exported to {path}")
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Error exporting CSV:\n{e}")

class AddClinicVisitDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Clinic Visit")
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
            QLineEdit, QComboBox, QDateEdit, QTimeEdit {
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

        self.stud_name = QLineEdit()
        self.stud_name.setPlaceholderText("Enter Student Name (optional)")
        form_layout.addRow(QLabel("Student Name"), self.stud_name)

        self.cvl_date = QDateEdit(QDate.currentDate())
        self.cvl_date.setCalendarPopup(True)
        form_layout.addRow("Visit Date", self.cvl_date)

        self.cvl_reason = QLineEdit()
        self.cvl_reason.setPlaceholderText("Reason for visit")
        form_layout.addRow("Reason", self.cvl_reason)

        self.cvl_time_in = QTimeEdit(QTime.currentTime())
        self.cvl_time_in.setDisplayFormat("HH:mm")
        form_layout.addRow("Time In", self.cvl_time_in)

        self.cvl_time_out = QTimeEdit(QTime.currentTime())
        self.cvl_time_out.setDisplayFormat("HH:mm")
        form_layout.addRow("Time Out", self.cvl_time_out)

        layout.addLayout(form_layout)

        btn_row = QHBoxLayout()
        save_btn = QPushButton("Save Visit")
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

        self.data = None

    def save_and_accept(self):
        sid = self.stud_id.text().strip()
        name = self.stud_name.text().strip()
        date = self.cvl_date.date().toString("yyyy-MM-dd")
        reason = self.cvl_reason.text().strip()
        time_in = self.cvl_time_in.time().toString("HH:mm")
        time_out = self.cvl_time_out.time().toString("HH:mm")
        if not sid or not date or not reason or not time_in or not time_out:
            QMessageBox.warning(self, "Missing Information", "Please fill all required fields.")
            return
        self.data = (sid, name, date, reason, time_in, time_out)
        self.accept()

    def get_data(self):
        return self.data

class EditClinicVisitDialog(QDialog):
    def __init__(self, parent=None, record=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Clinic Visit")
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
            QLineEdit, QComboBox, QDateEdit, QTimeEdit {
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

        self.stud_name = QLineEdit()
        self.stud_name.setPlaceholderText("Enter Student Name (optional)")
        form_layout.addRow(QLabel("Student Name"), self.stud_name)

        self.cvl_date = QDateEdit()
        self.cvl_date.setCalendarPopup(True)
        form_layout.addRow("Visit Date", self.cvl_date)

        self.cvl_reason = QLineEdit()
        self.cvl_reason.setPlaceholderText("Reason for visit")
        form_layout.addRow("Reason", self.cvl_reason)

        self.cvl_time_in = QTimeEdit()
        self.cvl_time_in.setDisplayFormat("HH:mm")
        form_layout.addRow("Time In", self.cvl_time_in)

        self.cvl_time_out = QTimeEdit()
        self.cvl_time_out.setDisplayFormat("HH:mm")
        form_layout.addRow("Time Out", self.cvl_time_out)

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

        self.data = None

        if record:
            self.stud_id.setText(str(record[0]))
            self.stud_name.setText(str(record[1]))
            self.cvl_date.setDate(QDate.fromString(record[2], "yyyy-MM-dd"))
            self.cvl_reason.setText(str(record[3]))

            def safe_set_time(timeedit, value):
                t = QTime.fromString(str(value), "HH:mm:ss")
                if not t.isValid():
                    t = QTime.fromString(str(value), "HH:mm")
                if t.isValid():
                    timeedit.setTime(t)
                else:
                    timeedit.setTime(QTime.currentTime())
            safe_set_time(self.cvl_time_in, record[4])
            safe_set_time(self.cvl_time_out, record[5])

    def save_and_accept(self):
        sid = self.stud_id.text().strip()
        name = self.stud_name.text().strip()
        date = self.cvl_date.date().toString("yyyy-MM-dd")
        reason = self.cvl_reason.text().strip()
        time_in = self.cvl_time_in.time().toString("HH:mm")
        time_out = self.cvl_time_out.time().toString("HH:mm")
        if not sid or not date or not reason or not time_in or not time_out:
            QMessageBox.warning(self, "Missing Information", "Please fill all required fields.")
            return
        self.data = (sid, name, date, reason, time_in, time_out)
        self.accept()

    def get_data(self):
        return self.data
