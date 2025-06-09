from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QStackedWidget,
    QFrame, QLabel, QTableWidget, QTableWidgetItem, QMessageBox, QHeaderView,
    QLineEdit, QDialog, QFormLayout, QComboBox, QSizePolicy
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPixmap
import psycopg2
import datetime

# Import your custom pages
from grade_section import GradeSectionPage
from patients import PatientsPage
from reports import ReportsPage
from storage import StoragePage
from medication import MedicationPage
from referral import ReferralPage
from clinic_visit_log import ClinicVisitLog

class AddHotlineDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Emergency Hotline")
        self.setMinimumWidth(400)
        layout = QVBoxLayout(self)
        form = QFormLayout()
        self.agency = QLineEdit()
        self.contact = QLineEdit()
        self.type = QComboBox()
        self.type.addItems(["Police", "Fire", "Ambulance", "Other"])
        form.addRow("Agency Name", self.agency)
        form.addRow("Contact Number", self.contact)
        form.addRow("Type", self.type)
        layout.addLayout(form)
        btn_row = QHBoxLayout()
        add_btn = QPushButton("Add")
        add_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        btn_row.addWidget(add_btn)
        btn_row.addWidget(cancel_btn)
        layout.addLayout(btn_row)

    def get_data(self):
        return (
            self.agency.text().strip(),
            self.contact.text().strip(),
            self.type.currentText()
        )

