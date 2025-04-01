from PySide6.QtWidgets import (
    QMainWindow, QVBoxLayout, QWidget, QTableWidget, QTableWidgetItem, 
    QComboBox, QHBoxLayout, QPushButton, QLineEdit
)

from datebase import Connect, Employee, Department, EmployeeSkill, Skill
from AddEmployeeDialog import AddEmployeeDialog
from EditEmployeeDialog import EditEmployeeDialog

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.session = Connect.create_connection()
        self.setWindowTitle("Сотрудники")
        self.setGeometry(100, 100, 800, 600)

        layout = QVBoxLayout()
        filter_layout = QHBoxLayout()

        self.department_filter = QComboBox()
        self.department_filter.addItem("Все", None)
        self.load_departments()
        self.department_filter.currentIndexChanged.connect(self.filter_history)
        filter_layout.addWidget(self.department_filter)
        
        self.skill_search = QLineEdit()
        self.skill_search.setPlaceholderText("Поиск по навыкам...")
        self.skill_search.textChanged.connect(self.filter_history)
        filter_layout.addWidget(self.skill_search)

        layout.addLayout(filter_layout)

        self.history_table = QTableWidget()
        self.history_table.setColumnCount(6)
        self.history_table.setHorizontalHeaderLabels([
            "Фамилия", "Имя", "Отчество", "Должность", "Отдел", "Список навыков"
        ])
        layout.addWidget(self.history_table)

        self.refresh_history()
        
        self.add_employee_button = QPushButton("Добавить сотрудника")
        self.add_employee_button.clicked.connect(self.open_add_employee_dialog)
        layout.addWidget(self.add_employee_button)
        
        self.edit_employee_button = QPushButton("Редактировать сотрудника")
        self.edit_employee_button.clicked.connect(self.open_edit_employee_dialog)
        layout.addWidget(self.edit_employee_button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def load_departments(self):
        departments = self.session.query(Department).all()
        for department in departments:
            self.department_filter.addItem(department.department_name, department.id)

    def refresh_history(self):
        selected_department_id = self.department_filter.currentData()
        search_skill = self.skill_search.text().strip().lower()
        
        
        query = self.session.query(Employee)
        

        if selected_department_id:
            query = query.filter(Employee.id_department == selected_department_id)
            
        if search_skill:
            query = query.join(EmployeeSkill).join(Skill).filter(Skill.skill_name.ilike(f"%{search_skill}%"))

        employees = query.all()
        self.history_table.setRowCount(len(employees))

        for row_idx, employee in enumerate(employees):
            self.history_table.setItem(row_idx, 0, QTableWidgetItem(employee.last_name))
            self.history_table.setItem(row_idx, 1, QTableWidgetItem(employee.first_name))
            self.history_table.setItem(row_idx, 2, QTableWidgetItem(employee.middle_name))
            self.history_table.setItem(row_idx, 3, QTableWidgetItem(employee.duty_rel.duty_name))
            self.history_table.setItem(row_idx, 4, QTableWidgetItem(employee.dep_rel.department_name))
            
            skills = self.session.query(EmployeeSkill).filter(EmployeeSkill.id_employee == employee.id).all()

            skill_list = ""
            for skill in skills:
                skill_list += str(skill.skill_rel.skill_name) + " "

            self.history_table.setItem(row_idx, 5, QTableWidgetItem(skill_list))

    def filter_history(self):
        self.refresh_history()

    def open_add_employee_dialog(self):
        dialog = AddEmployeeDialog(self)
        if dialog.exec():
            self.refresh_history()
            
    def open_edit_employee_dialog(self):
        current_row = self.history_table.currentRow()
        if current_row >= 0:
            employee_id = self.session.query(Employee).all()[current_row].id
            employee = self.session.query(Employee).filter(Employee.id == employee_id).first()
            if employee:
                dialog = EditEmployeeDialog(employee, self)
                if dialog.exec():
                    self.refresh_history()