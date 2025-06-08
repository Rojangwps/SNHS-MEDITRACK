from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem
import psycopg2

def get_db_connection():
    return psycopg2.connect(
        host="localhost",
        database="SAMPLE",
        user="postgres",
        password="123"
    )

class ClinicVisitLog(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Clinic Visit Log"))
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Student ID", "Visit Date", "Reason", "Time In", "Time Out"])
        layout.addWidget(self.table)
        self.load_data()

    def load_data(self):
        self.table.setRowCount(0)
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("SELECT stud_id, visit_date, reason, time_in, time_out FROM clinic_visit_log ORDER BY visit_date DESC")
            rows = cur.fetchall()
            self.table.setRowCount(len(rows))
            for row_idx, row in enumerate(rows):
                for col_idx, val in enumerate(row):
                    self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(val) if val else ""))
            cur.close()
            conn.close()
        except Exception as e:
            print("Error loading clinic visit log:", e)
