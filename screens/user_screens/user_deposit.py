from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, 
    QLineEdit, QMessageBox, QMainWindow
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
import sys
from datetime import datetime
from pathlib import Path
# Add the root directory to sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))
from screens.database import DatabaseManager, get_db_connection

class DepositAmountScreen(QMainWindow):
    def __init__(self, user_id):
        super().__init__()
        self.setWindowTitle("Deposit Amount")
        self.setFixedSize(400, 450)
        self.user_id = user_id
        self.db_manager = DatabaseManager(conn=get_db_connection())
        print(self.user_id)
        
        # Main layout
        main_layout = QVBoxLayout()

        # Top navigation buttons
        top_bar = QHBoxLayout()
        back_button = QPushButton("Back to Balance History")
        back_button.setStyleSheet("background-color: #9C2EF0; color: white; padding: 5px;")
        back_button.clicked.connect(self.go_to_balance_history)
        top_bar.addWidget(back_button)

        main_menu_button = QPushButton("Main Menu")
        main_menu_button.setStyleSheet("background-color: #9C2EF0; color: white; padding: 5px;")
        main_menu_button.clicked.connect(self.go_to_main_menu)
        top_bar.addWidget(main_menu_button)

        main_layout.addLayout(top_bar)

        # Deposit Amount Title
        title_label = QLabel("Deposit Amount", self)
        title_label.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)

        # Instruction Label
        instruction_label = QLabel("Enter an amount between Rs. 500 - 10,000", self)
        instruction_label.setFont(QFont("Arial", 14))
        main_layout.addWidget(instruction_label, alignment=Qt.AlignmentFlag.AlignCenter)

        # Input Field for Deposit Amount
        self.amount_input = QLineEdit(self)
        self.amount_input.setPlaceholderText("Enter amount")
        main_layout.addWidget(self.amount_input, alignment=Qt.AlignmentFlag.AlignCenter)

        # Debit Card Option Button
        self.debit_card_button = QPushButton("Use Debit Card", self)
        self.debit_card_button.setCheckable(True)
        self.debit_card_button.setStyleSheet("font-size: 14px; padding: 8px; background-color: blue; color: white;")
        self.debit_card_button.clicked.connect(self.toggle_card_fields)
        main_layout.addWidget(self.debit_card_button, alignment=Qt.AlignmentFlag.AlignCenter)

        # Card Details Section (Initially Hidden)
        self.card_number_input = QLineEdit(self)
        self.card_number_input.setPlaceholderText("Card Number")
        self.card_number_input.setVisible(False)
        main_layout.addWidget(self.card_number_input, alignment=Qt.AlignmentFlag.AlignCenter)

        # Expiry date and CVV fields
        self.expiry_cvv_layout = QHBoxLayout()
        self.expiry_date_input = QLineEdit(self)
        self.expiry_date_input.setPlaceholderText("MM/YY")
        self.expiry_date_input.setVisible(False)
        self.expiry_cvv_layout.addWidget(self.expiry_date_input)

        self.cvv_input = QLineEdit(self)
        self.cvv_input.setPlaceholderText("CVV")
        self.cvv_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.cvv_input.setVisible(False)
        self.expiry_cvv_layout.addWidget(self.cvv_input)
        main_layout.addLayout(self.expiry_cvv_layout)

        # Confirm Button
        confirm_button = QPushButton("Confirm Deposit", self)
        confirm_button.setStyleSheet("font-size: 14px; padding: 8px; background-color: green; color: white;")
        confirm_button.clicked.connect(self.confirm_deposit)
        main_layout.addWidget(confirm_button, alignment=Qt.AlignmentFlag.AlignCenter)

        # Set main layout
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def toggle_card_fields(self):
        """Toggle the visibility of card input fields."""
        is_checked = self.debit_card_button.isChecked()
        self.card_number_input.setVisible(is_checked)
        self.expiry_date_input.setVisible(is_checked)
        self.cvv_input.setVisible(is_checked)

    def validate_card_info(self):
        """Validate card number, expiry date, and CVV format."""
        card_number = self.card_number_input.text()
        expiry_date = self.expiry_date_input.text()
        cvv = self.cvv_input.text()

        if len(card_number) != 16 or not card_number.isdigit():
            QMessageBox.critical(self, "Invalid Card Number", "Card number must be 16 digits.")
            return False

        try:
            exp_month, exp_year = map(int, expiry_date.split("/"))
            current_date = datetime.now()
            exp_date = datetime(current_date.year // 100 * 100 + exp_year, exp_month, 1)
            if exp_date < current_date:
                QMessageBox.critical(self, "Invalid Expiry Date", "Expiry date must be in the future.")
                return False
        except ValueError:
            QMessageBox.critical(self, "Invalid Expiry Date", "Expiry date format must be MM/YY.")
            return False

        if len(cvv) != 3 or not cvv.isdigit():
            QMessageBox.critical(self, "Invalid CVV", "CVV must be a 3-digit number.")
            return False

        return True

    def confirm_deposit(self):
        """Validate inputs, update balance, and handle deposit action."""
        try:
            deposit_amount = float(self.amount_input.text())
            if deposit_amount < 500 or deposit_amount > 10000:
                QMessageBox.critical(self, "Invalid Amount", "Amount must be between Rs. 500 and Rs. 10,000.")
                return
        except ValueError:
            QMessageBox.critical(self, "Invalid Amount", "Please enter a valid numeric amount.")
            return

        if self.debit_card_button.isChecked():
            if not self.validate_card_info():
                return  # Stop if card validation fails

        # Update balance in the database
        self.db_manager.deposit_money(self.user_id, deposit_amount)
        self.current_balance = self.db_manager.get_user_info(self.user_id)[1]
        QMessageBox.information(self, "Deposit Successful",
                                f"Successfully added Rs. {deposit_amount} to your balance. "
                                f"Your current balance is Rs. {self.current_balance}.")

    def go_to_balance_history(self):
        from user_balance_history import UserBalanceHistory
        self.hide()
        self.user_balance = UserBalanceHistory(self.user_id)
        self.user_balance.show()

    def go_to_main_menu(self):
        from user_main_menu import MainMenuUser
        self.hide()
        self.main_menu = MainMenuUser(self.user_id)
        self.main_menu.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    deposit_screen = DepositAmountScreen(user_id=1001)
    deposit_screen.show()
    sys.exit(app.exec())
