from datetime import date
from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QPushButton, QLineEdit, QComboBox
from PySide6.QtGui import QIcon
from datebase import Guest, Connect
from tkinter import messagebox

class SecondWindow(QMainWindow):
    def __init__(self, main_window):
        super(SecondWindow, self).__init__()
        self.main_window = main_window
        self.setWindowTitle("Добавление данных")
        self.setWindowIcon(QIcon('7603391.png'))
        self.setStyleSheet("QWidget {background-color: white}")
        self.setGeometry(100, 100, 400, 400)

        self.session = Connect.create_connection()

        layout = QVBoxLayout()

        self.client_id_input = QLineEdit(self)
        self.client_id_input.setPlaceholderText("id")
        self.client_f_input = QLineEdit(self)
        self.client_f_input.setPlaceholderText("Фамилия")
        self.client_i_input = QLineEdit(self)
        self.client_i_input.setPlaceholderText("Имя")
        self.client_o_input = QLineEdit(self)
        self.client_o_input.setPlaceholderText("Отчество")
        self.client_burth_input = QLineEdit(self)
        self.client_burth_input.setPlaceholderText("Дата рождения (YYYY-MM-DD)")
        self.client_numerphone_input = QLineEdit(self)
        self.client_numerphone_input.setPlaceholderText("Номер телефона")
        
        self.gender_combobox = QComboBox()
        self.gender_combobox.addItems(["Мужской", "Женский"])

        self.add_button = QPushButton("Добавить Клиента")
        self.add_button.clicked.connect(self.add_client)

        layout.addWidget(self.client_id_input)
        layout.addWidget(self.client_f_input)
        layout.addWidget(self.client_i_input)
        layout.addWidget(self.client_o_input)
        layout.addWidget(self.client_numerphone_input)
        layout.addWidget(self.client_burth_input)
        layout.addWidget(self.gender_combobox)
        layout.addWidget(self.add_button)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def add_client(self):
        client_id = self.client_id_input.text()
        client_f = self.client_f_input.text()
        client_i = self.client_i_input.text()
        client_o = self.client_o_input.text()
        client_numerphone = self.client_numerphone_input.text()
        client_burth = self.client_burth_input.text()
        selected_gender = self.gender_combobox.currentText()  # Получаем текст

        # Создание нового клиента
        new_client = Guest(
            id=client_id,
            last_name=client_f,
            first_name=client_i,
            middle_name=client_o,
            birth_date=client_burth,
            phone=client_numerphone,
            gender=selected_gender,
        )

        self.session.add(new_client)
        self.session.commit()

        messagebox.showinfo("Успех", "Клиент успешно добавлен!")
        
        # Обновление таблицы в главном окне
        self.main_window.switchToTable(self.main_window, "__guest")

        self.close()