from PySide6.QtWidgets import (
    QDialog, QLineEdit, QHBoxLayout, QFormLayout, QVBoxLayout, QPushButton, QComboBox
)
from datebase import Connect, Movement, Product

class AddMovementDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.session = Connect.create_connection()
        self.setWindowTitle("Добавить перемещение")
        
        form_layout = QFormLayout()

        self.product_combo = QComboBox()
        self.load_products()
        
        self.from_location_input = QLineEdit()
        self.to_location_input = QLineEdit()
        self.quantity_input = QLineEdit()

        form_layout.addRow("Название товара:", self.product_combo)
        form_layout.addRow("Откуда:", self.from_location_input)
        form_layout.addRow("Куда:", self.to_location_input)
        form_layout.addRow("Количество:", self.quantity_input)

        save_button = QPushButton("Сохранить")
        save_button.clicked.connect(self.save_new_movement)
        cancel_button = QPushButton("Отмена")
        cancel_button.clicked.connect(self.reject)

        button_layout = QHBoxLayout()
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)

        main_layout = QVBoxLayout()
        main_layout.addLayout(form_layout)
        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)

    def load_products(self):
        products = self.session.query(Product).all()
        for product in products:
            self.product_combo.addItem(product.name, product.id)

    def save_new_movement(self):
        selected_product_id = self.product_combo.currentData()
        from_location = self.from_location_input.text().strip()
        to_location = self.to_location_input.text().strip()
        quantity = int(self.quantity_input.text())

        new_movement = Movement(
            product_id=selected_product_id,
            from_location=from_location,
            to_location=to_location,
            quantity=quantity
        )
        self.session.add(new_movement)
        self.session.commit()
        self.accept()