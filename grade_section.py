from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QScrollArea
from PyQt5.QtCore import Qt

class GradeSectionPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        container = QWidget()
        inner_layout = QVBoxLayout(container)
        inner_layout.setSpacing(20)

        banner = QLabel("School Employee And Staffs")
        banner.setStyleSheet("""
            background-color: #FFE1D3;
            padding: 20px;
            border-radius: 20px;
            font-weight: bold;
            font-size: 24px;
        """)
        banner.setAlignment(Qt.AlignCenter)
        inner_layout.addWidget(banner)

        for title in ["Grade 7", "Grade 8", "Grade 9", "Grade 10", "Grade 11", "Grade 12"]:
            section = QLabel(f"{title} Section Placeholder")
            section.setStyleSheet("""
                background-color: #FFD5C2;
                padding: 40px;
                border-radius: 15px;
                font-weight: bold;
                font-size: 20px;
            """)
            section.setAlignment(Qt.AlignCenter)    
            inner_layout.addWidget(section)

        scroll.setWidget(container)
        layout.addWidget(scroll)
