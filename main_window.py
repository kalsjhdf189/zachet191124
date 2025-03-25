from PySide6.QtWidgets import (
    QMainWindow, QPushButton, QVBoxLayout, QWidget, QTableWidget, QTableWidgetItem, 
    QLineEdit, QLabel, QComboBox, QHBoxLayout, QDialog
)
from add_movement_dialog import AddMovementDialog
from edit_movement_dialog import EditMovementDialog
from datebase import Connect, Movement, Product

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.session = Connect.create_connection()
        self.setWindowTitle("Учет товаров на складе")
        self.setGeometry(100, 100, 800, 600)

        layout = QVBoxLayout()

        filter_layout = QHBoxLayout()
        
        self.search_input = QLineEdit()
        self.search_input.textChanged.connect(self.filter_history)
        filter_layout.addWidget(self.search_input)

        self.product_filter = QComboBox()
        self.product_filter.addItem("Все товары", None)
        self.load_products()
        self.product_filter.currentIndexChanged.connect(self.filter_history)
        filter_layout.addWidget(self.product_filter)

        layout.addLayout(filter_layout)

        self.add_product_button = QPushButton("Добавить перемещение")
        self.add_product_button.clicked.connect(self.open_add_movement_dialog)
        layout.addWidget(self.add_product_button)
        
        self.edit_button = QPushButton("Редактировать выбранное перемещение")
        self.edit_button.clicked.connect(self.edit_selected_movement)
        layout.addWidget(self.edit_button)

        self.history_table(layout)

        self.delete_button = QPushButton("Удалить выбранное перемещение")
        self.delete_button.clicked.connect(self.delete_selected_movement)
        layout.addWidget(self.delete_button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def load_products(self):
        products = self.session.query(Product).all()
        for product in products:
            self.product_filter.addItem(product.name, product.id)

    def edit_selected_movement(self):
        selected_row = self.history_table.currentRow()
        if selected_row >= 0:
            movements = self.get_filtered_movements()
            movement = movements[selected_row]
            dialog = EditMovementDialog(movement, self)
            if dialog.exec() == QDialog.Accepted:
                self.refresh_history()

    def open_add_movement_dialog(self):
        dialog = AddMovementDialog(self)
        if dialog.exec() == QDialog.Accepted:
            self.refresh_history()

    def history_table(self, layout):
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(4)
        self.history_table.setHorizontalHeaderLabels(["Товар", "Откуда", "Куда", "Количество"])
        layout.addWidget(self.history_table)
        self.refresh_history()

    def refresh_history(self):
        movements = self.get_filtered_movements()
        self.history_table.setRowCount(len(movements))
        for row_idx, movement in enumerate(movements):
            self.history_table.setItem(row_idx, 0, QTableWidgetItem(movement.product.name))
            self.history_table.setItem(row_idx, 1, QTableWidgetItem(movement.from_location))
            self.history_table.setItem(row_idx, 2, QTableWidgetItem(movement.to_location))
            self.history_table.setItem(row_idx, 3, QTableWidgetItem(str(movement.quantity)))

    def get_filtered_movements(self):
        search_text = self.search_input.text().strip().lower()
        selected_product_id = self.product_filter.currentData()

        all_movements = self.session.query(Movement).all()
        
        if selected_product_id:
            all_movements = [m for m in all_movements if m.product_id == selected_product_id]

        if not search_text:
            return all_movements
        
        return [m for m in all_movements if (
            search_text in m.product.name.lower() or
            search_text in m.from_location.lower() or
            search_text in m.to_location.lower()
        )]

    def filter_history(self):
        self.refresh_history()

    def delete_selected_movement(self):
        selected_row = self.history_table.currentRow()
        if selected_row >= 0:
            movements = self.get_filtered_movements()
            movement = movements[selected_row]
            self.session.delete(movement)
            self.session.commit()
            self.refresh_history()