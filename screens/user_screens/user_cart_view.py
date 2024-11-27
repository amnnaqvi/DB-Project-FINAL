from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout,
    QHBoxLayout, QScrollArea, QToolButton, QMainWindow, QMenu, QFrame, QMessageBox
)
from PyQt6.QtGui import QFont, QIcon, QAction
from PyQt6.QtCore import Qt
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))
from screens.database import DatabaseManager, get_db_connection


class UserCartScreen(QMainWindow):
    def __init__(self, user_id):
        super().__init__()
        self.setWindowTitle("Cart")
        self.setFixedSize(600, 700)
        self.user_id = user_id

        # Initialize database manager
        self.db_manager = DatabaseManager(conn=get_db_connection())
        self.cart_items, self.total_cost = self.fetch_cart_items()  # Fetch cart items for the user
        self.user_balance = self.fetch_user_balance()

        # UI setup
        self.create_app_bar()
        self.create_more_menu()
        self.create_cart_items_display()  # Display cart items
        self.create_proceed_button()  # Proceed to ordering button

        # Main layout
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.app_bar)
        main_layout.addWidget(self.cart_scroll_area)
        main_layout.addWidget(self.cart_total_frame)  # Add the cart total frame here
        main_layout.addWidget(self.proceed_button)

        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)
    
    def fetch_user_balance(self):
        info = self.db_manager.get_user_info(self.user_id)
        return info[1]

    def fetch_cart_items(self):
        return self.db_manager.fetch_cart_details(self.user_id)
    
    def create_app_bar(self):
        self.app_bar = QFrame()
        app_bar_layout = QHBoxLayout()

        # Title setup
        title = QLabel("Cart")
        title.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        title.setStyleSheet("color: white;")
        app_bar_layout.addWidget(title)

        # Add a stretch between title and balance to push balance to the right
        app_bar_layout.addStretch()

        # Balance setup
        balance = QLabel(f"Balance: {self.user_balance}")
        balance.setFont(QFont("Arial", 15))
        balance.setStyleSheet("color: white;")
        app_bar_layout.addWidget(balance)

        # Apply layout and style to the app bar
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

    def create_cart_items_display(self):
        """Create scrollable display for cart items with delete functionality."""
        self.cart_layout = QVBoxLayout()
        self.cart_scroll_area = QScrollArea()
        self.cart_scroll_area.setWidgetResizable(True)

        # Populate the initial display with cart items
        self.update_cart_display(self.cart_items)

        # Set up the main widget for the scroll area
        cart_widget = QWidget()
        cart_widget.setLayout(self.cart_layout)
        self.cart_scroll_area.setWidget(cart_widget)

        self.create_cart_total_display()

    def update_cart_display(self, cart_items):
        """Update display for cart items with delete functionality."""
        for i in reversed(range(self.cart_layout.count())):
            widget_to_remove = self.cart_layout.itemAt(i).widget()
            if widget_to_remove is not None:
                widget_to_remove.deleteLater()

        for item_name, quantity, item_total_cost, item_id in cart_items:
            item_frame = QFrame()
            item_frame.setFixedSize(550, 100)
            item_frame.setStyleSheet("background-color: #1A1A3F; border-radius: 8px; padding: 8px;")

            item_frame_layout = QHBoxLayout()

            item_label = QLabel(f"{item_name}\nItem ID: {item_id}")
            item_label.setFont(QFont("Arial", 12))
            item_label.setStyleSheet("color: white;")
            item_frame_layout.addWidget(item_label)

            quantity_label = QLabel(f"Quantity: {quantity}")
            quantity_label.setFont(QFont("Arial", 12))
            quantity_label.setStyleSheet("color: white;")
            item_frame_layout.addWidget(quantity_label)

            item_total_label = QLabel(f"Rs.{item_total_cost}")
            item_total_label.setFont(QFont("Arial", 12, 3))
            item_total_label.setStyleSheet("color: white;")
            item_frame_layout.addWidget(item_total_label)

            delete_button = QPushButton()
            delete_button.setFixedSize(30, 30)
            delete_button.setIcon(QIcon("icons/bin.png"))
            delete_button.setStyleSheet("background-color: transparent;")
            delete_button.clicked.connect(lambda _, i_id=item_id, i_name=item_name: self.confirm_remove_item(i_id, i_name))
            item_frame_layout.addWidget(delete_button)

            item_frame.setLayout(item_frame_layout)
            self.cart_layout.addWidget(item_frame)

        self.cart_scroll_area.update()

    def confirm_remove_item(self, item_id, item_name):
        """Prompt user to confirm removal of an item from the cart."""
        reply = QMessageBox.question(self, "Remove Item", f"Are you sure you want to remove '{item_name}' from your cart?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.remove_item_from_cart(item_id)

    def remove_item_from_cart(self, item_id):
        """Remove an item from the user's cart and update the display."""
        self.db_manager.remove_item_from_cart(self.user_id, item_id)

        # Refresh cart items and display
        self.cart_items, self.total_cost = self.fetch_cart_items()  # Update total cost here
        self.update_cart_display(self.cart_items)
        self.update_cart_total_display()  # Update total cost display

    def create_proceed_button(self):
        """Create Proceed to Ordering button."""
        self.proceed_button = QPushButton("Proceed to Ordering")
        self.proceed_button.setFont(QFont("Arial", 14))
        self.proceed_button.setStyleSheet("background-color: #F0F6FF; color: black; padding: 8px;")
        self.proceed_button.clicked.connect(self.proceed_to_order_confirmation)

    def create_cart_total_display(self):
        """Create a display box showing the total cost of items in the cart."""
        self.cart_total_frame = QFrame()
        self.cart_total_frame.setFixedSize(550, 100)
        self.cart_total_frame.setStyleSheet("border: 2px solid #9C2EF0; background-color: #F0F6FF; border-radius: 8px; padding: 8px;")

        # Layout for the total cost display
        self.total_layout = QHBoxLayout()
        self.total_label = QLabel(f"Cart Total: Rs. {self.total_cost}")
        self.total_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        self.total_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.total_label.setStyleSheet("color: black;")
        self.total_layout.addWidget(self.total_label)

        self.cart_total_frame.setLayout(self.total_layout)
        self.cart_layout.addWidget(self.cart_total_frame)

    def update_cart_total_display(self):
        """Update the total cost label in the cart total display."""
        self.total_label.setText(f"Cart Total: Rs. {self.total_cost}")

    def proceed_to_order_confirmation(self):
        """Redirect to order confirmation page."""
        from user_order_confirmation import OrderConfirmationScreen
        self.hide()
        self.order_confirmation = OrderConfirmationScreen(user_id=self.user_id)
        self.order_confirmation.show()

    def go_to_main_menu(self):
        from user_main_menu import MainMenuUser
        self.hide()
        self.main_menu = MainMenuUser(user_id=self.user_id)
        self.main_menu.show()

    def confirm_logout(self):
        """Confirm logout and close the application."""
        reply = QMessageBox.question(self, "Logout", "Are you sure you want to logout?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    user_cart_screen = UserCartScreen(user_id=1003)
    user_cart_screen.show()
    sys.exit(app.exec())
