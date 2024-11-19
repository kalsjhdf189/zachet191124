from PySide6.QtWidgets import QMainWindow, QPushButton, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget, QHBoxLayout, QMessageBox, QInputDialog
from PySide6.QtGui import QIcon
from datebase import Connect, Product, Movement

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Система учета инвентаря")
        self.setWindowIcon(QIcon("resources/icon.png"))

        # Основной виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.session = Connect.create_connection()

        # Кнопки управления
        self.add_button = QPushButton("Добавить товар")
        self.move_button = QPushButton("Переместить товар")
        self.delete_button = QPushButton("Удалить товар")
        self.history_button = QPushButton("Показать историю")

        self.add_button.clicked.connect(self.add_product)
        self.move_button.clicked.connect(self.move_product)
        self.delete_button.clicked.connect(self.delete_product)
        self.history_button.clicked.connect(self.show_history)

        # Верхняя панель с кнопками
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.move_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addWidget(self.history_button)

        # Таблица для отображения данных
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "Название", "Количество", "Локация"])

        # Основной макет
        layout = QVBoxLayout()
        layout.addLayout(button_layout)
        layout.addWidget(self.table)
        central_widget.setLayout(layout)
        self.refresh_table()

    def add_product(self):
        """Добавление нового товара."""
        name, ok1 = QInputDialog.getText(self, "Добавить товар", "Введите название товара:")
        if not ok1 or not name:
            return

        quantity, ok2 = QInputDialog.getInt(self, "Добавить товар", "Введите количество товара:", min=1)
        if not ok2:
            return

        price, ok3 = QInputDialog.getDouble(self, "Добавить товар", "Введите цену товара:", min=0.01)
        if not ok3:
            return

        location, ok4 = QInputDialog.getText(self, "Добавить товар", "Введите местоположение товара:")
        if not ok4 or not location:
            return

        # Сохранение товара в базу данных
        product = Product(name=name, quantity=quantity, price=price, location=location)
        self.session.add(product)
        self.session.commit()
        QMessageBox.information(self, "Успех", f"Товар '{name}' добавлен.")
        self.refresh_table()

    def move_product(self):
        """Перемещение товара между складами."""
        # Получение списка товаров
        products = self.session.query(Product).all()
        if not products:
            QMessageBox.warning(self, "Ошибка", "Нет товаров для перемещения.")
            return

        product_names = [f"{p.id}: {p.name} (Количество: {p.quantity}, Локация: {p.location})" for p in products]
        product_choice, ok1 = QInputDialog.getItem(self, "Перемещение товара", "Выберите товар:", product_names, editable=False)
        if not ok1:
            return

        product_id = int(product_choice.split(":")[0])
        product = self.session.query(Product).get(product_id)

        quantity, ok2 = QInputDialog.getInt(self, "Перемещение товара", "Введите количество для перемещения:", min=1, max=product.quantity)
        if not ok2:
            return

        new_location, ok3 = QInputDialog.getText(self, "Перемещение товара", "Введите новое местоположение:")
        if not ok3 or not new_location:
            return

        # Сохранение перемещения в базу данных
        movement = Movement(product_id=product.id, from_location=product.location, to_location=new_location, quantity=quantity)
        self.session.add(movement)

        # Обновление количества и местоположения товара
        product.quantity -= quantity
        if product.quantity == 0:
            product.location = new_location
        self.session.commit()
        QMessageBox.information(self, "Успех", f"Товар '{product.name}' перемещен в '{new_location}'.")
        self.refresh_table()

    def delete_product(self):
        """Удаление товара."""
        # Получение списка товаров
        products = self.session.query(Product).all()
        if not products:
            QMessageBox.warning(self, "Ошибка", "Нет товаров для удаления.")
            return

        product_names = [f"{p.id}: {p.name}" for p in products]
        product_choice, ok = QInputDialog.getItem(self, "Удалить товар", "Выберите товар:", product_names, editable=False)
        if not ok:
            return

        product_id = int(product_choice.split(":")[0])
        product = self.session.query(Product).get(product_id)

        # Удаление товара
        self.session.delete(product)
        self.session.commit()
        QMessageBox.information(self, "Успех", f"Товар '{product.name}' удален.")
        self.refresh_table()

    def show_history(self):
        """Показать историю перемещений."""
        movements = self.session.query(Movement).all()
        if not movements:
            QMessageBox.information(self, "История", "История перемещений пуста.")
            return

        # Заполнение таблицы историей перемещений
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "Товар", "Из", "В", "Количество"])
        self.table.setRowCount(len(movements))

        for row_idx, movement in enumerate(movements):
            product = self.session.query(Product).get(movement.product_id)
            product_name = product.name if product else "Удалено"  # Обрабатываем случай удаления товара
            self.table.setItem(row_idx, 0, QTableWidgetItem(str(movement.id)))
            self.table.setItem(row_idx, 1, QTableWidgetItem(product_name))
            self.table.setItem(row_idx, 2, QTableWidgetItem(movement.from_location))
            self.table.setItem(row_idx, 3, QTableWidgetItem(movement.to_location))
            self.table.setItem(row_idx, 4, QTableWidgetItem(str(movement.quantity)))

    def refresh_table(self):
        """Обновление таблицы товаров."""
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "Название", "Количество", "Локация"])
        products = self.session.query(Product).all()
        self.table.setRowCount(len(products))

        for row_idx, product in enumerate(products):
            self.table.setItem(row_idx, 0, QTableWidgetItem(str(product.id)))
            self.table.setItem(row_idx, 1, QTableWidgetItem(product.name))
            self.table.setItem(row_idx, 2, QTableWidgetItem(str(product.quantity)))
            self.table.setItem(row_idx, 3, QTableWidgetItem(product.location))
