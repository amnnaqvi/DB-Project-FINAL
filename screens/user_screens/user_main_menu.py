from PyQt6 import QtWidgets
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout,
    QHBoxLayout, QMessageBox, QGridLayout, QScrollArea, QToolButton,
    QMainWindow, QMenu, QFrame
)
from PyQt6.QtGui import QFont, QAction, QIcon, QPixmap
from PyQt6.QtCore import Qt
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))
from screens.database import DatabaseManager, get_db_connection


class MainMenuUser(QMainWindow):
    def __init__(self, user_id):
        super().__init__()
        self.setWindowTitle("HU Eats - Main Menu")
        self.setFixedSize(600, 700)
        self.user_id = user_id

        qr = self.frameGeometry()
        cp = QtWidgets.QApplication.primaryScreen().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

        # Initialize database manager and fetch user and vendor data
        self.db_manager = DatabaseManager(conn=get_db_connection())
        self.user_info = self.fetch_user_info()  # Fetches full_name and balance
        self.vendors = self.fetch_vendors()  # List of vendors with images

        # Create and set up the UI components
        self.create_app_bar()
        self.create_search_bar()
        self.create_user_info_panel()
        self.create_drawer()

        # Initialize no results label for search feedback
        self.no_results_label = QLabel("")  
        self.no_results_label.setFont(QFont("Arial", 12))
        self.no_results_label.setStyleSheet("color: white;")

        # Create vendor cards and add to layout
        self.create_vendor_cards()  

        # Set main layout for central widget
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.app_bar)
        main_layout.addLayout(self.search_bar)
        main_layout.addWidget(self.user_info_panel)
        main_layout.addWidget(self.vendor_scroll_area)
        main_layout.addWidget(self.no_results_label)

        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

    def fetch_user_info(self):
        user_info = self.db_manager.get_user_info(self.user_id)
        return {
            'full_name': user_info[0] if user_info else "N/A",
            'current_balance': user_info[1] if user_info else "0.00"
        }

    def fetch_vendors(self):
        vendors = self.db_manager.get_active_vendors()
        return [(vendor[0], vendor[1], vendor[2]) for vendor in vendors]  # vendor_id, vendor_name, image_path

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

    def create_search_bar(self):
        self.search_bar = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search for a vendor")
        self.search_bar.addWidget(self.search_input)

        # Connect the textChanged signal to dynamically filter vendors
        self.search_input.textChanged.connect(self.filter_vendors)

    def create_user_info_panel(self):
        self.user_info_panel = QWidget()
        user_info_layout = QVBoxLayout()

        name_label = QLabel(f"Name: {self.user_info['full_name']}")
        name_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))

        balance_label = QLabel(f"Balance: Rs. {self.user_info['current_balance']}")
        balance_label.setFont(QFont("Arial", 14))

        user_info_layout.addWidget(name_label)
        user_info_layout.addWidget(balance_label)
        self.user_info_panel.setLayout(user_info_layout)
        self.user_info_panel.setStyleSheet("background-color: rgba(0, 0, 139, 0.9); padding: 10px;")

    def create_vendor_cards(self):
        self.vendor_layout = QGridLayout()
        self.vendor_scroll_area = QScrollArea()
        self.update_vendor_cards(self.vendors)  # Initialize with all vendors

        vendor_widget = QWidget()
        vendor_widget.setLayout(self.vendor_layout)
        self.vendor_scroll_area.setWidget(vendor_widget)
        self.vendor_scroll_area.setWidgetResizable(True)

    def update_vendor_cards(self, vendor_list):
        self.vendor_layout = QGridLayout()  # Clear existing vendor layout

        for i, (vendor_id, vendor_name, image_path) in enumerate(vendor_list):
            vendor_card = QWidget()
            vendor_card_layout = QVBoxLayout()
            vendor_card_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

            # Add vendor image if available
            if image_path:
                vendor_image = QLabel()
                pixmap = QPixmap(image_path).scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio)
                vendor_image.setPixmap(pixmap)
            else:
                vendor_image = QLabel("No Image")
                vendor_image.setFixedSize(100, 100)
                vendor_image.setStyleSheet("background-color: #cccccc;")

            vendor_card_layout.addWidget(vendor_image)

            # Vendor name
            vendor_label = QLabel(vendor_name)
            vendor_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
            vendor_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            vendor_card_layout.addWidget(vendor_label)

            # Visit button
            visit_button = QPushButton("Visit")
            visit_button.setStyleSheet("background-color: rgba(255, 255, 0, 0.8); padding: 5px;")
            visit_button.clicked.connect(lambda _, v_id=vendor_id: self.open_vendor_menu(v_id))
            vendor_card_layout.addWidget(visit_button)

            vendor_card.setLayout(vendor_card_layout)
            vendor_card.setStyleSheet("border: 2px solid rgba(255, 255, 0, 0.8); padding: 10px;")

            self.vendor_layout.addWidget(vendor_card, i // 3, i % 3)

        # Update scroll area
        self.vendor_scroll_area.takeWidget()  # Remove old widget
        vendor_widget = QWidget()
        vendor_widget.setLayout(self.vendor_layout)
        self.vendor_scroll_area.setWidget(vendor_widget)

        # Update no results label based on the filtered list
        if not vendor_list:
            self.no_results_label.setText(f"No results for '{self.search_input.text()}'")
        else:
            self.no_results_label.setText("")

    def filter_vendors(self):
        """Filter vendor list based on search input and update display dynamically."""
        search_text = self.search_input.text().lower()
        filtered_vendors = [vendor for vendor in self.vendors if search_text in vendor[1].lower()]
        self.update_vendor_cards(filtered_vendors)


    def create_drawer(self):
        drawer = QMenu(self)
        drawer.setTitle("More")

        notifications_action = QAction("Notifications", self)
        notifications_action.triggered.connect(self.open_notifications)

        order_history_action = QAction("Order History", self)
        order_history_action.triggered.connect(self.open_order_history)

        balance_history_action = QAction("Balance History", self)
        balance_history_action.triggered.connect(self.open_balance_history)

        favorites_action = QAction("Favorites", self)
        favorites_action.triggered.connect(self.open_favorites)

        logout_action = QAction("Logout", self)
        logout_action.triggered.connect(self.confirm_logout)

        drawer.addAction(notifications_action)
        drawer.addAction(order_history_action)
        drawer.addAction(balance_history_action)
        drawer.addAction(favorites_action)
        drawer.addAction(logout_action)

        self.menuBar().addMenu(drawer)
    
    def open_vendor_menu(self, vendor_id):
        """Open the UserBuyMenu for a specific vendor."""
        from user_vendor_menu import UserBuyMenu
        self.hide()
        self.vendor_menu = UserBuyMenu(user_id=self.user_id, vendor_id=vendor_id)
        self.vendor_menu.show()

    def open_notifications(self):
        from user_notifications import NotificationScreen
        self.hide()
        self.notifications = NotificationScreen(self.user_id)
        self.notifications.show()

    def open_cart(self):
        from user_cart_view import UserCartScreen
        self.hide()
        self.cartScreen = UserCartScreen(self.user_id)
        self.cartScreen.show()

    def open_order_history(self):
        from user_all_order_history import OrderHistoryScreen
        self.hide()
        self.orderHistory = OrderHistoryScreen(self.user_id)
        self.orderHistory.show()

    def open_balance_history(self):
        from user_balance_history import UserBalanceHistory
        self.hide()
        self.balance_screen = UserBalanceHistory(self.user_id)
        self.balance_screen.show()

    def open_favorites(self):
        from user_favorites import FavoritesScreen
        self.hide()
        self.favorite_screen = FavoritesScreen(self.user_id)
        self.favorite_screen.show()
    
    def logout(self):
        from screens.login import LoginScreen
        self.hide()
        self.logoutscreen = LoginScreen
        self.logoutscreen.show()

    def confirm_logout(self):
        reply = QMessageBox.question(self, "Logout", "Are you sure you want to logout?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.logout()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    user_main_menu = MainMenuUser(user_id=1002)
    user_main_menu.show()
    sys.exit(app.exec())
