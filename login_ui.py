    from PyQt5.QtWidgets import QWidget, QLabel, QLineEdit, QPushButton, QHBoxLayout, QVBoxLayout, QFrame
    from PyQt5.QtGui import QFont
    from PyQt5.QtCore import Qt
    from dashboard_ui import DashboardUI  # Import DashboardUI
    
    class LoginUI(QWidget):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("Clinic Patient's Dashboard - Login")
            self.setStyleSheet("background-color: #FFE3D2;")
            self.init_ui()
            self.showFullScreen()  # Make the window full screen
    
        def init_ui(self):
            main_layout = QHBoxLayout(self)
    
            # Left side (Logo placeholder)
            left_frame = QFrame()
            left_layout = QVBoxLayout(left_frame)
            left_layout.setAlignment(Qt.AlignCenter)
    
            title = QLabel("SNSH MediTrack")
            title.setFont(QFont("Arial", 24))
            title.setAlignment(Qt.AlignCenter)
    
            logo_placeholder = QLabel("LOGO HERE")
            logo_placeholder.setAlignment(Qt.AlignCenter)
            logo_placeholder.setStyleSheet(
                "border: 2px dashed #AAAAAA; font-size: 24px; color: #888888; padding: 100px;"
            )
    
            left_layout.addWidget(title)
            left_layout.addWidget(logo_placeholder)
    
            # Right side (Form)
            right_frame = QFrame()
            right_frame.setStyleSheet("background-color: #FDBD8D; border-radius: 20px;")
            right_layout = QVBoxLayout(right_frame)
            right_layout.setContentsMargins(60, 60, 60, 60)
            right_layout.setSpacing(30)
    
            welcome_label = QLabel("Welcome\nBack")
            welcome_label.setFont(QFont("Arial", 40, QFont.Bold))
            welcome_label.setAlignment(Qt.AlignLeft)
            welcome_label.setStyleSheet("color: #2F2F2F;")
    
            self.email_input = QLineEdit()
            self.email_input.setPlaceholderText("E- Mail")
            self.email_input.setStyleSheet("padding: 20px; font-size: 18px; border: 2px solid #444; border-radius: 30px;")
    
            self.password_input = QLineEdit()
            self.password_input.setPlaceholderText("Password")
            self.password_input.setEchoMode(QLineEdit.Password)
            self.password_input.setStyleSheet("padding: 20px; font-size: 18px; border: 2px solid #444; border-radius: 30px;")
    
            login_btn = QPushButton("Log-In")
            login_btn.setStyleSheet(
                "background-color: #10562E; color: white; font-size: 20px; padding: 15px; border-radius: 15px;"
            )
            login_btn.clicked.connect(self.login)
    
            signup_label = QLabel("If You Didn't Have Account <a href='#'>Sign-Up</a>")
            signup_label.setTextFormat(Qt.RichText)
            signup_label.setAlignment(Qt.AlignCenter)
            signup_label.setStyleSheet("color: #333; font-size: 16px;")
            signup_label.setOpenExternalLinks(False)
    
            # Add to right layout
            right_layout.addWidget(welcome_label)
            right_layout.addWidget(self.email_input)
            right_layout.addWidget(self.password_input)
            right_layout.addWidget(login_btn)
            right_layout.addWidget(signup_label)
    
            # Add both frames to main layout
            main_layout.addWidget(left_frame, 1)
            main_layout.addWidget(right_frame, 1)
    
        def login(self):
            # Close the login window and open the DashboardUI
            self.close()
    
            self.dashboard_window = DashboardUI()
            self.dashboard_window.show()
