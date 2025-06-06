import psycopg2
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QTextEdit, QDateEdit, QMessageBox
)
from PyQt5.QtCore import QDate

class ReportsPage(QWidget):
    def __init__(self, conn):
        super().__init__()
        self.conn = conn
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        header = QLabel("Accident/Incident Report")
        header.setStyleSheet("font-size: 28px; font-weight: bold;")
        layout.addWidget(header)

        # Student ID
        row_sid = QHBoxLayout()
        row_sid.addWidget(QLabel("Student LRN:"))
        self.input_sid = QLineEdit()
        self.input_sid.setPlaceholderText("Enter Student LRN")
        row_sid.addWidget(self.input_sid)
        layout.addLayout(row_sid)

        # Date of Incident
        row_date = QHBoxLayout()
        row_date.addWidget(QLabel("Date of Incident:"))
        self.input_date = QDateEdit()
        self.input_date.setCalendarPopup(True)
        self.input_date.setDate(QDate.currentDate())
        row_date.addWidget(self.input_date)
        layout.addLayout(row_date)

        # Description
        layout.addWidget(QLabel("Description:"))
        self.input_desc = QTextEdit()
        self.input_desc.setPlaceholderText("Describe the accident/incident")
        layout.addWidget(self.input_desc)

        # Action Taken
        layout.addWidget(QLabel("Action Taken:"))
        self.input_action = QTextEdit()
        self.input_action.setPlaceholderText("Describe the action taken")
        layout.addWidget(self.input_action)

        # Referral
        row_ref = QHBoxLayout()
        row_ref.addWidget(QLabel("Referral:"))
        self.input_ref = QLineEdit()
        self.input_ref.setPlaceholderText("Enter referral (if any)")
        row_ref.addWidget(self.input_ref)
        layout.addLayout(row_ref)

        # Follow Up Date
        row_follow = QHBoxLayout()
        row_follow.addWidget(QLabel("Follow-up Date:"))
        self.input_followup = QDateEdit()
        self.input_followup.setCalendarPopup(True)
        self.input_followup.setDate(QDate.currentDate())
        row_follow.addWidget(self.input_followup)
        layout.addLayout(row_follow)

        # Submit Button
        self.btn_submit = QPushButton("Submit Report")
        self.btn_submit.clicked.connect(self.submit_report)
        layout.addWidget(self.btn_submit)

    def submit_report(self):
        try:
            lrn = self.input_sid.text().strip()
            date_incident = self.input_date.date().toString("yyyy-MM-dd")
            desc = self.input_desc.toPlainText().strip()
            action = self.input_action.toPlainText().strip()
            referral = self.input_ref.text().strip()
            followup_date = self.input_followup.date().toString("yyyy-MM-dd")

            if not lrn.isdigit():
                QMessageBox.warning(self, "Input Error", "Student LRN must be numeric.")
                return
            if not desc:
                QMessageBox.warning(self, "Input Error", "Description is required.")
                return

            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT INTO incident_report (
                    stud_id, ir_date_incident, ir_description, ir_action_taken,
                    ir_referral, ir_follow_up_date, created_at, updated_at
                ) VALUES (%s, %s, %s, %s, %s, %s, NOW(), NOW())
            """, (int(lrn), date_incident, desc, action, referral, followup_date))
            self.conn.commit()
            cursor.close()
            QMessageBox.information(self, "Success", "Incident report submitted.")
            self.clear_form()
        except Exception as e:
            self.conn.rollback()
            QMessageBox.critical(self, "Database Error", f"Error submitting report:\n{e}")

    def clear_form(self):
        self.input_sid.clear()
        self.input_date.setDate(QDate.currentDate())
        self.input_desc.clear()
        self.input_action.clear()
        self.input_ref.clear()
        self.input_followup.setDate(QDate.currentDate())