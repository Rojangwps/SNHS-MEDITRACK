from PyQt5.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton, QHBoxLayout, QVBoxLayout,
    QFrame, QMessageBox, QCheckBox, QSpacerItem, QSizePolicy, QApplication
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from dashboard_ui import DashboardUI
import psycopg2

def get_db_connection():
    return psycopg2.connect(
        host="localhost",
        database="SAMPLE",  # Change if needed
        user="postgres",    # Change if needed
        password="123"      # Change if needed
    )

class LoginUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Clinic Patient's Dashboard - Login")
        self.setStyleSheet("background-color: #FFE3D2;")
        self.init_ui()
        self.showFullScreen()

    def init_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Left side (Logo placeholder)
        left_frame = QFrame()
        left_layout = QVBoxLayout(left_frame)
        left_layout.setAlignment(Qt.AlignCenter)
        left_frame.setStyleSheet("background-color: #FDD1B0;")

        title = QLabel("SNSH MediTrack")
        title.setFont(QFont("Arial", 32, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #444; margin-bottom: 20px;")

        logo_placeholder = QLabel("LOGO HERE")
        logo_placeholder.setAlignment(Qt.AlignCenter)
        logo_placeholder.setStyleSheet(
            "border: 2px dashed #AAAAAA; font-size: 24px; color: #888888; padding: 100px; margin-bottom: 40px;"
        )

        left_layout.addStretch(1)
        left_layout.addWidget(title)
        left_layout.addWidget(logo_placeholder)
        left_layout.addStretch(2)

        # Right side (Form)
        right_frame = QFrame()
        right_frame.setStyleSheet("background-color: #FDBD8D; border-radius: 20px;")
        right_layout = QVBoxLayout(right_frame)
        right_layout.setContentsMargins(80, 80, 80, 80)
        right_layout.setSpacing(30)

        welcome_label = QLabel("Welcome\nBack")
        welcome_label.setFont(QFont("Arial", 44, QFont.Bold))
        welcome_label.setAlignment(Qt.AlignLeft)
        welcome_label.setStyleSheet("color: #2F2F2F; margin-bottom: 10px;")

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")
        self.username_input.setStyleSheet("""
            padding: 20px; font-size: 18px; border: 2px solid #444; border-radius: 30px;
            background: #fff8f4;
        """)
        self.username_input.setClearButtonEnabled(True)
        self.username_input.setMinimumHeight(46)
        self.username_input.setFont(QFont("Arial", 16))

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setStyleSheet("""
            padding: 20px; font-size: 18px; border: 2px solid #444; border-radius: 30px;
            background: #fff8f4;
        """)
        self.password_input.setClearButtonEnabled(True)
        self.password_input.setMinimumHeight(46)
        self.password_input.setFont(QFont("Arial", 16))

        self.show_password_cb = QCheckBox("Show password")
        self.show_password_cb.setStyleSheet("font-size: 14px; color: #555; margin-left: 8px;")
        self.show_password_cb.stateChanged.connect(self.toggle_password_visibility)

        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: #d32f2f; font-size: 16px;")
        self.error_label.setVisible(False)

        login_btn = QPushButton("Log In")
        login_btn.setStyleSheet("""
            QPushButton {
                background-color: #10562E; color: white; font-size: 20px; padding: 15px; border-radius: 15px;
            }
            QPushButton:disabled {
                background-color: #b5c7bb;
                color: #fff;
            }
        """)
        login_btn.setCursor(Qt.PointingHandCursor)
        login_btn.clicked.connect(self.login)
        login_btn.setMinimumHeight(44)
        self.login_btn = login_btn

        # Sign up label (not implemented)
        signup_label = QLabel(
            "Don't have an account? <a href='#' style='color:#10562E'><b>Sign Up</b></a>"
        )
        signup_label.setTextFormat(Qt.RichText)
        signup_label.setAlignment(Qt.AlignCenter)
        signup_label.setStyleSheet("color: #333; font-size: 16px;")
        signup_label.setOpenExternalLinks(False)
        signup_label.linkActivated.connect(self.signup_clicked)

        right_layout.addWidget(welcome_label)
        right_layout.addWidget(self.username_input)
        right_layout.addWidget(self.password_input)
        right_layout.addWidget(self.show_password_cb)
        right_layout.addWidget(self.error_label)
        right_layout.addSpacerItem(QSpacerItem(20, 12, QSizePolicy.Minimum, QSizePolicy.Fixed))
        right_layout.addWidget(login_btn)
        right_layout.addWidget(signup_label)
        right_layout.addStretch(1)

        main_layout.addWidget(left_frame, 1)
        main_layout.addWidget(right_frame, 1)

        self.username_input.returnPressed.connect(self.focus_password)
        self.password_input.returnPressed.connect(self.login)
        self.setTabOrder(self.username_input, self.password_input)
        self.setTabOrder(self.password_input, self.show_password_cb)
        self.setTabOrder(self.show_password_cb, self.login_btn)

    def focus_password(self):
        self.password_input.setFocus()

    def toggle_password_visibility(self, state):
        if state:
            self.password_input.setEchoMode(QLineEdit.Normal)
        else:
            self.password_input.setEchoMode(QLineEdit.Password)

    def validate_inputs(self):
        username = self.username_input.text().strip()
        password = self.password_input.text()
        if not username or not password:
            return False, "Please enter both Username and Password."
        return True, ""

    def set_loading(self, loading):
        self.login_btn.setDisabled(loading)
        QApplication.processEvents()

    def login(self):
        self.error_label.setVisible(False)
        valid, message = self.validate_inputs()
        if not valid:
            self.error_label.setText(message)
            self.error_label.setVisible(True)
            return

        username = self.username_input.text().strip()
        password = self.password_input.text()
        self.set_loading(True)
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            # Use email as username for login
            cur.execute(
                "SELECT id FROM users WHERE email = %s AND password = %s",
                (username, password)
            )
            result = cur.fetchone()
            cur.close()
            conn.close()
            if result:
                self.close()
                self.dashboard_window = DashboardUI()
                self.dashboard_window.show()
            else:
                self.error_label.setText("Invalid username or password.")
                self.error_label.setVisible(True)
        except Exception as e:
            self.error_label.setText(f"Database error: {e}")
            self.error_label.setVisible(True)
        finally:
            self.set_loading(False)

    def signup_clicked(self):
        QMessageBox.information(self, "Sign Up", "Sign-up feature coming soon!")
