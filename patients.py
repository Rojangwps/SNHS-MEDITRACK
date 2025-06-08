import psycopg2
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QLineEdit, QDateEdit, QComboBox, QMessageBox,
    QListWidget, QFrame, QFormLayout, QGroupBox, QStackedWidget,
    QTextEdit, QSpinBox, QTableWidget, QTableWidgetItem, QHeaderView, QFileDialog,
)
from PyQt5.QtGui import QFont, QPixmap, QIcon, QIntValidator
from PyQt5.QtCore import Qt, QDate
import datetime

class PatientsPage(QWidget):
    def __init__(self):
        super().__init__()
        self.conn = None
        self.init_ui()
        self.connect_db()
        self.load_year_level()
        self.show_view_students()

    def init_ui(self):
        self.main_layout = QHBoxLayout(self)
        self.setStyleSheet("background-color: #fff6f1;")
        self.center_frame = QFrame()
        self.center_frame.setMaximumHeight(1020)  # You can adjust this number as needed
        self.center_frame.setObjectName("MainFrame")
        self.center_frame.setStyleSheet("""
            QFrame#MainFrame {
                background: #FBE0D0;
                border-radius: 18px;
                border: 1.5px solid #d9b79e;
            }
        """)
        self.center_frame_layout = QVBoxLayout(self.center_frame)
        self.center_frame_layout.setContentsMargins(24, 0, 24, 0)
        self.center_frame_layout.setSpacing(18)
        self.main_layout.addWidget(self.center_frame, stretch=8)

        self.header = QLabel("View Students")
        self.header.setFont(QFont("Arial", 28, QFont.Bold))
        self.header.setAlignment(Qt.AlignCenter)
        self.header.setStyleSheet("""
            background: #fbe0d0;
            border-radius: 6px;
            padding: 12px 0 12px 0;
            margin-bottom: 8px;
        """)
        self.center_frame_layout.addWidget(self.header)

        # --- FILTER WIDGET (for View Students only) ---
        self.filter_widget = QWidget()
        filter_row = QHBoxLayout(self.filter_widget)
        filter_row.setSpacing(18)
        lbl_year = QLabel("Year Level:")
        lbl_year.setFont(QFont("Arial", 16))
        self.year_level_input_view = QComboBox()
        self.year_level_input_view.setFont(QFont("Arial", 16))
        self.year_level_input_view.setFixedWidth(250)
        self.filter_widget.setStyleSheet("background-color: #FBE0D0; border-radius: 8px;")
        self.year_level_input_view.setStyleSheet(
            "background-color: #FFF0F5; border: 2px solid #D295BF; border-radius: 5px;")
        self.year_level_input_view.addItem("Select Year Level", -1)
        self.year_level_input_view.currentIndexChanged.connect(self.load_sections_for_year_view)
        self.year_level_input_view.setToolTip("Select a year level to filter students.")

        lbl_section = QLabel("Section:")
        lbl_section.setFont(QFont("Arial", 16))
        self.section_input_view = QComboBox()
        self.section_input_view.setFont(QFont("Arial", 16))
        self.section_input_view.setFixedWidth(250)
        self.section_input_view.setStyleSheet(
            "background-color: #FFF0F5; border: 2px solid #D295BF; border-radius: 5px;")
        self.section_input_view.addItem("Select Section", -1)
        self.section_input_view.setToolTip("Select a section to filter students.")

        filter_row.addWidget(lbl_year)
        filter_row.addWidget(self.year_level_input_view)
        filter_row.addWidget(lbl_section)
        filter_row.addWidget(self.section_input_view)
        filter_row.addStretch()
        self.center_frame_layout.addWidget(self.filter_widget)

        self.view_students_button = QPushButton("View Students")
        self.view_students_button.setStyleSheet("""
            QPushButton {
                background-color: #5dade2;
                color: white;
                font-weight: bold;
                font-size: 22px;
                border-radius: 8px;
                padding: 12px 0;
                margin-bottom: 8px;
            }
            QPushButton:hover {
                background-color: #3779a5;
            }
        """)
        self.view_students_button.setMinimumHeight(44)
        self.view_students_button.clicked.connect(self.display_students)
        self.center_frame_layout.addWidget(self.view_students_button)

        # ----- TABLE FOR STUDENTS -----
        self.students_table = QTableWidget()
        self.students_table.setFont(QFont("Arial", 25))
        self.students_table.setColumnCount(5)
        self.students_table.setHorizontalHeaderLabels(["LRN", "Last Name", "Middle Name", "First Name", "Edit"])
        self.students_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.students_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.students_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.students_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.students_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.Stretch)
        self.students_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.students_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.students_table.setStyleSheet("""
            QTableWidget {
                background: #fff6f1;
                border-radius: 12px;
                font-size: 22px;
            }
            QHeaderView::section {
                background: #FFE1D3;
                font-weight: bold;
                font-size: 21px;
                border: 1.5px solid #d9b79e;
                padding: 10px 0;
            }
        """)
        self.center_frame_layout.addWidget(self.students_table)

        # --- BUTTONS AT THE BOTTOM ---
        btns_row = QHBoxLayout()
        btns_row.setSpacing(22)
        btns_row.setContentsMargins(24, 10, 24, 14)
        self.btn_switch_to_add = QPushButton("Add Student")
        self.btn_switch_to_add.setStyleSheet("""
            QPushButton {
                background-color: #d295bf;
                color: white;
                font-weight: bold;
                font-size: 20px;
                border-radius: 10px;
                padding: 10px 0;
            }
            QPushButton:hover {
                background-color: #a77299;
            }
        """)
        self.btn_switch_to_add.setMinimumHeight(44)
        self.btn_switch_to_add.clicked.connect(self.show_add_student)
        btns_row.addWidget(self.btn_switch_to_add)

        self.btn_switch_to_manage = QPushButton("Manage Year Level and Section")
        self.btn_switch_to_manage.setStyleSheet("""
            QPushButton {
                background-color: #7dcea0;
                color: white;
                font-weight: bold;
                font-size: 20px;
                border-radius: 10px;
                padding: 10px 0;

            }
            QPushButton:hover {
                background-color: #51956b;
            }
        """)
        self.btn_switch_to_manage.setMinimumHeight(44)
        self.btn_switch_to_manage.clicked.connect(self.show_manage_year_section)
        btns_row.addWidget(self.btn_switch_to_manage)

        self.btn_switch_to_view = QPushButton("View Students")
        self.btn_switch_to_view.setStyleSheet("""
            QPushButton {
                background-color: #5dade2;
                color: white;
                font-weight: bold;
                font-size: 20px;
                border-radius: 10px;
                padding: 10px 0;
            }
            QPushButton:hover {
                background-color: #3779a5;
            }
        """)
        self.btn_switch_to_view.setMinimumHeight(44)
        self.btn_switch_to_view.clicked.connect(self.show_view_students)
        btns_row.addWidget(self.btn_switch_to_view)

        self.center_frame_layout.addLayout(btns_row)

        self.create_add_student_form()
        self.manage_widget = QWidget()
        self.manage_layout = QVBoxLayout(self.manage_widget)
        self.manage_layout.setSpacing(20)

        yl_label = QLabel("Manage Year Levels")
        yl_label.setFont(QFont("Arial", 20, QFont.Bold))
        self.manage_layout.addWidget(yl_label)

        yl_form_layout = QHBoxLayout()
        self.year_level_name_input = QLineEdit()
        self.year_level_name_input.setPlaceholderText("Enter New Year Level Name")
        self.year_level_name_input.setFont(QFont("Arial", 20))
        self.year_level_name_input.setFixedHeight(40)
        yl_form_layout.addWidget(self.year_level_name_input)

        self.btn_add_year_level = QPushButton("Add Year Level")
        self.btn_add_year_level.setStyleSheet(
            "background-color: #27AE60; color: white; font-weight: bold; padding: 12px; border-radius: 8px; font-size: 16px;")
        self.btn_add_year_level.clicked.connect(self.add_year_level)
        yl_form_layout.addWidget(self.btn_add_year_level)
        self.manage_layout.addLayout(yl_form_layout)

        self.year_level_list = QListWidget()
        self.year_level_list.setFont(QFont("Arial", 14))
        self.year_level_list.setFixedHeight(150)
        self.year_level_list.itemClicked.connect(self.load_sections_for_selected_year_level)
        self.manage_layout.addWidget(self.year_level_list)
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        self.manage_layout.addWidget(separator)

        sec_label = QLabel("Manage Sections")
        sec_label.setFont(QFont("Arial", 20, QFont.Bold))
        self.manage_layout.addWidget(sec_label)
        sec_form_layout = QHBoxLayout()
        self.section_year_level_combo = QComboBox()
        self.section_year_level_combo.addItem("Select Year Level", -1)
        self.section_year_level_combo.setFont(QFont("Arial", 15))
        self.section_year_level_combo.setFixedHeight(40)
        sec_form_layout.addWidget(self.section_year_level_combo)
        self.section_name_input = QLineEdit()
        self.section_name_input.setPlaceholderText("Enter New Section Name")
        self.section_name_input.setFont(QFont("Arial", 15))
        self.section_name_input.setFixedHeight(40)
        sec_form_layout.addWidget(self.section_name_input)
        self.btn_add_section = QPushButton("Add Section")
        self.btn_add_section.setStyleSheet(
            "background-color: #2874A6; color: white; font-weight: bold; padding: 12px; border-radius: 8px; font-size: 16px;")
        self.btn_add_section.clicked.connect(self.add_section)
        sec_form_layout.addWidget(self.btn_add_section)
        self.manage_layout.addLayout(sec_form_layout)
        self.section_list = QListWidget()
        self.section_list.setFont(QFont("Arial", 14))
        self.section_list.setFixedHeight(150)
        self.manage_layout.addWidget(self.section_list)
        self.btn_back_from_manage = QPushButton("Back to View Students")
        self.btn_back_from_manage.setStyleSheet(
            "background-color: #5DADE2; color: white; font-weight: bold; padding: 15px; border-radius: 10px; font-size: 18px;")
        self.btn_back_from_manage.clicked.connect(self.show_view_students)
        self.manage_layout.addWidget(self.btn_back_from_manage)
        self.student_cards = []

    def create_add_student_form(self):
        from PyQt5.QtWidgets import QRadioButton, QButtonGroup

        self.add_form_stack = QStackedWidget()
        INPUT_STYLE = """
            QLineEdit, QDateEdit, QComboBox, QTextEdit {
                background-color: #FFF0F5;
                border: 2px solid #D295BF;
                border-radius: 7px;
                font-size: 18px;
                padding: 8px 12px;
            }
            QLineEdit:focus, QDateEdit:focus, QComboBox:focus {
                border: 2.5px solid #c86ec9;
                background-color: #ffe8fa;
            }
        """

        # --- Page 1: Student Info ---
        page1 = QWidget()
        layout1 = QVBoxLayout(page1)
        layout1.setContentsMargins(16, 16, 16, 16)
        layout1.setSpacing(18)

        # --- Student Details (left) ---
        student_group = QGroupBox("Student Details")
        student_form = QFormLayout(student_group)
        student_group.setFont(QFont("Arial", 14, QFont.Bold))
        student_form.setHorizontalSpacing(10)

        self.lrn_input = QLineEdit()
        self.lrn_input.setPlaceholderText("Enter numeric LRN")
        self.lrn_input.setFont(QFont("Arial", 18))
        self.lrn_input.setFixedHeight(42)
        self.lrn_input.setFixedWidth(200)
        self.lrn_input.setStyleSheet(INPUT_STYLE)

        self.fname_input = QLineEdit()
        self.fname_input.setPlaceholderText("First Name")
        self.fname_input.setFont(QFont("Arial", 16))
        self.fname_input.setFixedHeight(42)
        self.fname_input.setFixedWidth(250)
        self.fname_input.setStyleSheet(INPUT_STYLE)

        self.mname_input = QLineEdit()
        self.mname_input.setPlaceholderText("Middle Name")
        self.mname_input.setFont(QFont("Arial", 16))
        self.mname_input.setFixedHeight(42)
        self.mname_input.setFixedWidth(250)
        self.mname_input.setStyleSheet(INPUT_STYLE)

        self.lname_input = QLineEdit()
        self.lname_input.setPlaceholderText("Last Name")
        self.lname_input.setFont(QFont("Arial", 16))
        self.lname_input.setFixedHeight(42)
        self.lname_input.setFixedWidth(250)
        self.lname_input.setStyleSheet(INPUT_STYLE)

        self.dob_input = QDateEdit()
        self.dob_input.setCalendarPopup(True)
        self.dob_input.setDate(QDate.currentDate())
        self.dob_input.setFont(QFont("Arial", 16))
        self.dob_input.setFixedHeight(42)
        self.dob_input.setFixedWidth(150)
        self.dob_input.setStyleSheet(INPUT_STYLE)

        self.gender_input = QComboBox()
        self.gender_input.addItems(["Select Gender", "Male", "Female", "Other"])
        self.gender_input.setFont(QFont("Arial", 16))
        self.gender_input.setFixedHeight(42)
        self.gender_input.setFixedWidth(170)
        self.gender_input.setStyleSheet(INPUT_STYLE)

        self.year_level_input_add = QComboBox()
        self.year_level_input_add.addItem("Select Year Level", -1)
        self.year_level_input_add.setFont(QFont("Arial", 16))
        self.year_level_input_add.setFixedHeight(42)
        self.year_level_input_add.setFixedWidth(170)
        self.year_level_input_add.setToolTip("Select year level for student")
        self.year_level_input_add.setStyleSheet(INPUT_STYLE)
        self.year_level_input_add.currentIndexChanged.connect(self.load_sections_for_add_form)

        self.section_input_add = QComboBox()
        self.section_input_add.addItem("Select Section", -1)
        self.section_input_add.setFont(QFont("Arial", 16))
        self.section_input_add.setFixedHeight(42)
        self.section_input_add.setFixedWidth(170)
        self.section_input_add.setToolTip("Select section for student")
        self.section_input_add.setStyleSheet(INPUT_STYLE)

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("example@mail.com")
        self.email_input.setFont(QFont("Arial", 16))
        self.email_input.setFixedHeight(42)
        self.email_input.setFixedWidth(400)
        self.email_input.setStyleSheet(INPUT_STYLE)

        self.address_input = QLineEdit()
        self.address_input.setPlaceholderText("Street, City, Province")
        self.address_input.setFont(QFont("Arial", 16))
        self.address_input.setFixedHeight(42)
        self.address_input.setFixedWidth(700)
        self.address_input.setStyleSheet(INPUT_STYLE)

        # Add to the form layout
        student_form.addRow("LRN*", self.lrn_input)
        student_form.addRow("First Name*", self.fname_input)
        student_form.addRow("Middle Name", self.mname_input)
        student_form.addRow("Last Name*", self.lname_input)
        student_form.addRow("Date of Birth*", self.dob_input)
        student_form.addRow("Gender*", self.gender_input)
        student_form.addRow("Year Level*", self.year_level_input_add)
        student_form.addRow("Section*", self.section_input_add)
        student_form.addRow("Email", self.email_input)
        student_form.addRow("Address", self.address_input)

        # --- Parent/Guardian Details (right) ---
        parent_group = QGroupBox("Parent/Guardian Details")
        parent_form = QFormLayout(parent_group)
        parent_group.setFont(QFont("Arial", 14, QFont.Bold))

        self.parent_name_input = QLineEdit()
        self.parent_name_input.setPlaceholderText("Parent's Full Name")
        self.parent_name_input.setFont(QFont("Arial", 16))
        self.parent_name_input.setFixedHeight(42)
        self.parent_name_input.setFixedWidth(300)
        self.parent_name_input.setStyleSheet(INPUT_STYLE)

        self.parent_contact_input = QLineEdit()
        self.parent_contact_input.setPlaceholderText("09xxxxxxxxx")
        self.parent_contact_input.setFont(QFont("Arial", 16))
        self.parent_contact_input.setFixedHeight(42)
        self.parent_contact_input.setFixedWidth(200)
        self.parent_contact_input.setStyleSheet(INPUT_STYLE)
        parent_form.addRow("Parent's Name", self.parent_name_input)
        parent_form.addRow("Parent's Contact", self.parent_contact_input)
        parent_group.setFixedHeight(140)
        parent_group.setMinimumWidth(340)

        parent_container = QWidget()
        parent_container_layout = QVBoxLayout(parent_container)
        parent_container_layout.setContentsMargins(0, 0, 0, 400)  # LEFT, TOP, RIGHT, BOTTOM (e.g. 40px top margin)
        parent_container_layout.addWidget(parent_group)

        # --- Place Student and Parent/Guardian Details side by side ---
        details_row = QHBoxLayout()
        details_row.addWidget(student_group, stretch=2)
        details_row.addSpacing(24)
        details_row.addWidget(parent_container, stretch=1)
        layout1.addLayout(details_row)

        # --- Status Details below both ---
        status_group = QGroupBox("Status Details")
        status_form = QFormLayout(status_group)
        status_group.setFont(QFont("Arial", 14, QFont.Bold))
        status_form.setLabelAlignment(Qt.AlignRight)
        status_form.setFormAlignment(Qt.AlignLeft | Qt.AlignTop)

        self.status_input = QComboBox()
        self.status_input.addItems(["Select Status", "Active", "Inactive"])
        self.status_input.setFont(QFont("Arial", 16))
        self.status_input.setFixedHeight(42)
        self.status_input.setFixedWidth(350)
        self.status_input.setStyleSheet(INPUT_STYLE)
        status_form.addRow("Status*", self.status_input)

        label_font = QFont("Arial", 12, QFont.Bold)
        for i in range(student_form.rowCount()):
            label_widget = student_form.itemAt(i, QFormLayout.LabelRole).widget()
            if label_widget:
                label_widget.setFont(label_font)
        for i in range(parent_form.rowCount()):
            label_widget = parent_form.itemAt(i, QFormLayout.LabelRole).widget()
            if label_widget:
                label_widget.setFont(label_font)
        for i in range(status_form.rowCount()):
            label_widget = status_form.itemAt(i, QFormLayout.LabelRole).widget()
            if label_widget:
                label_widget.setFont(label_font)

        layout1.addWidget(status_group)

        # --- Navigation Buttons ---
        nav1 = QHBoxLayout()
        nav1.addStretch()
        self.btn_to_health = QPushButton("Next: Health Record →")
        self.btn_to_health.setStyleSheet(
            "background-color: #D295BF; color: white; font-weight: bold; padding: 15px; border-radius: 10px; font-size: 18px;"
        )
        self.btn_to_health.clicked.connect(lambda: self.add_form_stack.setCurrentIndex(1))
        nav1.addWidget(self.btn_to_health)
        layout1.addLayout(nav1)

        self.add_form_stack.addWidget(page1)

        # --- Page 2: Health Record ---
        page2 = QWidget()
        layout2 = QVBoxLayout(page2)
        layout2.setContentsMargins(16, 16, 16, 16)
        layout2.setSpacing(18)

        health_group = QGroupBox("Health Record (Current Year)")
        health_form = QFormLayout(health_group)
        health_group.setFont(QFont("Arial", 14, QFont.Bold))
        health_form.setLabelAlignment(Qt.AlignLeft)
        health_form.setFormAlignment(Qt.AlignLeft | Qt.AlignTop)
        health_form.setHorizontalSpacing(8)
        health_form.setVerticalSpacing(3)

        self.hr_date_recorded = QDateEdit()
        self.hr_date_recorded.setCalendarPopup(True)
        self.hr_date_recorded.setDate(QDate.currentDate())
        self.hr_date_recorded.setFont(QFont("Arial", 16))
        self.hr_date_recorded.setFixedWidth(150)
        self.hr_date_recorded.setStyleSheet(INPUT_STYLE)

        self.hr_height = CmLineEdit()
        self.hr_height.setPlaceholderText("Enter (cm)")
        self.hr_height.setFont(QFont("Arial", 16))
        self.hr_height.setFixedWidth(150)
        self.hr_height.setStyleSheet(INPUT_STYLE)

        self.hr_weight = KgLineEdit()
        self.hr_weight.setPlaceholderText("Enter (kg)")
        self.hr_weight.setFont(QFont("Arial", 16))
        self.hr_weight.setFixedWidth(150)
        self.hr_weight.setStyleSheet(INPUT_STYLE)

        self.hr_allergies = QLineEdit()
        self.hr_allergies.setPlaceholderText("Enter Allergies")
        self.hr_allergies.setStyleSheet(INPUT_STYLE)
        self.hr_allergies.setFixedWidth(350)
        self.hr_allergies.setFont(QFont("Arial", 16))

        self.hr_notes = QTextEdit()
        self.hr_notes.setPlaceholderText("Enter Notes")
        self.hr_notes.setFixedHeight(80)
        self.hr_notes.setFixedWidth(500)
        self.hr_notes.setFont(QFont("Arial", 16))
        self.hr_notes.setStyleSheet(INPUT_STYLE)

        health_form.addRow("Date Recorded", self.hr_date_recorded)
        health_form.addRow("Height", self.hr_height)
        health_form.addRow("Weight", self.hr_weight)
        health_form.addRow("Allergies", self.hr_allergies)
        health_form.addRow("Notes", self.hr_notes)
        layout2.addWidget(health_group)

        # --- PUSH BUTTON prompt for current health issue ---
        prompt_row = QHBoxLayout()
        prompt_label = QLabel("Does the student have a current health issue?")
        prompt_label.setFont(QFont("Arial", 15))
        prompt_row.addWidget(prompt_label)
        self.btn_issue_no = QPushButton("No")
        self.btn_issue_yes = QPushButton("Yes")
        self.btn_issue_no.setStyleSheet(
            "background-color: #7dcea0; color: white; font-weight: bold; font-size: 18px; border-radius: 8px; padding: 8px 24px;")
        self.btn_issue_yes.setStyleSheet(
            "background-color: #d295bf; color: white; font-weight: bold; font-size: 18px; border-radius: 8px; padding: 8px 24px;")
        prompt_row.addWidget(self.btn_issue_no)
        prompt_row.addWidget(self.btn_issue_yes)
        prompt_row.addStretch()
        layout2.addLayout(prompt_row)
        # Navigation: No = skip to medical history, Yes = go to current health issue page
        self.btn_issue_no.clicked.connect(self.goto_medical_history_from_health)  # Page 4: Medical History
        self.btn_issue_yes.clicked.connect(self.goto_current_issue_from_health)  # Page 3: Current Health Issue

        nav2 = QHBoxLayout()
        self.btn_to_student = QPushButton("← Previous")
        self.btn_to_student.setStyleSheet(
            "background-color: #5DADE2; color: white; font-weight: bold; padding: 15px; border-radius: 10px; font-size: 18px;")
        self.btn_to_student.clicked.connect(lambda: self.add_form_stack.setCurrentIndex(0))
        nav2.addWidget(self.btn_to_student)
        nav2.addStretch()
        layout2.addLayout(nav2)
        label_style = """
        QLabel {
            font-family: Arial;
            font-size: 12pt;
            font-weight: bold;
        }
        """
        health_group.setStyleSheet(label_style)
        self.add_form_stack.addWidget(page2)

        # --- Page 3: Current Health Issue (NEW) ---
        page3 = QWidget()
        layout3 = QVBoxLayout(page3)
        layout3.setContentsMargins(16, 16, 16, 16)
        layout3.setSpacing(18)

        current_issue_group = QGroupBox("Current Health Issue")
        current_issue_group.setFont(QFont("Arial", 14, QFont.Bold))
        ci_form = QFormLayout(current_issue_group)
        ci_form.setLabelAlignment(Qt.AlignLeft)
        ci_form.setFormAlignment(Qt.AlignLeft | Qt.AlignTop)
        ci_form.setHorizontalSpacing(8)
        ci_form.setVerticalSpacing(3)

        self.ci_condition = QLineEdit()
        self.ci_condition.setPlaceholderText("Enter Condition")
        self.ci_condition.setFont(QFont("Arial", 16))
        self.ci_condition.setFixedWidth(350)
        self.ci_condition.setStyleSheet(INPUT_STYLE)

        self.ci_detected_date = QDateEdit()
        self.ci_detected_date.setFont(QFont("Arial", 16))
        self.ci_detected_date.setFixedWidth(150)
        self.ci_detected_date.setStyleSheet(INPUT_STYLE)
        self.ci_detected_date.setCalendarPopup(True)
        self.ci_detected_date.setDate(QDate.currentDate())

        self.ci_status = QLineEdit()
        self.ci_status.setPlaceholderText("Enter Status")
        self.ci_status.setFont(QFont("Arial", 16))
        self.ci_status.setFixedWidth(350)
        self.ci_status.setStyleSheet(INPUT_STYLE)

        self.ci_notes = QTextEdit()
        self.ci_notes.setPlaceholderText("Enter Notes")
        self.ci_notes.setFont(QFont("Arial", 16))
        self.ci_notes.setFixedWidth(500)
        self.ci_notes.setFixedHeight(80)
        self.ci_notes.setStyleSheet(INPUT_STYLE)

        ci_form.addRow("Condition*", self.ci_condition)
        ci_form.addRow("Detected Date*", self.ci_detected_date)
        ci_form.addRow("Status", self.ci_status)
        ci_form.addRow("Notes", self.ci_notes)
        layout3.addWidget(current_issue_group)

        nav3 = QHBoxLayout()
        self.btn_to_health2 = QPushButton("← Previous")
        self.btn_to_health2.setStyleSheet(
            "background-color: #5DADE2; color: white; font-weight: bold; padding: 15px; border-radius: 10px; font-size: 18px;")
        self.btn_to_health2.clicked.connect(
            lambda: print("Going back to Health Record") or self.add_form_stack.setCurrentIndex(1))
        self.btn_to_health2.clicked.connect(lambda: self.add_form_stack.setCurrentIndex(1))
        nav3.addWidget(self.btn_to_health2)
        nav3.addStretch()
        layout3.addLayout(nav3)
        self.btn_to_history = QPushButton("Next: Health History →")
        self.btn_to_history.setStyleSheet(
            "background-color: #D295BF; color: white; font-weight: bold; padding: 15px; border-radius: 10px; font-size: 18px;")
        self.btn_to_history.clicked.connect(lambda: self.add_form_stack.setCurrentIndex(3))
        nav3.addWidget(self.btn_to_history)
        layout3.addLayout(nav3)
        label_style = """
        QLabel {
            font-family: Arial;
            font-size: 12pt;
            font-weight: bold;
        }
        """
        current_issue_group.setStyleSheet(label_style)
        self.add_form_stack.addWidget(page3)

        # --- Page 4: Medical History ---
        page4 = QWidget()
        layout4 = QVBoxLayout(page4)
        layout4.setContentsMargins(16, 16, 16, 16)
        layout4.setSpacing(18)

        history_group = QGroupBox("Medical History")
        history_vbox = QVBoxLayout(history_group)
        self.medhist_table = QTableWidget(0, 4)
        history_group.setFont(QFont("Arial", 14, QFont.Bold))
        self.medhist_table.setHorizontalHeaderLabels(["Condition", "Diagnosis Date", "Notes", "Photo"])
        self.medhist_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        history_vbox.addWidget(self.medhist_table)
        self.medhist_table.setStyleSheet("""
        QHeaderView::section {
            background-color: #FBE0D0;
            color: #222;
            font-size: 18px;
            font-weight: bold;
            border: 1.5px solid #d9b79e;
            padding: 6px 0px;
        }
        QTableWidget {
            font-size: 15px;
            background: #fff6f1;
        }
    """)

        row_btns = QHBoxLayout()
        self.btn_add_history = QPushButton("Add History Row")
        self.btn_add_history.clicked.connect(self.add_history_row)
        self.btn_add_history.setStyleSheet(
            "background-color: #7dcea0; color: white; font-weight: bold; font-size: 18px; border-radius: 8px; padding: 8px 24px;")
        self.btn_remove_history = QPushButton("Remove Selected")
        self.btn_remove_history.clicked.connect(self.remove_history_row)
        self.btn_remove_history.setStyleSheet(
            "background-color: #d295bf; color: white; font-weight: bold; font-size: 18px; border-radius: 8px; padding: 8px 24px;")
        row_btns.addWidget(self.btn_add_history)
        row_btns.addWidget(self.btn_remove_history)
        row_btns.addStretch()
        history_vbox.addLayout(row_btns)
        layout4.addWidget(history_group)

        nav4 = QHBoxLayout()
        self.btn_to_health3 = QPushButton("← Previous")
        self.btn_to_health3.setStyleSheet(
            "background-color: #5DADE2; color: white; font-weight: bold; padding: 15px; border-radius: 10px; font-size: 18px;")
        # Go back to current health issue page if user used it, else health record page
        self.btn_to_health3.clicked.connect(self.go_to_previous_from_history)
        nav4.addWidget(self.btn_to_health3)
        nav4.addStretch()
        self.submit_button = QPushButton("Submit Student Info")
        self.submit_button.setStyleSheet("""
            QPushButton {
                background-color: #D295BF;
                color: white;
                padding: 16px;
                font-size: 18px;
                font-weight: bold;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #BA74AD;
            }
        """)
        self.submit_button.clicked.connect(self.submit_student)
        nav4.addWidget(self.submit_button)
        layout4.addLayout(nav4)
        self.add_form_stack.addWidget(page4)

        self.form_widget = QWidget()
        form_layout = QVBoxLayout(self.form_widget)
        form_layout.setContentsMargins(0, 0, 0, 0)
        form_layout.setSpacing(0)
        form_layout.addWidget(self.add_form_stack)

        # Make the form scrollable
        self.form_scroll = QScrollArea()
        self.form_scroll.setWidgetResizable(True)
        self.form_scroll.setWidget(self.form_widget)

        # Optional: Style the scrollbar to match your theme
        scrollbar_style = """
        QScrollBar:vertical {
            background: #FBE0D0;
        }
        """
        self.form_scroll.setStyleSheet(scrollbar_style)

    def goto_medical_history_from_health(self):
        self.has_current_issue = False
        self.add_form_stack.setCurrentIndex(3)  # Medical History

    def goto_current_issue_from_health(self):
        self.has_current_issue = True
        self.add_form_stack.setCurrentIndex(2)  # Current Health Issue

    def go_to_next_after_health(self):
        idx = self.current_issue_combo.currentIndex()
        if idx == 0:
            QMessageBox.warning(self, "Input Error", "Please select if the student has a current health issue.")
        elif idx == 1:  # No
            self.add_form_stack.setCurrentIndex(3)  # Go to Medical History
        else:  # Yes
            self.add_form_stack.setCurrentIndex(2)  # Go to Current Health Issue

    def go_to_previous_from_history(self):
        if self.has_current_issue:
            self.add_form_stack.setCurrentIndex(2)  # Back to current health issue
        else:
            self.add_form_stack.setCurrentIndex(1)  # Back to health record

    def add_history_row(self):
        row = self.medhist_table.rowCount()
        self.medhist_table.insertRow(row)
        self.medhist_table.setItem(row, 0, QTableWidgetItem(""))  # Condition
        dateedit = QDateEdit()
        dateedit.setCalendarPopup(True)
        dateedit.setDate(QDate.currentDate())
        self.medhist_table.setCellWidget(row, 1, dateedit)
        self.medhist_table.setItem(row, 2, QTableWidgetItem(""))  # Notes
        upload_btn = QPushButton("Upload Photo")
        upload_btn.clicked.connect(lambda _, r=row: self.upload_photo_for_history(r))
        self.medhist_table.setCellWidget(row, 3, upload_btn)
        self.medhist_table.setItem(row, 3, QTableWidgetItem(""))

    def upload_photo_for_history(self, row):
        fname, _ = QFileDialog.getOpenFileName(self, "Select Photo", "", "Images (*.png *.jpg *.jpeg *.bmp *.gif)")
        if fname:
            pixmap = QPixmap(fname)
            if not pixmap.isNull():
                thumbnail = pixmap.scaled(32, 32, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                icon = QIcon(thumbnail)
                btn = self.medhist_table.cellWidget(row, 3)
                btn.setIcon(icon)
            self.medhist_table.setItem(row, 3, QTableWidgetItem(fname))

    def remove_history_row(self):
        idx = self.medhist_table.currentRow()
        if idx >= 0:
            self.medhist_table.removeRow(idx)

    def connect_db(self):
        try:
            self.conn = psycopg2.connect(
                host="localhost",
                database="SAMPLE",
                user="postgres",
                password="123"
            )
        except Exception as e:
            QMessageBox.critical(self, "DB Connection Error", str(e))

    def load_year_level(self):
        if not self.conn:
            return
        cursor = self.conn.cursor()
        cursor.execute("SELECT year_level_id, year_level_name FROM year_level ORDER BY year_level_name")
        rows = cursor.fetchall()

        self.year_level_input_view.clear()
        self.year_level_input_view.addItem("Select Year Level", -1)
        self.section_year_level_combo.clear()
        self.section_year_level_combo.addItem("Select Year Level", -1)
        self.year_level_list.clear()
        self.year_level_input_add.clear()
        self.year_level_input_add.addItem("Select Yr Level", -1)

        for _id, name in rows:
            self.year_level_input_view.addItem(name, _id)
            self.section_year_level_combo.addItem(name, _id)
            self.year_level_list.addItem(f"{_id}: {name}")
            self.year_level_input_add.addItem(name, _id)
        cursor.close()

    def load_sections_for_add_form(self):
        year_level_id = self.year_level_input_add.currentData()
        if year_level_id is None or year_level_id == -1:
            self.section_input_add.clear()
            self.section_input_add.addItem("Select Section", -1)
            return
        cursor = self.conn.cursor()
        cursor.execute("SELECT section_id, section_name FROM section WHERE year_level_id = %s ORDER BY section_name",
                       (year_level_id,))
        rows = cursor.fetchall()
        self.section_input_add.clear()
        self.section_input_add.addItem("Select Section", -1)
        for _id, name in rows:
            self.section_input_add.addItem(name, _id)
        cursor.close()

    def load_sections_for_year_view(self):
        year_level_id = self.year_level_input_view.currentData()
        if year_level_id is None or year_level_id == -1:
            self.section_input_view.clear()
            self.section_input_view.addItem("Select Section", -1)
            return
        cursor = self.conn.cursor()
        cursor.execute("SELECT section_id, section_name FROM section WHERE year_level_id = %s ORDER BY section_name",
                       (year_level_id,))
        rows = cursor.fetchall()
        self.section_input_view.clear()
        self.section_input_view.addItem("Select Section", -1)
        for _id, name in rows:
            self.section_input_view.addItem(name, _id)
        cursor.close()

    # ... (create_add_student_form and all other unchanged methods remain here)

    # ---START OF EDIT BUTTON AND EDIT FUNCTIONALITY---
    def display_students(self):
        self.students_table.setRowCount(0)
        year_level_id = self.year_level_input_view.currentData()
        section_id = self.section_input_view.currentData()
        if year_level_id == -1 or section_id == -1:
            QMessageBox.warning(self, "Input Error", "Please select a valid Year Level and Section.")
            return

        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT stud_id, stud_lname, stud_mname, stud_fname FROM student
                WHERE year_level_id = %s AND section_id = %s
                ORDER BY stud_lname, stud_fname
            """, (year_level_id, section_id))
            students = cursor.fetchall()
            cursor.close()
            self.students_table.setRowCount(len(students))

            for row_idx, stud in enumerate(students):
                # LRN
                lrn_item = QTableWidgetItem(str(stud[0]))
                lrn_item.setTextAlignment(Qt.AlignCenter)
                self.students_table.setItem(row_idx, 0, lrn_item)

                # Last Name
                lastname_item = QTableWidgetItem(str(stud[1]))
                lastname_item.setTextAlignment(Qt.AlignCenter)
                self.students_table.setItem(row_idx, 1, lastname_item)

                # Middle Name
                middlename_item = QTableWidgetItem(str(stud[2]))
                middlename_item.setTextAlignment(Qt.AlignCenter)
                self.students_table.setItem(row_idx, 2, middlename_item)

                # First Name
                firstname_item = QTableWidgetItem(str(stud[3]))
                firstname_item.setTextAlignment(Qt.AlignCenter)
                self.students_table.setItem(row_idx, 3, firstname_item)

                # Edit Button
                edit_btn = QPushButton("Edit")
                edit_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #f7ca18;
                        color: #4a3625;
                        font-weight: bold;
                        font-size: 18px;
                        border-radius: 8px;
                        padding: 7px 28px;
                    }
                    QPushButton:hover {
                        background-color: #e1b12c;
                    }
                """)
                edit_btn.clicked.connect(lambda _, s_id=stud[0]: self.edit_student(s_id))
                btn_widget = QWidget()
                btn_layout = QHBoxLayout(btn_widget)
                btn_layout.addStretch()
                btn_layout.addWidget(edit_btn)
                btn_layout.addStretch()
                btn_layout.setContentsMargins(0, 0, 0, 0)
                self.students_table.setCellWidget(row_idx, 4, btn_widget)
        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"An error occurred while fetching students:\n{e}")

    def edit_student(self, stud_id):
        import datetime
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT
                    stud_id, stud_fname, stud_mname, stud_lname, stud_DOB, stud_gender,
                    section_id, year_level_id, stud_email_add, stud_address,
                    stud_parent_fname, stud_parent_lname, stud_parent_contnum, stud_status
                FROM student WHERE stud_id = %s
            """, (stud_id,))
            student = cursor.fetchone()
            if not student:
                QMessageBox.warning(self, "Not Found", f"No student found with LRN {stud_id}")
                cursor.close()
                return

            self.lrn_input.setText(str(student[0]))
            self.lrn_input.setReadOnly(True)
            self.fname_input.setText(student[1])
            self.mname_input.setText(student[2])
            self.lname_input.setText(student[3])

            dob_val = student[4]
            if isinstance(dob_val, datetime.date):
                self.dob_input.setDate(QDate(dob_val.year, dob_val.month, dob_val.day))
            else:
                self.dob_input.setDate(QDate.fromString(str(dob_val), "yyyy-MM-dd"))

            gender_index = self.gender_input.findText(str(student[5]))
            self.gender_input.setCurrentIndex(gender_index if gender_index != -1 else 0)

            yl_idx = self.year_level_input_add.findData(int(student[7]))
            self.year_level_input_add.setCurrentIndex(yl_idx if yl_idx != -1 else 0)
            self.load_sections_for_add_form()
            sec_idx = self.section_input_add.findData(int(student[6]))
            self.section_input_add.setCurrentIndex(sec_idx if sec_idx != -1 else 0)

            self.email_input.setText(student[8])
            self.address_input.setText(student[9])
            self.parent_name_input.setText(f"{student[10]} {student[11]}".strip())
            self.parent_contact_input.setText(student[12])
            status_index = self.status_input.findText(str(student[13]))
            self.status_input.setCurrentIndex(status_index if status_index != -1 else 0)

            cursor.execute("""
                SELECT hr_date_recorded, hr_height, hr_weight, hr_allergies, hr_notes
                FROM health_record WHERE stud_id = %s
                ORDER BY hr_date_recorded DESC LIMIT 1
            """, (stud_id,))
            hr = cursor.fetchone()
            if hr:
                hr_date_val = hr[0]
                if isinstance(hr_date_val, datetime.date):
                    self.hr_date_recorded.setDate(QDate(hr_date_val.year, hr_date_val.month, hr_date_val.day))
                else:
                    self.hr_date_recorded.setDate(QDate.fromString(str(hr_date_val), "yyyy-MM-dd"))
                self.hr_height.setText(f"{int(float(hr[1]))} cm" if hr[1] is not None else "")
                self.hr_weight.setText(f"{int(float(hr[2]))} kg" if hr[2] is not None else "")
                self.hr_allergies.setText(hr[3] if hr[3] else "")
                self.hr_notes.setPlainText(hr[4] if hr[4] else "")
            else:
                self.hr_date_recorded.setDate(QDate.currentDate())
                self.hr_height.setText("30 cm")
                self.hr_weight.setText("5 kg")
                self.hr_allergies.clear()
                self.hr_notes.clear()

            cursor.execute("""
                SELECT medhist_condition, medhist_diagnosis_date, medhist_notes, medhist_photo
                FROM medical_history WHERE stud_id = %s
                ORDER BY medhist_diagnosis_date DESC
            """, (stud_id,))
            medhist_rows = cursor.fetchall()
            self.medhist_table.setRowCount(0)
            for cond, diag_date, notes, photo in medhist_rows:
                row = self.medhist_table.rowCount()
                self.medhist_table.insertRow(row)
                self.medhist_table.setItem(row, 0, QTableWidgetItem(cond if cond else ""))
                dateedit = QDateEdit()
                dateedit.setCalendarPopup(True)
                if isinstance(diag_date, datetime.date):
                    dateedit.setDate(QDate(diag_date.year, diag_date.month, diag_date.day))
                else:
                    dateedit.setDate(QDate.fromString(str(diag_date), "yyyy-MM-dd"))
                self.medhist_table.setCellWidget(row, 1, dateedit)
                self.medhist_table.setItem(row, 2, QTableWidgetItem(notes if notes else ""))
                upload_btn = QPushButton("Upload Photo")
                if photo:
                    from tempfile import NamedTemporaryFile
                    temp_file = NamedTemporaryFile(delete=False, suffix='.png')
                    temp_file.write(photo)
                    temp_file.close()
                    pixmap = QPixmap(temp_file.name)
                    thumbnail = pixmap.scaled(32, 32, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    icon = QIcon(thumbnail)
                    upload_btn.setIcon(icon)
                    self.medhist_table.setItem(row, 3, QTableWidgetItem(temp_file.name))
                else:
                    self.medhist_table.setItem(row, 3, QTableWidgetItem(''))
                upload_btn.clicked.connect(lambda _, r=row: self.upload_photo_for_history(r))
                self.medhist_table.setCellWidget(row, 3, upload_btn)

            cursor.close()
            self.show_add_student()
            self.add_form_stack.setCurrentIndex(0)
            self.submit_button.setText("Update Student Info")
            try:
                self.submit_button.clicked.disconnect()
            except Exception:
                pass
            self.submit_button.clicked.connect(lambda: self.update_student(stud_id))
        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"Error loading student for editing:\n{e}")

    def update_student(self, stud_id):
        """
        Save changes to an existing student.
        """
        year_level_id = self.year_level_input_add.currentData()
        section_id = self.section_input_add.currentData()
        lrn_text = self.lrn_input.text().strip()
        if not lrn_text.isdigit():
            QMessageBox.warning(self, "Input Error", "LRN must be a numeric value.")
            return
        lrn = int(lrn_text)
        if year_level_id == -1 or section_id == -1:
            QMessageBox.warning(self, "Input Error", "Please select valid Year Level and Section.")
            return
        parent_full_name = self.parent_name_input.text().strip()
        parent_fname, parent_lname = "", ""
        if parent_full_name:
            names = parent_full_name.split()
            parent_fname = names[0]
            parent_lname = " ".join(names[1:]) if len(names) > 1 else ""

        hr_date = self.hr_date_recorded.date().toString("yyyy-MM-dd")
        hr_height = self.hr_height.value()
        hr_weight = self.hr_weight.value()
        hr_allergies = self.hr_allergies.text().strip()
        hr_notes = self.hr_notes.toPlainText().strip()

        medhist_data = []
        for row in range(self.medhist_table.rowCount()):
            cond_item = self.medhist_table.item(row, 0)
            cond = cond_item.text().strip() if cond_item else ""
            dateedit = self.medhist_table.cellWidget(row, 1)
            diag_date = dateedit.date().toString("yyyy-MM-dd") if dateedit else ""
            notes_item = self.medhist_table.item(row, 2)
            notes = notes_item.text().strip() if notes_item else ""
            photo_item = self.medhist_table.item(row, 3)
            photo_path = photo_item.text() if photo_item else ""
            photo_bytes = None
            if photo_path:
                try:
                    with open(photo_path, "rb") as f:
                        photo_bytes = f.read()
                except Exception:
                    photo_bytes = None
            if cond:
                medhist_data.append((cond, diag_date, notes, photo_bytes))
        try:
            cursor = self.conn.cursor()
            # Update student
            cursor.execute("""
                UPDATE student SET
                    stud_fname=%s, stud_mname=%s, stud_lname=%s, stud_DOB=%s, stud_gender=%s,
                    section_id=%s, year_level_id=%s, stud_email_add=%s,
                    stud_address=%s, stud_parent_fname=%s, stud_parent_lname=%s,
                    stud_parent_contnum=%s, stud_status=%s
                WHERE stud_id=%s
            """, (
                self.fname_input.text().strip(),
                self.mname_input.text().strip(),
                self.lname_input.text().strip(),
                self.dob_input.date().toString("yyyy-MM-dd"),
                self.gender_input.currentText(),
                section_id,
                year_level_id,
                self.email_input.text().strip(),
                self.address_input.text().strip(),
                parent_fname,
                parent_lname,
                self.parent_contact_input.text().strip(),
                self.status_input.currentText(),
                stud_id
            ))
            # Insert new health record (for simplicity)
            cursor.execute("""
                INSERT INTO health_record (
                    stud_id, hr_date_recorded, hr_height, hr_weight, hr_allergies, hr_notes, created_at, updated_at
                ) VALUES (%s, %s, %s, %s, %s, %s, NOW(), NOW())
            """, (stud_id, hr_date, hr_height, hr_weight, hr_allergies, hr_notes))
            # Remove old medical history and re-insert
            cursor.execute("DELETE FROM medical_history WHERE stud_id=%s", (stud_id,))
            for cond, diag_date, notes, photo_bytes in medhist_data:
                cursor.execute("""
                    INSERT INTO medical_history (
                        stud_id, medhist_condition, medhist_diagnosis_date, medhist_notes, medhist_photo, created_at, updated_at
                    ) VALUES (%s, %s, %s, %s, %s, NOW(), NOW())
                """, (stud_id, cond, diag_date, notes, photo_bytes))
            self.conn.commit()
            cursor.close()
            QMessageBox.information(self, "Success", f"Student info updated for LRN: {stud_id}")
            self.clear_form()
            self.lrn_input.setReadOnly(False)
            self.submit_button.setText("Submit Student Info")
            try:
                self.submit_button.clicked.disconnect()
            except Exception:
                pass
            self.submit_button.clicked.connect(self.submit_student)
            self.show_view_students()
        except psycopg2.errors.UniqueViolation:
            QMessageBox.warning(self, "Database Error",
                                "Email already exists. Please enter a unique email.")
            self.conn.rollback()
        except Exception as e:
            self.conn.rollback()
            QMessageBox.critical(self, "Database Error", f"An error occurred:\n{e}")

    def show_view_students(self):
        self.header.setText("View Students")
        # Show only the widgets relevant for viewing students
        self.filter_widget.show()
        self.view_students_button.show()
        self.students_table.show()
        # Hide other widgets if you have them
        if hasattr(self, 'form_widget'):
            self.form_scroll.hide()
        if hasattr(self, 'manage_widget'):
            self.manage_widget.hide()
        self.btn_switch_to_add.show()
        self.btn_switch_to_manage.show()
        self.btn_switch_to_view.hide()

    def show_add_student(self):
        self.header.setText("Add Student Info")
        self.clear_container()
        self.center_frame_layout.insertWidget(3, self.form_scroll)
        self.form_scroll.show()
        self.manage_widget.hide()
        self.filter_widget.hide()
        self.view_students_button.hide()
        self.btn_switch_to_add.hide()
        self.btn_switch_to_manage.show()
        self.btn_switch_to_view.show()
        self.load_year_level()
        self.load_sections_for_add_form()
        self.add_form_stack.setCurrentIndex(0)

    def show_manage_year_section(self):
        self.header.setText("Manage Year Level & Section")
        self.clear_container()
        self.center_frame_layout.insertWidget(3, self.manage_widget)
        self.manage_widget.show()
        self.form_scroll.hide()
        self.filter_widget.hide()
        self.view_students_button.hide()
        self.btn_switch_to_add.show()
        self.btn_switch_to_manage.hide()
        self.btn_switch_to_view.show()
        self.load_year_level()
        self.load_sections_for_manage()

    def clear_container(self):
        for i in range(3, self.center_frame_layout.count()):
            item = self.center_frame_layout.itemAt(i)
            if item.widget():
                item.widget().hide()

    def submit_student(self):
        year_level_id = self.year_level_input_add.currentData()
        section_id = self.section_input_add.currentData()
        lrn_text = self.lrn_input.text().strip()
        if not lrn_text.isdigit():
            QMessageBox.warning(self, "Input Error", "LRN must be a numeric value.")
            return
        lrn = int(lrn_text)
        if year_level_id == -1 or section_id == -1:
            QMessageBox.warning(self, "Input Error", "Please select valid Year Level and Section.")
            return
        parent_full_name = self.parent_name_input.text().strip()
        parent_fname, parent_lname = "", ""
        if parent_full_name:
            names = parent_full_name.split()
            parent_fname = names[0]
            parent_lname = " ".join(names[1:]) if len(names) > 1 else ""

        hr_date = self.hr_date_recorded.date().toString("yyyy-MM-dd")
        hr_height = self.hr_height.value()
        hr_weight = self.hr_weight.value()
        hr_allergies = self.hr_allergies.text().strip()
        hr_notes = self.hr_notes.toPlainText().strip()

        medhist_data = []
        for row in range(self.medhist_table.rowCount()):
            cond_item = self.medhist_table.item(row, 0)
            cond = cond_item.text().strip() if cond_item else ""
            dateedit = self.medhist_table.cellWidget(row, 1)
            diag_date = dateedit.date().toString("yyyy-MM-dd") if dateedit else ""
            notes_item = self.medhist_table.item(row, 2)
            notes = notes_item.text().strip() if notes_item else ""
            photo_item = self.medhist_table.item(row, 3)
            photo_path = photo_item.text() if photo_item else ""
            photo_bytes = None
            if photo_path:
                try:
                    with open(photo_path, "rb") as f:
                        photo_bytes = f.read()
                except Exception:
                    photo_bytes = None
            if cond:
                medhist_data.append((cond, diag_date, notes, photo_bytes))
        try:
            cursor = self.conn.cursor()
            # Insert student
            insert_query = """
                INSERT INTO student (
                    stud_id, stud_fname, stud_mname, stud_lname, stud_DOB, stud_gender,
                    section_id, year_level_id, stud_email_add,
                    stud_address, stud_parent_fname, stud_parent_lname, stud_parent_contnum, stud_status
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            data = (
                lrn,
                self.fname_input.text().strip(),
                self.mname_input.text().strip(),
                self.lname_input.text().strip(),
                self.dob_input.date().toString("yyyy-MM-dd"),
                self.gender_input.currentText(),
                section_id,
                year_level_id,
                self.email_input.text().strip(),
                self.address_input.text().strip(),
                parent_fname,
                parent_lname,
                self.parent_contact_input.text().strip(),
                self.status_input.currentText()
            )
            cursor.execute(insert_query, data)
            # Health record
            cursor.execute("""
                INSERT INTO health_record (
                    stud_id, hr_date_recorded, hr_height, hr_weight, hr_allergies, hr_notes, created_at, updated_at
                ) VALUES (%s, %s, %s, %s, %s, %s, NOW(), NOW())
            """, (lrn, hr_date, hr_height, hr_weight, hr_allergies, hr_notes))
            # Medical history
            for cond, diag_date, notes, photo_bytes in medhist_data:
                cursor.execute("""
                    INSERT INTO medical_history (
                        stud_id, medhist_condition, medhist_diagnosis_date, medhist_notes, medhist_photo, created_at, updated_at
                    ) VALUES (%s, %s, %s, %s, %s, NOW(), NOW())
                """, (lrn, cond, diag_date, notes, photo_bytes))
            self.conn.commit()
            cursor.close()
            QMessageBox.information(self, "Success", f"Student info submitted!\nAssigned LRN: {lrn}")
            self.clear_form()
            self.show_view_students()
        except psycopg2.errors.UniqueViolation:
            QMessageBox.warning(self, "Database Error",
                                "LRN or email already exists. Please enter a unique LRN and email.")
            self.conn.rollback()
        except Exception as e:
            self.conn.rollback()
            QMessageBox.critical(self, "Database Error", f"An error occurred:\n{e}")

    def clear_form(self):
        self.lrn_input.clear()
        self.fname_input.clear()
        self.lname_input.clear()
        self.dob_input.setDate(QDate.currentDate())
        self.gender_input.setCurrentIndex(0)
        self.year_level_input_add.setCurrentIndex(0)
        self.section_input_add.setCurrentIndex(0)
        self.email_input.clear()
        self.address_input.clear()
        self.parent_name_input.clear()
        self.parent_contact_input.clear()
        self.status_input.setCurrentIndex(0)
        self.hr_date_recorded.setDate(QDate.currentDate())
        self.hr_height.setValue(30)
        self.hr_weight.setValue(5)
        self.hr_allergies.clear()
        self.hr_notes.clear()
        self.medhist_table.setRowCount(0)

    def add_year_level(self):
        name = self.year_level_name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Input Error", "Please enter a year level name.")
            return
        try:
            cursor = self.conn.cursor()
            cursor.execute("INSERT INTO year_level (year_level_name) VALUES (%s)", (name,))
            self.conn.commit()
            cursor.close()
            QMessageBox.information(self, "Success", f"Year Level '{name}' added successfully.")
            self.year_level_name_input.clear()
            self.load_year_level()
        except psycopg2.errors.UniqueViolation:
            QMessageBox.warning(self, "Database Error", "This Year Level already exists.")
            self.conn.rollback()
        except Exception as e:
            self.conn.rollback()
            QMessageBox.critical(self, "Database Error", f"An error occurred:\n{e}")

    def add_section(self):
        year_level_id = self.section_year_level_combo.currentData()
        name = self.section_name_input.text().strip()
        if year_level_id == -1 or year_level_id is None:
            QMessageBox.warning(self, "Input Error", "Please select a valid Year Level for the section.")
            return
        if not name:
            QMessageBox.warning(self, "Input Error", "Please enter a section name.")
            return
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "INSERT INTO section (section_name, year_level_id) VALUES (%s, %s)",
                (name, year_level_id)
            )
            self.conn.commit()
            cursor.close()
            QMessageBox.information(self, "Success", f"Section '{name}' added successfully.")
            self.section_name_input.clear()
            self.load_sections_for_manage()
        except psycopg2.errors.UniqueViolation:
            QMessageBox.warning(self, "Database Error", "This Section already exists for the selected Year Level.")
            self.conn.rollback()
        except Exception as e:
            self.conn.rollback()
            QMessageBox.critical(self, "Database Error", f"An error occurred:\n{e}")

    def load_sections_for_selected_year_level(self, item):
        try:
            id_str = item.text().split(":")[0].strip()
            year_level_id = int(id_str)
        except Exception:
            year_level_id = None
        if year_level_id is None:
            return
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "SELECT section_id, section_name FROM section WHERE year_level_id = %s ORDER BY section_name",
                (year_level_id,))
            rows = cursor.fetchall()
            cursor.close()
            self.section_list.clear()
            for sec_id, sec_name in rows:
                self.section_list.addItem(f"{sec_id}: {sec_name}")
        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"An error occurred loading sections:\n{e}")

    def load_sections_for_manage(self):
        if not self.conn:
            return
        cursor = self.conn.cursor()
        cursor.execute("SELECT section_id, section_name FROM section ORDER BY section_name")
        rows = cursor.fetchall()
        self.section_list.clear()
        for _id, name in rows:
            self.section_list.addItem(f"{_id}: {name}")
        cursor.close()


