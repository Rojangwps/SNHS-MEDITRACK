# clinic_system.py

from PyQt5.QtWidgets import QWidget, QPushButton, QVBoxLayout, QFormLayout, QLineEdit, QLabel, QComboBox, \
    QTableWidget, QTableWidgetItem, QHBoxLayout, QMessageBox
from PyQt5.QtCore import Qt


class SchoolClinicSystem(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('School Clinic System')
        self.setGeometry(100, 100, 600, 400)

        # Create Buttons for different actions
        self.register_patient_button = QPushButton('Register Patient')
        self.register_patient_button.clicked.connect(self.register_patient)

        self.schedule_appointment_button = QPushButton('Schedule Appointment')
        self.schedule_appointment_button.clicked.connect(self.schedule_appointment)

        self.view_medical_history_button = QPushButton('View Medical History')
        self.view_medical_history_button.clicked.connect(self.view_medical_history)

        # Create layout and add buttons
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        layout.addWidget(self.register_patient_button)
        layout.addWidget(self.schedule_appointment_button)
        layout.addWidget(self.view_medical_history_button)

        self.setLayout(layout)

    def register_patient(self):
        self.patient_dialog = PatientRegistrationDialog(self)
        self.patient_dialog.exec_()

    def schedule_appointment(self):
        self.appointment_dialog = AppointmentSchedulingDialog(self)
        self.appointment_dialog.exec_()

    def view_medical_history(self):
        self.medical_history_dialog = MedicalHistoryDialog(self)
        self.medical_history_dialog.exec_()


class PatientRegistrationDialog(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Register Patient')
        self.setGeometry(150, 150, 400, 250)

        # Patient registration form layout
        self.name_label = QLabel('Name:')
        self.name_input = QLineEdit()

        self.age_label = QLabel('Age:')
        self.age_input = QLineEdit()

        self.gender_label = QLabel('Gender:')
        self.gender_combo = QComboBox()
        self.gender_combo.addItems(["Male", "Female", "Other"])

        self.register_button = QPushButton('Register')
        self.register_button.clicked.connect(self.register_patient)

        layout = QFormLayout()
        layout.addRow(self.name_label, self.name_input)
        layout.addRow(self.age_label, self.age_input)
        layout.addRow(self.gender_label, self.gender_combo)
        layout.addWidget(self.register_button)

        self.setLayout(layout)

    def register_patient(self):
        name = self.name_input.text()
        age = self.age_input.text()
        gender = self.gender_combo.currentText()

        if name and age and gender:
            QMessageBox.information(self, 'Success', f'{name} registered successfully!')
            self.close()
        else:
            QMessageBox.warning(self, 'Error', 'Please fill in all fields.')


class AppointmentSchedulingDialog(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Schedule Appointment')
        self.setGeometry(150, 150, 400, 250)

        # Appointment form layout
        self.patient_label = QLabel('Patient Name:')
        self.patient_input = QLineEdit()

        self.date_label = QLabel('Appointment Date:')
        self.date_input = QLineEdit()

        self.time_label = QLabel('Appointment Time:')
        self.time_input = QLineEdit()

        self.schedule_button = QPushButton('Schedule Appointment')
        self.schedule_button.clicked.connect(self.schedule_appointment)

        layout = QFormLayout()
        layout.addRow(self.patient_label, self.patient_input)
        layout.addRow(self.date_label, self.date_input)
        layout.addRow(self.time_label, self.time_input)
        layout.addWidget(self.schedule_button)

        self.setLayout(layout)

    def schedule_appointment(self):
        patient = self.patient_input.text()
        date = self.date_input.text()
        time = self.time_input.text()

        if patient and date and time:
            QMessageBox.information(self, 'Success', f'Appointment for {patient} scheduled!')
            self.close()
        else:
            QMessageBox.warning(self, 'Error', 'Please fill in all fields.')


class MedicalHistoryDialog(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Medical History')
        self.setGeometry(150, 150, 600, 300)

        # Table to view medical history
        self.history_table = QTableWidget(self)
        self.history_table.setRowCount(5)  # Set 5 rows (can be dynamic)
        self.history_table.setColumnCount(3)  # Name, Age, Last Appointment
        self.history_table.setHorizontalHeaderLabels(['Patient Name', 'Age', 'Last Appointment'])

        # Fill table with example data
        self.history_table.setItem(0, 0, QTableWidgetItem("John Doe"))
        self.history_table.setItem(0, 1, QTableWidgetItem("15"))
        self.history_table.setItem(0, 2, QTableWidgetItem("2025-04-15"))

        layout = QVBoxLayout()
        layout.addWidget(self.history_table)

        self.setLayout(layout)
