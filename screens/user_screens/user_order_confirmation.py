from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout,
    QHBoxLayout, QScrollArea, QToolButton, QMainWindow, QMenu, QFrame, QMessageBox
)
from PyQt6.QtGui import QFont, QIcon, QAction
from PyQt6.QtCore import Qt
from PyQt6 import QtWidgets
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))
from screens.database import DatabaseManager, get_db_connection

class OrderConfirmationScreen(QMainWindow):
    def __init__(self, user_id):
        super().__init__()
        self.setWindowTitle("Order Confirmation")
        self.setFixedSize(600, 700)
        self.user_id = user_id

        qr = self.frameGeometry()
        cp = QtWidgets.QApplication.primaryScreen().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

        # Initialize database manager
        self.db_manager = DatabaseManager(conn=get_db_connection())
        self.cart_items, self.total_cost = self.fetch_cart_items()
        self.user_balance = self.fetch_user_balance()

        # UI setup
        self.create_app_bar()
        self.create_more_menu()
        self.create_order_items_display()
        self.create_order_total_display()
        self.create_confirm_button()

        # Main layout
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.app_bar)
        main_layout.addWidget(self.order_items_frame)
        main_layout.addWidget(self.order_total_frame)
        main_layout.addWidget(self.confirm_button)

        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

    def fetch_cart_items(self):
        """Fetch cart items and total cost for the user."""
        return self.db_manager.fetch_cart_details(self.user_id)

    def fetch_user_balance(self):
        """Fetch the current balance of the user."""
        user_info = self.db_manager.get_user_info(self.user_id)
        return user_info[1] if user_info else 0.0

    def create_app_bar(self):
        self.app_bar = QFrame()
        app_bar_layout = QHBoxLayout()
        self.app_bar.setFixedSize(580, 60)

        title = QLabel("Order Confirmation")
        title.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        title.setStyleSheet("color: white;")
        app_bar_layout.addWidget(title)

        app_bar_layout.addStretch()

        # Balance display
        balance_label = QLabel(f"Balance: Rs. {self.user_balance}")
        balance_label.setFont(QFont("Arial", 15))
        balance_label.setStyleSheet("color: white;")
        app_bar_layout.addWidget(balance_label)

        # Back to Cart button
        back_button = QPushButton("Back to Cart")
        back_button.setFont(QFont("Arial", 10))
        back_button.setStyleSheet("background-color: #F0F6FF; color: black; padding: 5px;")
        back_button.clicked.connect(self.go_back_to_cart)
        app_bar_layout.addWidget(back_button, alignment=Qt.AlignmentFlag.AlignRight)

        self.app_bar.setLayout(app_bar_layout)
        self.app_bar.setStyleSheet("background-color: #9C2EF0;")

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

    def create_order_items_display(self):
        """Display cart items in a single compact box with item details."""
        self.order_items_frame = QFrame()
        self.order_items_frame.setFixedSize(550, 300)  # Adjust size as necessary
        self.order_items_frame.setStyleSheet("background-color: #1a1a3f; padding: 8px;")

        items_text = "\n\n".join([f"{item_name}    x{quantity}" for item_name, quantity, _, _ in self.cart_items])
        items_label = QLabel(items_text)
        items_label.setFont(QFont("Arial", 12))
        items_label.setStyleSheet("color: white;")

        order_items_layout = QVBoxLayout()
        order_items_layout.addWidget(items_label)
        self.order_items_frame.setLayout(order_items_layout)

    def create_order_total_display(self):
        """Display total cost of the order in a small sharp-edged box."""
        self.order_total_frame = QFrame()
        self.order_total_frame.setFixedSize(550, 100)  # Smaller frame for the order total
        self.order_total_frame.setStyleSheet("background-color: #1a1a3f; padding: 8px;")

        total_label = QLabel(f"Order Total: Rs. {self.total_cost}")
        total_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        total_label.setStyleSheet("color: white;")

        order_total_layout = QHBoxLayout()
        order_total_layout.addWidget(total_label)
        self.order_total_frame.setLayout(order_total_layout)

    def create_confirm_button(self):
        """Create Confirm Order button."""
        self.confirm_button = QPushButton("Confirm Order")
        self.confirm_button.setFont(QFont("Arial", 14))
        self.confirm_button.setStyleSheet("background-color: #F0F6FF; color: black; padding: 8px;")
        self.confirm_button.clicked.connect(self.confirm_order)

    def confirm_order(self):
        """Check balance, place order if sufficient funds, else show warning."""
        if self.user_balance >= self.total_cost:
            self.place_order()
        else:
            self.show_insufficient_balance_dialog()

    def place_order(self):
        """Place the order using the stored procedure and handle success/failure."""
        try:
            success, message = self.db_manager.place_order(user_id=self.user_id, is_pickup=1, total_cost=self.total_cost)
            if success:
                QMessageBox.information(self, "Order Placed", "Order placed successfully!")
                self.go_to_main_menu()
            else:
                QMessageBox.warning(self, "Order Failed", f"Order could not be placed: {message}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred while placing the order: {e}")

    def show_insufficient_balance_dialog(self):
        """Show warning dialog for insufficient balance with options."""
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Icon.Critical)
        msg_box.setWindowTitle("Insufficient Balance")
        msg_box.setText("You do not have sufficient balance to place this order.")
        update_balance_button = msg_box.addButton("Update Balance", QMessageBox.ButtonRole.AcceptRole)
        back_to_cart = msg_box.addButton("Back to Cart", QMessageBox.ButtonRole.RejectRole)
        msg_box.exec()

        if msg_box.clickedButton() == update_balance_button:
            self.go_to_update_balance()
        elif msg_box.clickedButton() == back_to_cart:
            self.go_back_to_cart()

    def go_back_to_cart(self):
        from user_cart_view import UserCartScreen
        self.hide()
        self.cart_screen = UserCartScreen(user_id=self.user_id)
        self.cart_screen.show()

    def go_to_main_menu(self):
        from user_main_menu import MainMenuUser
        self.hide()
        self.main_menu = MainMenuUser(user_id=self.user_id)
        self.main_menu.show()

    def go_to_update_balance(self):
        pass
        # Implement logic to navigate to balance update screen

    def confirm_logout(self):
        """Confirm logout and close the application."""
        reply = QMessageBox.question(self, "Logout", "Are you sure you want to logout?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    order_confirmation_screen = OrderConfirmationScreen(user_id=1003)
    order_confirmation_screen.show()
    sys.exit(app.exec())
