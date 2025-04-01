from PySide6.QtWidgets import (
    QDialog, QLineEdit, QHBoxLayout, QFormLayout, QVBoxLayout, QPushButton, QComboBox
)
from PySide6.QtCore import QDate
from datebase import Connect, Department, Duty, Employee

class EditEmployeeDialog(QDialog):
    def __init__(self, employee, parent=None):
        super().__init__(parent)
        self.session = Connect.create_connection()
        self.employee = employee
        self.setWindowTitle("Редактировать сотрудника")
        
        form_layout = QFormLayout()

        self.last_name_input = QLineEdit(employee.last_name)
        self.first_name_input = QLineEdit(employee.first_name)
        self.middle_name_input = QLineEdit(employee.middle_name)
        
        self.duty_combo = QComboBox()
        self.department_combo = QComboBox()
        
        self.date_in_input = QLineEdit()
        self.date_in_input.setPlaceholderText("ГГГГ-ММ-ДД")
        if employee.date_in:
            self.date_in_input.setText(employee.date_in.strftime("%Y-%m-%d"))
        
        self.load_duties()
        self.load_departments()
        
        self.duty_combo.setCurrentText(employee.duty_rel.duty_name)
        self.department_combo.setCurrentText(employee.dep_rel.department_name)

        form_layout.addRow("Фамилия:", self.last_name_input)
        form_layout.addRow("Имя:", self.first_name_input)
        form_layout.addRow("Отчество:", self.middle_name_input)
        form_layout.addRow("Должность:", self.duty_combo)
        form_layout.addRow("Отдел:", self.department_combo)
        form_layout.addRow("Дата приема:", self.date_in_input)

        save_button = QPushButton("Сохранить")
        save_button.clicked.connect(self.save_changes)
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

    def save_changes(self):
        last_name = self.last_name_input.text().strip()
        first_name = self.first_name_input.text().strip()
        middle_name = self.middle_name_input.text().strip()
        selected_duty_id = self.duty_combo.currentData()
        selected_department_id = self.department_combo.currentData()
        date_in_text = self.date_in_input.text().strip()
        
        date_in = QDate.fromString(date_in_text, "yyyy-MM-dd").toPython() if date_in_text else None

        if last_name and first_name and selected_duty_id and selected_department_id:
            self.employee.last_name = last_name
            self.employee.first_name = first_name
            self.employee.middle_name = middle_name
            self.employee.id_duty = selected_duty_id
            self.employee.id_department = selected_department_id
            self.employee.date_in = date_in
            
            self.session.commit()
            self.accept()