class CmLineEdit(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setValidator(QIntValidator(0, 999, self))
        self._updating = False
        self.textChanged.connect(self._add_suffix)
        self.setAlignment(Qt.AlignLeft)

    def _add_suffix(self, text):
        if self._updating:
            return
        self._updating = True
        # Remove ' cm' if it exists
        clean = text.replace(' cm', '').strip()
        if clean:
            self.setText(f"{clean} cm")
            # Move cursor just before the space
            self.setCursorPosition(len(clean))
        else:
            self.setText('')
        self._updating = False

    def value(self):
        """Returns the int value (or None if empty)"""
        text = self.text().replace(' cm', '').strip()
        return int(text) if text.isdigit() else None


class KgLineEdit(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setValidator(QIntValidator(0, 999, self))
        self._updating = False
        self.textChanged.connect(self._add_suffix)
        self.setAlignment(Qt.AlignLeft)

    def _add_suffix(self, text):
        if self._updating:
            return
        self._updating = True
        # Remove ' kg' if it exists
        clean = text.replace(' kg', '').strip()
        if clean:
            self.setText(f"{clean} kg")
            # Move cursor just before the space
            self.setCursorPosition(len(clean))
        else:
            self.setText('')
        self._updating = False



    def to_str_if_date(val):
        if isinstance(val, datetime.date):
            return val.strftime('%Y-%m-%d')
        return str(val)

    def value(self):
        """Returns the int value (or None if empty)"""
        text = self.text().replace(' kg', '').strip()
        return int(text) if text.isdigit() else None

    class CmLineEdit(QLineEdit):
        def __init__(self, parent=None):
            super().__init__(parent)
            self.setValidator(QIntValidator(0, 999, self))
            self._updating = False
            self.textChanged.connect(self._add_suffix)
            self.setAlignment(Qt.AlignLeft)

        def _add_suffix(self, text):
            if self._updating:
                return
            self._updating = True
            clean = text.replace(' cm', '').strip()
            if clean:
                self.setText(f"{clean} cm")
                self.setCursorPosition(len(clean))
            else:
                self.setText('')
            self._updating = False

        def value(self):
            text = self.text().replace(' cm', '').strip()
            return int(text) if text.isdigit() else None

        def setValue(self, val):
            # Accepts int or str, sets text with 'cm' suffix if valid
            if val is None or val == "":
                self.setText('')
            else:
                self.setText(f"{val} cm")

    class KgLineEdit(QLineEdit):
        def __init__(self, parent=None):
            super().__init__(parent)
            self.setValidator(QIntValidator(0, 999, self))
            self._updating = False
            self.textChanged.connect(self._add_suffix)
            self.setAlignment(Qt.AlignLeft)

        def _add_suffix(self, text):
            if self._updating:
                return
            self._updating = True
            clean = text.replace(' kg', '').strip()
            if clean:
                self.setText(f"{clean} kg")
                self.setCursorPosition(len(clean))
            else:
                self.setText('')
            self._updating = False

        def value(self):
            text = self.text().replace(' kg', '').strip()
            return int(text) if text.isdigit() else None

        def setValue(self, val):
            # Accepts int or str, sets text with 'kg' suffix if valid
            if val is None or val == "":
                self.setText('')
            else:
                self.setText(f"{val} kg")
