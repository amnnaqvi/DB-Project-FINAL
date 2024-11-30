from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout,
    QHBoxLayout, QScrollArea, QToolButton, QMainWindow, QMenu, QFrame, QMessageBox
)
from PyQt6.QtGui import QFont, QIcon, QAction
from PyQt6.QtCore import Qt
from PyQt6 import QtWidgets
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))
from screens.database import DatabaseManager, get_db_connection


class UserBuyMenu(QMainWindow):
    def __init__(self, user_id, vendor_id):
        super().__init__()
        self.setWindowTitle("Vendor Menu")
        self.setFixedSize(600, 700)
        self.user_id = user_id
        self.vendor_id = vendor_id

        qr = self.frameGeometry()
        cp = QtWidgets.QApplication.primaryScreen().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

        # Initialize database manager
        self.db_manager = DatabaseManager(conn=get_db_connection())
        self.vendor_name = self.fetch_vendor_name()  # Get vendor's name
        self.items = self.fetch_vendor_items()  # Fetch menu items with IDs

        # UI setup
        self.create_app_bar()
        self.create_search_bar()
        self.create_vendor_info_panel()
        self.create_more_menu()
        
        # No results label
        self.no_results_label = QLabel("")
        self.no_results_label.setFont(QFont("Arial", 12))
        self.no_results_label.setStyleSheet("color: white;")

        self.create_item_cards() 

        # Main layout
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.app_bar)
        main_layout.addLayout(self.search_bar)
        main_layout.addWidget(self.vendor_info_panel)
        main_layout.addWidget(self.item_scroll_area)
        main_layout.addWidget(self.no_results_label)

        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

    def fetch_vendor_name(self):
        vendor_info = self.db_manager.get_vendor_info(self.vendor_id)
        return vendor_info[1] if vendor_info else "Unknown Vendor"

    def fetch_vendor_items(self):
        return self.db_manager.fetch_vendor_items(self.vendor_id)

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
        self.app_bar.setStyleSheet("background-color: #9c2ef0;")

    def create_more_menu(self):
        self.more_menu = QMenu("More", self)
        main_menu_action = QAction("Main Menu", self)
        main_menu_action.triggered.connect(self.go_to_main_menu)

        logout_action = QAction("Logout", self)
        logout_action.triggered.connect(self.confirm_logout)

        self.more_menu.addAction(main_menu_action)
        self.more_menu.addAction(logout_action)
        self.menuBar().addMenu(self.more_menu)

    def create_search_bar(self):
        self.search_bar = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search for a menu item")
        self.search_bar.addWidget(self.search_input)
        self.search_input.textChanged.connect(self.filter_items)

    def create_vendor_info_panel(self):
        self.vendor_info_panel = QWidget()
        vendor_info_layout = QVBoxLayout()

        vendor_name_label = QLabel(f"Vendor: {self.vendor_name}")
        vendor_name_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))

        vendor_info_layout.addWidget(vendor_name_label)
        self.vendor_info_panel.setLayout(vendor_info_layout)
        self.vendor_info_panel.setStyleSheet("background-color: rgba(0, 0, 139, 0.9); padding: 10px;")

    def create_item_cards(self):
        self.item_layout = QVBoxLayout()
        self.item_scroll_area = QScrollArea()

        self.update_item_cards(self.items)

        item_widget = QWidget()
        item_widget.setLayout(self.item_layout)
        self.item_scroll_area.setWidget(item_widget)
        self.item_scroll_area.setWidgetResizable(True)

    def update_item_cards(self, item_list):
        self.item_layout = QVBoxLayout() 

        for item_id, item_name, price, subcategory_type in item_list:
            item_card = QFrame()
            item_card_layout = QVBoxLayout()
            item_card_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

            # Item name and price
            item_label = QLabel(f"{item_name} - Rs. {price} ({subcategory_type})")
            item_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
            item_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            item_card_layout.addWidget(item_label)

            # Add to cart button
            add_button = QPushButton()
            add_button.setIcon(QIcon("icons/add.png"))
            add_button.setFixedSize(40, 40)
            add_button.setStyleSheet("background-color: #ADD8E6; border-radius: 20px; padding: 5px;")
            add_button.clicked.connect(lambda _, i_id=item_id, i_name=item_name: self.add_item_to_cart(i_id, i_name))

            # Heart icon button to add to favorites
            heart_button = QPushButton()
            heart_button.setIcon(QIcon("icons/heart.png"))
            heart_button.setFixedSize(40, 40)
            heart_button.setStyleSheet("background-color: transparent;")
            heart_button.clicked.connect(lambda _, i_id=item_id: self.add_to_favorites(i_id))

            # Add buttons layout
            buttons_layout = QHBoxLayout()
            buttons_layout.addStretch()
            buttons_layout.addWidget(add_button)
            buttons_layout.addWidget(heart_button)

            item_card_layout.addLayout(buttons_layout)

            # Set up item card appearance
            item_card.setLayout(item_card_layout)
            item_card.setStyleSheet("border: 2px solid rgba(0, 0, 255, 0.2); padding: 10px;")
            self.item_layout.addWidget(item_card)

        # Update scroll area
        self.item_scroll_area.takeWidget()
        item_widget = QWidget()
        item_widget.setLayout(self.item_layout)
        self.item_scroll_area.setWidget(item_widget)

        # Update no results label
        self.no_results_label.setText(f"No results for '{self.search_input.text()}'" if not item_list else "")

    def filter_items(self):
        search_text = self.search_input.text().lower()
        filtered_items = [item for item in self.items if search_text in item[1].lower()]
        self.update_item_cards(filtered_items)

    def add_item_to_cart(self, item_id, item_name):
        try:
            success, status = self.db_manager.add_or_update_cart_item(self.user_id, self.vendor_id, item_id)
            
            if success:
                if status == "item_added":
                    QMessageBox.information(self, "Added to Cart", f"{item_name} was added to your cart successfully!")
                elif status == "quantity_updated":
                    QMessageBox.information(self, "Updated Cart", f"Quantity of {item_name} was updated in your cart.")
            elif status == "different_vendor":
                QMessageBox.warning(self, "Cart Restriction", "You already have items from another vendor in your cart.")
            else:
                QMessageBox.critical(self, "Error", f"An error occurred: {status}")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred while adding the item to the cart: {e}")
            print(f"Error in add_item_to_cart: {e}")

    def add_to_favorites(self, item_id):
        try:
            success = self.db_manager.add_to_user_favorites(self.user_id, item_id)
            if success:
                QMessageBox.information(self, "Added to Favorites", "Item was added to your favorites.")
            else:
                QMessageBox.warning(self, "Already in Favorites", "This item is already in your favorites.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred while adding the item to favorites: {e}")

    def go_to_main_menu(self):
        from user_main_menu import MainMenuUser
        self.hide()
        self.main_menu = MainMenuUser(user_id=self.user_id)
        self.main_menu.show()

    def open_cart(self):
        from user_cart_view import UserCartScreen
        self.hide()
        self.cart = UserCartScreen(self.user_id)
        self.cart.show()
    
    def logout(self):
        from screens.login import LoginScreen
        self.hide()
        self.logout_screen = LoginScreen
        self.logout_screen.show()

    def confirm_logout(self):
        reply = QMessageBox.question(self, "Logout", "Are you sure you want to logout?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.logout()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    user_buy_menu = UserBuyMenu(user_id=1000, vendor_id=103)
    user_buy_menu.show()
    sys.exit(app.exec())
