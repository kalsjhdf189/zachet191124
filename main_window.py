import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QTableWidget, QTableWidgetItem, 
    QMessageBox, QDialog, QLineEdit, QComboBox, QHBoxLayout, QFormLayout
)
from PySide6.QtGui import QIcon
from datebase import Connect, Movement, Product  # Импорты из вашего файла с моделями

class AddProductDialog(QDialog):
    def __init__(self, session, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Добавить товар")
        self.setWindowIcon(QIcon('icon.ico'))  # Устанавливаем иконку окна

        self.session = session
        
        form_layout = QFormLayout()

        # Поля для ввода данных о товаре
        self.name_input = QLineEdit()
        self.quantity_input = QLineEdit()
        self.price_input = QLineEdit()
        self.location_input = QLineEdit()

        form_layout.addRow("Название товара:", self.name_input)
        form_layout.addRow("Количество:", self.quantity_input)
        form_layout.addRow("Цена:", self.price_input)
        form_layout.addRow("Местоположение:", self.location_input)

        add_button = QPushButton("Добавить товар")
        add_button.clicked.connect(self.add_product)

        cancel_button = QPushButton("Отмена")
        cancel_button.clicked.connect(self.reject)

        button_layout = QHBoxLayout()
        button_layout.addWidget(add_button)
        button_layout.addWidget(cancel_button)

        main_layout = QVBoxLayout()
        main_layout.addLayout(form_layout)
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

    def add_product(self):
        name = self.name_input.text().strip()
        try:
            quantity = int(self.quantity_input.text())
            price = float(self.price_input.text())
        except ValueError:
            QMessageBox.warning(self, "Ошибка", "Некорректные значения для количества или цены.")
            return
        location = self.location_input.text().strip()
        
        # Добавление товара в БД
        new_product = Product(name=name, quantity=quantity, price=price, location=location)
        self.session.add(new_product)
        self.session.commit()
        
        # Закрыть диалоговое окно
        self.accept()


class MoveProductDialog(QDialog):
    def __init__(self, session, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Переместить товар")
        self.setWindowIcon(QIcon('icon.ico'))  # Устанавливаем иконку окна
        
        self.session = session

        form_layout = QFormLayout()

        # Загрузка списка товаров из базы данных
        self.product_select = QComboBox()
        products = self.session.query(Product).all()
        self.product_select.addItems([product.name for product in products])

        self.move_quantity_input = QLineEdit()
        self.from_location_input = QLineEdit()
        self.to_location_input = QLineEdit()

        form_layout.addRow("Выберите товар:", self.product_select)
        form_layout.addRow("Количество для перемещения:", self.move_quantity_input)
        form_layout.addRow("Откуда:", self.from_location_input)
        form_layout.addRow("Куда:", self.to_location_input)

        move_button = QPushButton("Переместить товар")
        move_button.clicked.connect(self.move_product)

        cancel_button = QPushButton("Отмена")
        cancel_button.clicked.connect(self.reject)

        button_layout = QHBoxLayout()
        button_layout.addWidget(move_button)
        button_layout.addWidget(cancel_button)

        main_layout = QVBoxLayout()
        main_layout.addLayout(form_layout)
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

    def move_product(self):
        product_name = self.product_select.currentText()
        product = self.session.query(Product).filter(Product.name == product_name).first()
        
        try:
            quantity = int(self.move_quantity_input.text())
        except ValueError:
            QMessageBox.warning(self, "Ошибка", "Введите корректное количество для перемещения.")
            return
        
        from_location = self.from_location_input.text().strip()
        to_location = self.to_location_input.text().strip()

        if product.quantity < quantity:
            QMessageBox.warning(self, "Ошибка", "Недостаточно товара на складе для перемещения.")
            return

        # Создание записи о перемещении товара
        movement = Movement(
            product_id=product.id, 
            quantity=quantity, 
            from_location=from_location, 
            to_location=to_location
        )
        self.session.add(movement)

        # Обновление количества товара
        product.quantity -= quantity
        self.session.commit()

        self.accept()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Учет товаров на складе")
        self.setWindowIcon(QIcon('icon.ico'))  # Устанавливаем иконку окна
        self.setGeometry(100, 100, 800, 600)

        # Создание соединения с БД
        self.session = Connect.create_connection()

        # Основной layout
        layout = QVBoxLayout()

        # Форма для добавления товара
        self.add_product_button = QPushButton("Добавить товар")
        self.add_product_button.clicked.connect(self.open_add_product_dialog)
        layout.addWidget(self.add_product_button)

        # Кнопка для перемещения товара
        self.move_product_button = QPushButton("Переместить товар")
        self.move_product_button.clicked.connect(self.open_move_product_dialog)
        layout.addWidget(self.move_product_button)

        # Таблица для отображения перемещений товара
        self.history_table(layout)

        # Кнопка для удаления выбранного перемещения
        self.delete_button = QPushButton("Удалить выбранное перемещение")
        self.delete_button.clicked.connect(self.delete_selected_movement)
        layout.addWidget(self.delete_button)

        # Основной виджет
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def open_add_product_dialog(self):
        dialog = AddProductDialog(self.session, self)
        if dialog.exec() == QDialog.Accepted:
            self.refresh_history()

    def open_move_product_dialog(self):
        dialog = MoveProductDialog(self.session, self)
        if dialog.exec() == QDialog.Accepted:
            self.refresh_history()

    def history_table(self, layout):
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(4)  # Убираем столбец для кнопки удаления
        self.history_table.setHorizontalHeaderLabels(["Товар", "Откуда", "Куда", "Количество"])
        layout.addWidget(self.history_table)

        self.refresh_history()

    def refresh_history(self):
        movements = self.session.query(Movement).all()
        self.history_table.setRowCount(len(movements))

        for row_idx, movement in enumerate(movements):
            self.history_table.setItem(row_idx, 0, QTableWidgetItem(movement.product.name))
            self.history_table.setItem(row_idx, 1, QTableWidgetItem(movement.from_location))
            self.history_table.setItem(row_idx, 2, QTableWidgetItem(movement.to_location))
            self.history_table.setItem(row_idx, 3, QTableWidgetItem(str(movement.quantity)))

    def delete_selected_movement(self):
        selected_row = self.history_table.currentRow()  # Получаем выбранную строку

        if selected_row == -1:  # Проверка, выбрана ли строка
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, выберите перемещение для удаления.")
            return

        # Получаем ID перемещения из выбранной строки
        movement_id = self.session.query(Movement).all()[selected_row].id
        movement_to_delete = self.session.query(Movement).filter(Movement.id == movement_id).first()

        # Удаляем запись о перемещении из базы данных
        self.session.delete(movement_to_delete)
        self.session.commit()

        # Обновляем таблицу
        self.refresh_history()