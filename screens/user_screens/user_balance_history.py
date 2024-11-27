from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QPushButton, QScrollArea, QMainWindow, QMenu, QFrame, QMessageBox, QToolButton
)
from PyQt6.QtGui import QFont, QAction, QIcon
from PyQt6.QtCore import Qt
import sys
from pathlib import Path

# Add the root directory to sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))
from screens.database import DatabaseManager, get_db_connection

class UserBalanceHistory(QMainWindow):
    def __init__(self, user_id):
        super().__init__()
        self.setWindowTitle("HU Eats - Balance History")
        self.setFixedSize(600, 700)
        self.user_id = user_id
        print(self.user_id)

        # Initialize database manager
        self.db_manager = DatabaseManager(conn=get_db_connection())
        self.current_balance = self.fetch_user_balance()  # Fetch current balance from the database
        self.transactions = self.fetch_balance_history()  # Fetch transaction history from the database

        # UI setup
        self.create_app_bar()
        self.create_balance_box()
        self.create_balance_history_list()
        self.create_more_menu()

        # Set central widget layout
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.app_bar)
        main_layout.addWidget(self.balance_box)
        main_layout.addWidget(self.balance_history_scroll_area)

        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

    def fetch_user_balance(self):
        """Fetch the user's current balance from the database."""
        user_info = self.db_manager.get_user_info(self.user_id)
        return user_info[1] if user_info else "0.00"

    def fetch_balance_history(self):
        """Fetch the user's balance history from the database."""
        return self.db_manager.fetch_balance_history(self.user_id)

    def create_app_bar(self):
        self.app_bar = QFrame()
        app_bar_layout = QHBoxLayout()

        title = QLabel("HU_EATS")
        title.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        title.setStyleSheet("color: white;")

        cart_icon = QToolButton()
        cart_icon.setIcon(QIcon("icons/cart.png"))
        cart_icon.clicked.connect(self.open_cart)

        logout_icon = QToolButton()
        logout_icon.setIcon(QIcon("icons/logout.png"))
        logout_icon.clicked.connect(self.confirm_logout)

        app_bar_layout.addWidget(title)
        app_bar_layout.addStretch()
        app_bar_layout.addWidget(cart_icon)
        app_bar_layout.addWidget(logout_icon)

        self.app_bar.setLayout(app_bar_layout)
        self.app_bar.setStyleSheet("background-color: #9C2EF0")

    def create_more_menu(self):
        """Add a More button with options to go to the main menu or logout."""
        self.more_menu = QMenu("More", self)
        main_menu_action = QAction("Main Menu", self)
        main_menu_action.triggered.connect(self.go_to_main_menu)

        logout_action = QAction("Logout", self)
        logout_action.triggered.connect(self.confirm_logout)

        self.more_menu.addAction(main_menu_action)
        self.more_menu.addAction(logout_action)
        self.menuBar().addMenu(self.more_menu)

    def create_balance_box(self):
        # Box to show current balance and deposit option
        self.balance_box = QFrame()
        self.balance_box.setStyleSheet("background-color: #2b2b2b; color: white; padding: 15px;")
        
        balance_layout = QVBoxLayout()

        # Current balance display
        current_balance_label = QLabel(f"Current Balance: Rs. {self.current_balance}")
        current_balance_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        balance_layout.addWidget(current_balance_label, alignment=Qt.AlignmentFlag.AlignCenter)

        # Deposit button
        deposit_button = QPushButton("Deposit Amount")
        deposit_button.setFont(QFont("Arial", 12))
        deposit_button.setStyleSheet("background-color: #F0F6FF; color: black; padding: 5px;")
        deposit_button.clicked.connect(self.deposit_amount)
        balance_layout.addWidget(deposit_button, alignment=Qt.AlignmentFlag.AlignCenter)

        self.balance_box.setLayout(balance_layout)

    def create_balance_history_list(self):
        # Scrollable balance history list
        self.balance_history_layout = QVBoxLayout()
        self.balance_history_scroll_area = QScrollArea()
        self.balance_history_scroll_area.setWidgetResizable(True)
        self.balance_history_scroll_area.setStyleSheet("background-color: #1a1a3f;")

        # Add transaction widgets to layout
        for transaction in self.transactions:
            self.add_transaction_box(
                transaction_type = transaction[0],
                transaction_id=transaction[1], 
                amount=transaction[2],
                date=transaction[3], 
                time=transaction[4] # Assuming datetime format, adjust if needed
            )

        history_widget = QWidget()
        history_widget.setLayout(self.balance_history_layout)
        self.balance_history_scroll_area.setWidget(history_widget)

    def add_transaction_box(self, transaction_type, transaction_id, amount, date, time):
        # Create a single transaction box
        transaction_box = QFrame()
        transaction_box.setStyleSheet("background-color: #2b2b2b; color: white; padding: 15px;")
        
        transaction_layout = QHBoxLayout()
        transaction_id_label = QLabel(f"Transaction ID: {transaction_id} \n Type: {transaction_type}")
        transaction_id_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))

        date_time_label = QLabel(f"{date} | {time}")
        date_time_label.setFont(QFont("Arial", 10))

        amount_label = QLabel(f"Rs. {amount}")
        amount_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        amount_label.setStyleSheet("color: green;" if "+" in str(amount) else "color: red;")

        # Add components to layout
        transaction_layout.addWidget(transaction_id_label)
        transaction_layout.addStretch()
        transaction_layout.addWidget(date_time_label)
        transaction_layout.addWidget(amount_label)

        transaction_box.setLayout(transaction_layout)
        self.balance_history_layout.addWidget(transaction_box)

    def deposit_amount(self):
        from user_deposit import DepositAmountScreen
        self.hide()
        self.deposit_screen = DepositAmountScreen(self.user_id)
        self.deposit_screen.show()

    def confirm_logout(self):
        reply = QMessageBox.question(self, "Logout", "Are you sure you want to logout?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.logout()

    def open_cart(self):
        from user_cart_view import UserCartScreen
        self.hide()
        self.cart_screen = UserCartScreen(self.user_id)
        self.cart_screen.show()

    def logout(self):
        """Logout functionality."""
        from screens.login import LoginScreen
        self.hide()
        self.logout_screen = LoginScreen
        self.logout_screen.show()

    def go_to_main_menu(self):
        """Redirect to main menu functionality."""
        from user_main_menu import MainMenuUser
        self.hide()
        self.main_menu = MainMenuUser(self.user_id)
        self.main_menu.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    user_balance_history = UserBalanceHistory(user_id=1003)
    user_balance_history.show()
    sys.exit(app.exec())
