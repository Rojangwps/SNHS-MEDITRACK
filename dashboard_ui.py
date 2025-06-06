from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QStackedWidget,
    QFrame, QLabel
)
from PyQt5.QtCore import Qt

import psycopg2
from grade_section import GradeSectionPage
from patients import PatientsPage
from reports import ReportsPage
from storage import StoragePage
from medication import MedicationPage  # <--- ADD THIS IMPORT

class DashboardUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Clinic Patient's Dashboard")
        self.setStyleSheet("background-color: #FFE3D2;")
        self.init_ui()
        self.showFullScreen()

    def init_ui(self):
        main_layout = QHBoxLayout(self)

        # Sidebar
        sidebar = QFrame()
        sidebar.setStyleSheet("background-color: #FDD1B0;")
        sidebar.setFixedWidth(250)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setAlignment(Qt.AlignTop)
        sidebar_layout.setSpacing(20)

        logo_label = QLabel("LOGO HERE")
        logo_label.setAlignment(Qt.AlignCenter)
        logo_label.setStyleSheet(
            "border: 2px dashed #AAAAAA; font-size: 18px; color: #888888; padding: 60px;")
        sidebar_layout.addWidget(logo_label)

        # Database connection for reports page
        conn = psycopg2.connect(
            host="localhost",
            database="SAMPLE",
            user="postgres",
            password="123"
        )

        # Page Stack
        self.pages = QStackedWidget()

        self.dashboard_page = GradeSectionPage()
        self.patients_page = PatientsPage()
        self.reports_page = ReportsPage(conn)
        self.storage_page = StoragePage()
        self.medication_page = MedicationPage()  # <--- ADD THIS

        self.pages.addWidget(self.dashboard_page)   # index 0
        self.pages.addWidget(self.patients_page)    # index 1
        self.pages.addWidget(self.reports_page)     # index 2
        self.pages.addWidget(self.storage_page)     # index 3
        self.pages.addWidget(self.medication_page)  # index 4

        menu_items = [
            ("Dashboard", self.dashboard_page),
            ("Patients", self.patients_page),
            ("Generate Reports", self.reports_page),
            ("Storage", self.storage_page),
            ("Medication", self.medication_page),    # <--- ADD THIS
        ]

        for i, (text, _) in enumerate(menu_items):
            button = QPushButton(text)
            button.setStyleSheet("""
                QPushButton {
                    background-color: #D295BF;
                    border: none;
                    color: white;
                    font-size: 18px;
                    padding: 15px;
                    border-radius: 10px;
                    text-align: left;
                }
                QPushButton:hover {
                    background-color: #BA74AD;
                }
            """)
            sidebar_layout.addWidget(button)
            button.clicked.connect(lambda _, idx=i: self.pages.setCurrentIndex(idx))

        main_layout.addWidget(sidebar)
        main_layout.addWidget(self.pages)