class HomeDashboardPage(QWidget):
    def __init__(self, conn):
        super().__init__()
        self.conn = conn
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)

        # --- Quick Stats / KPIs ---
        self.stats_row = QHBoxLayout()
        self.stat_cards = []
        for title in ["Total Students", "Visits Today", "Medications Dispensed Today", "Pending Referrals"]:
            card = self._stat_card(title, "--")
            self.stats_row.addWidget(card)
            self.stat_cards.append(card)
        layout.addLayout(self.stats_row)

        # --- Alerts & Reminders ---
        alert_block = QVBoxLayout()
        alert_title = QLabel("⚠️ Alerts & Reminders")
        alert_title.setStyleSheet("font-size:20px;font-weight:bold;color:#b43d16;")
        alert_block.addWidget(alert_title)
        self.alerts_label = QLabel("Loading alerts...")
        self.alerts_label.setWordWrap(True)
        self.alerts_label.setStyleSheet("margin-top:10px;font-size:15px;")
        alert_block.addWidget(self.alerts_label)
        alert_frame = QFrame()
        alert_frame.setStyleSheet("background:#FFE1D3;border-radius:18px;padding:18px;")
        alert_frame.setLayout(alert_block)

        # --- Emergency Hotlines ---
        hotline_block = QVBoxLayout()
        hotline_title = QLabel("🚨 Emergency Hotlines")
        hotline_title.setStyleSheet("font-size:20px;font-weight:bold;color:#10562E;")
        hotline_block.addWidget(hotline_title)
        self.hotline_label = QLabel("Loading emergency hotlines...")
        self.hotline_label.setWordWrap(True)
        self.hotline_label.setStyleSheet("margin-top:10px;font-size:15px;")
        hotline_block.addWidget(self.hotline_label)
        self.add_hotline_btn = QPushButton("Add Hotline")
        self.add_hotline_btn.setStyleSheet(
            "background:#D295BF; color:white; font-weight:bold; font-size:15px; padding:8px 18px; border-radius:10px; margin-top:8px;"
        )
        self.add_hotline_btn.clicked.connect(self.add_hotline)
        hotline_block.addWidget(self.add_hotline_btn, alignment=Qt.AlignRight)
        hotline_frame = QFrame()
        hotline_frame.setStyleSheet("background:#E6F2FF;border-radius:18px;padding:18px;")
        hotline_frame.setLayout(hotline_block)

        # --- Recent Activity Feed ---
        feed_title = QLabel("⏰ Recent Activity")
        feed_title.setStyleSheet("font-size:20px;font-weight:bold;")
        self.feed_label = QLabel("Loading activity...")
        self.feed_label.setWordWrap(True)
        self.feed_label.setStyleSheet("margin-top:10px;font-size:15px;")
        feed_frame = QFrame()
        feed_frame.setLayout(QVBoxLayout())
        feed_frame.layout().addWidget(feed_title)
        feed_frame.layout().addWidget(self.feed_label)
        feed_frame.setStyleSheet("background:#FFF9E6;border-radius:18px;padding:18px;")

        mid_row = QHBoxLayout()
        mid_row.addWidget(alert_frame, 2)
        mid_row.addWidget(hotline_frame, 3)
        mid_row.addWidget(feed_frame, 3)
        layout.addLayout(mid_row)

        # --- Quick Actions ---
        action_row = QHBoxLayout()
        for text, cb in [
            ("Open Patients", self.goto_patients),
            ("Add Clinic Visit", self.goto_clinic_visit),
            ("Dispense Medication", self.goto_medication),
            ("Generate Report", self.goto_reports),
        ]:
            b = QPushButton(text)
            b.setStyleSheet("""
                QPushButton {
                    background:#D295BF;
                    color:white;
                    font-weight:bold;
                    font-size:18px;
                    padding:15px 28px;
                    border-radius:12px;
                    margin-right:12px;
                }
                QPushButton:hover { background:#BA74AD; }
            """)
            b.clicked.connect(cb)
            action_row.addWidget(b)
        action_row.addStretch()
        layout.addLayout(action_row)

        # --- Recent Clinic Visits Card (Header fully visible & readable) ---
        visits_card = QFrame()
        visits_card.setStyleSheet("""
            QFrame {
                background: #FFF8F4;
                border-radius: 8px;
                border: 2px solid #E4BAB2;
                margin-top: 12px;
                margin-bottom: 12px;
                padding: 0px;
            }
        """)
        visits_layout = QVBoxLayout(visits_card)
        visits_layout.setContentsMargins(16, 16, 16, 16)
        visits_layout.setSpacing(0)

        # Add a big bold header above the table
        visits_header = QLabel("📝 Recent Clinic Visits")
        visits_header.setStyleSheet("font-size: 25px; font-weight: bold; color: #B43D16; margin-bottom: 10px;")
        visits_header.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        visits_layout.addWidget(visits_header)

        headers = [
            "Student ID", "Student Name", "Visit Date", "Reason", "Time In", "Time Out"
        ]
        self.visits_table = QTableWidget(0, 6)
        self.visits_table.setHorizontalHeaderLabels(headers)
        self.visits_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.visits_table.setMinimumHeight(300)
        self.visits_table.setAlternatingRowColors(True)
        self.visits_table.setShowGrid(True)
        self.visits_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.visits_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.visits_table.setSelectionMode(QTableWidget.SingleSelection)
        self.visits_table.verticalHeader().setVisible(True)
        self.visits_table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.visits_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.visits_table.verticalHeader().setDefaultAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.visits_table.verticalHeader().setFixedWidth(38)

        # Table header style: let Qt auto-size height, use padding and font.
        self.visits_table.horizontalHeader().setStyleSheet("""
        QHeaderView::section {
            background-color: #F9D2C8;
            color: #3C2121;
            font-size: 18px;
            font-weight: bold;
            border: 1px solid #E4BAB2;
            border-bottom: 2px solid #E4BAB2;
            border-right: 1px solid #E4BAB2;
            text-align: center;
            padding-top: 10px;
            padding-bottom: 10px;
        }
        """)
        # Fix: Only set minimum section size, not fixed height, to avoid collapsed headers
        header = self.visits_table.horizontalHeader()
        header.setMinimumSectionSize(44)
        header.setDefaultAlignment(Qt.AlignCenter)
        font = header.font()
        font.setPointSize(16)
        font.setBold(True)
        header.setFont(font)

        self.visits_table.verticalHeader().setStyleSheet("""
        QHeaderView::section {
            background-color: #F9D2C8;
            color: #3C2121;
            font-size: 15px;
            font-weight: bold;
            border: 1px solid #E4BAB2;
            text-align: center;
            padding: 2px;
        }
        """)

        visits_layout.addWidget(self.visits_table)
        layout.addWidget(visits_card, stretch=2)

        self.setLayout(layout)
        self.refresh_dashboard()

    def _stat_card(self, title, value):
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {background:#FED6C8;border-radius:18px;}
            QLabel {font-size:19px;}
        """)
        lay = QVBoxLayout(frame)
        lay.setAlignment(Qt.AlignCenter)
        label1 = QLabel(title)
        label1.setStyleSheet("font-size:17px;font-weight:bold;")
        label2 = QLabel(str(value))
        label2.setStyleSheet("font-size:38px;font-weight:bold;color:#BA74AD;")
        lay.addWidget(label1)
        lay.addWidget(label2)
        frame.value_label = label2
        frame.setFixedHeight(88)
        return frame

    def refresh_dashboard(self):
        try:
            cur = self.conn.cursor()

            # Quick Stats
            cur.execute("SELECT COUNT(*) FROM student")
            total_students = cur.fetchone()[0]
            cur.execute("SELECT COUNT(*) FROM clinic_visit_log WHERE cvl_date = %s", (datetime.date.today(),))
            visits_today = cur.fetchone()[0]
            cur.execute("SELECT COUNT(*) FROM medication WHERE med_start_date = %s", (datetime.date.today(),))
            meds_disp_today = cur.fetchone()[0]
            cur.execute("SELECT COUNT(*) FROM referral WHERE referral_status = 'Pending'")
            pending_ref = cur.fetchone()[0]
            for val, frame in zip([total_students, visits_today, meds_disp_today, pending_ref], self.stat_cards):
                frame.value_label.setText(str(val))

            # Alerts & Reminders
            alerts = []
            cur.execute("SELECT invitem_name, invitem_quantity FROM inventory_item WHERE invitem_quantity <= 5")
            for name, qty in cur.fetchall():
                alerts.append(f"Low inventory: <b>{name}</b> ({qty} left)")
            cur.execute("SELECT invitem_name, invitem_expiry_date FROM inventory_item WHERE invitem_expiry_date <= %s", (datetime.date.today() + datetime.timedelta(days=30),))
            for name, exp in cur.fetchall():
                alerts.append(f"Expiring soon: <b>{name}</b> (expires {exp})")
            cur.execute("SELECT COUNT(*) FROM appointment WHERE apmt_date >= %s", (datetime.date.today(),))
            up_appt = cur.fetchone()[0]
            if up_appt:
                alerts.append(f"Upcoming appointments: <b>{up_appt}</b> scheduled.")
            if pending_ref > 0:
                alerts.append(f"<b>{pending_ref}</b> pending referrals.")
            if not alerts:
                alerts.append("No critical alerts at the moment.")
            self.alerts_label.setText("<br>".join(alerts))

            # Emergency Hotlines
            self.load_hotlines(cur)

            # Recent Clinic Visits
            cur.execute("""
                SELECT v.stud_id,
                    s.stud_lname || ', ' || s.stud_fname || CASE WHEN s.stud_mname IS NOT NULL AND s.stud_mname <> '' THEN ' ' || s.stud_mname ELSE '' END AS stud_fullname,
                    v.cvl_date, v.cvl_reason, v.cvl_time_in, v.cvl_time_out
                FROM clinic_visit_log v
                LEFT JOIN student s ON v.stud_id = s.stud_id
                ORDER BY v.cvl_date DESC, v.cvl_time_in DESC
                LIMIT 8
            """)
            rows = cur.fetchall()
            self.visits_table.setRowCount(0)
            for idx, row in enumerate(rows):
                r = self.visits_table.rowCount()
                self.visits_table.insertRow(r)
                for c, val in enumerate(row):
                    self.visits_table.setItem(r, c, QTableWidgetItem(str(val) if val is not None else ""))
            # Set vertical header numbers (1-based)
            for r in range(self.visits_table.rowCount()):
                self.visits_table.setVerticalHeaderItem(r, QTableWidgetItem(str(r + 1)))

            # Recent Activity Feed
            feed = []
            cur.execute("""SELECT stud_id, cvl_date, cvl_reason FROM clinic_visit_log ORDER BY created_at DESC LIMIT 4""")
            for sid, vdate, reason in cur.fetchall():
                feed.append(f"Clinic visit: <b>{sid}</b> ({vdate}) - {reason}")
            cur.execute("""SELECT stud_id, med_name, med_start_date FROM medication ORDER BY created_at DESC LIMIT 3""")
            for sid, med, date in cur.fetchall():
                feed.append(f"Medication dispensed: <b>{med}</b> to {sid} ({date})")
            cur.execute("""SELECT stud_id, ir_description, ir_date_incident FROM incident_report ORDER BY created_at DESC LIMIT 3""")
            for sid, desc, date in cur.fetchall():
                feed.append(f"Incident: {sid} ({date}) - {desc[:30]}...")
            self.feed_label.setText("<br>".join(feed[:8]) if feed else "No recent activity.")

            cur.close()
        except Exception as e:
            self.alerts_label.setText("Error loading dashboard: " + str(e))
            self.hotline_label.setText("Error loading hotlines: " + str(e))

    def load_hotlines(self, cur):
        try:
            hotlines = []
            cur.execute("""
                SELECT ehotline_agency_name, ehotline_contnumber, ehotline_type
                FROM emergency_hotline
                ORDER BY ehotline_type, ehotline_agency_name
            """)
            rows = cur.fetchall()
            for agency, cont, typ in rows:
                hotlines.append(f"<b>{agency}</b> ({typ}): {cont}")
            self.hotline_label.setText("<br>".join(hotlines) if hotlines else "No hotlines registered.")
        except Exception as e:
            self.hotline_label.setText("Error loading hotlines: " + str(e))

    def add_hotline(self):
        dialog = AddHotlineDialog(self)
        if dialog.exec_():
            agency, contact, typ = dialog.get_data()
            if not agency or not contact or not typ:
                QMessageBox.warning(self, "Invalid Input", "All fields are required.")
                return
            try:
                conn = self.conn
                cur = conn.cursor()
                cur.execute("""
                    INSERT INTO emergency_hotline (ehotline_agency_name, ehotline_contnumber, ehotline_type, created_at, updated_at)
                    VALUES (%s, %s, %s, NOW(), NOW())
                """, (agency, contact, typ))
                conn.commit()
                self.refresh_dashboard()
                QMessageBox.information(self, "Success", "Emergency hotline added successfully!")
            except Exception as e:
                QMessageBox.critical(self, "Database Error", f"Error adding hotline: {e}")

    def goto_patients(self): self.parent().setCurrentIndex(1)
    def goto_clinic_visit(self): self.parent().setCurrentIndex(6)
    def goto_medication(self): self.parent().setCurrentIndex(4)
    def goto_reports(self): self.parent().setCurrentIndex(2)

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
        sidebar_layout.setSpacing(18)

        # --- LOGO IMAGE ---
        logo_label = QLabel()
        logo_pixmap = QPixmap("LOGO.png")
        if not logo_pixmap.isNull():
            logo_pixmap = logo_pixmap.scaled(150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_label.setPixmap(logo_pixmap)
            logo_label.setAlignment(Qt.AlignCenter)
            logo_label.setStyleSheet("padding: 20px;")
        else:
            logo_label.setText("LOGO.png")
            logo_label.setAlignment(Qt.AlignCenter)
            logo_label.setStyleSheet(
                "border: 2px dashed #AAAAAA; font-size: 18px; color: #888888; padding: 60px;"
            )
        sidebar_layout.addWidget(logo_label)

        self.conn = psycopg2.connect(
            host="localhost",
            database="SAMPLE",
            user="postgres",
            password="123"
        )

        self.pages = QStackedWidget()
        self.dashboard_page = HomeDashboardPage(self.conn)
        self.patients_page = PatientsPage()
        self.reports_page = ReportsPage(self.conn)
        self.storage_page = StoragePage()
        self.medication_page = MedicationPage()
        self.referral_page = ReferralPage()
        self.clinic_visit_log_page = ClinicVisitLog()

        self.pages.addWidget(self.dashboard_page)         # index 0
        self.pages.addWidget(self.patients_page)          # index 1
        self.pages.addWidget(self.reports_page)           # index 2
        self.pages.addWidget(self.storage_page)           # index 3
        self.pages.addWidget(self.medication_page)        # index 4
        self.pages.addWidget(self.referral_page)          # index 5
        self.pages.addWidget(self.clinic_visit_log_page)  # index 6

        menu_items = [
            ("Dashboard", self.dashboard_page),
            ("Patients", self.patients_page),
            ("Generate Reports", self.reports_page),
            ("Storage", self.storage_page),
            ("Medication", self.medication_page),
            ("Referral", self.referral_page),
            ("Clinic Visit Log", self.clinic_visit_log_page),
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
        self.setLayout(main_layout)

if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    win = DashboardUI()
    win.show()
    sys.exit(app.exec_())
