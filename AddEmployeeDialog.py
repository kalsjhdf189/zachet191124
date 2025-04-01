from PySide6.QtWidgets import (
    QDialog, QLineEdit, QHBoxLayout, QFormLayout, QVBoxLayout, QPushButton, QComboBox
)
from datebase import Connect, Employee, Department, Duty
from PySide6.QtCore import QDate

class AddEmployeeDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.session = Connect.create_connection()
        self.setWindowTitle("Добавить сотрудника")
        
        form_layout = QFormLayout()

        self.first_name_input = QLineEdit()
        self.middle_name_input = QLineEdit()
        self.last_name_input = QLineEdit()
        
        self.duty_combo = QComboBox()
        self.load_duties()
        
        self.department_combo = QComboBox()
        self.load_departments()
        
        self.date_in_input = QLineEdit()
        self.date_in_input.setPlaceholderText("ГГГГ-ММ-ДД")

        form_layout.addRow("Имя:", self.first_name_input)
        form_layout.addRow("Отчество:", self.middle_name_input)
        form_layout.addRow("Фамилия:", self.last_name_input)
        form_layout.addRow("Должность:", self.duty_combo)
        form_layout.addRow("Отдел:", self.department_combo)
        form_layout.addRow("Дата приема:", self.date_in_input)

        save_button = QPushButton("Сохранить")
        save_button.clicked.connect(self.save_new_employee)
        cancel_button = QPushButton("Отмена")
        cancel_button.clicked.connect(self.reject)

        button_layout = QHBoxLayout()
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)

        main_layout = QVBoxLayout()
        main_layout.addLayout(form_layout)
        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)

    def load_duties(self):
        duties = self.session.query(Duty).all()
        for duty in duties:
            self.duty_combo.addItem(duty.duty_name, duty.id)

    def load_departments(self):
        departments = self.session.query(Department).all()
        for department in departments:
            self.department_combo.addItem(department.department_name, department.id)

    def save_new_employee(self):
        first_name = self.first_name_input.text().strip()
        middle_name = self.middle_name_input.text().strip()
        last_name = self.last_name_input.text().strip()
        id_duty = self.duty_combo.currentData()
        id_department = self.department_combo.currentData()
        date_in_text = self.date_in_input.text().strip()
        
        date_in = QDate.fromString(date_in_text, "yyyy-MM-dd").toPython() if date_in_text else None

        if first_name and last_name and id_duty and id_department and date_in:
            new_employee = Employee(
                first_name=first_name,
                middle_name=middle_name,
                last_name=last_name,
                id_duty=id_duty,
                id_department=id_department,
                date_in=date_in
            )
            self.session.add(new_employee)
            self.session.commit()
            self.accept()
