from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout, 
    QPushButton, QScrollArea, QMainWindow, QMenu, QFrame, QMessageBox, QToolButton, QLineEdit
)
from PyQt6.QtGui import QFont, QIcon, QAction
from PyQt6.QtCore import Qt
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))
from screens.login import LoginScreen
from screens.database import DatabaseManager, get_db_connection

class FavoritesScreen(QMainWindow):
    def __init__(self, user_id):
        super().__init__()
        self.setWindowTitle("HU Eats - Favorites")
        self.setFixedSize(600, 700)
        self.user_id = user_id
        self.db_manager = DatabaseManager(conn=get_db_connection())
        self.favorites = self.fetch_favorites()
        
        # UI setup
        self.create_app_bar()
        self.create_search_bar()  # Add search bar
        self.create_favorites_list()
        self.create_drawer()

        # Set central widget layout
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.app_bar)
        main_layout.addLayout(self.search_bar)  # Add search bar to layout
        main_layout.addWidget(self.favorite_scroll_area)

        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

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


    def create_drawer(self):
        drawer = QMenu(self)
        drawer.setTitle("More")

        main_menu_action = QAction("Main Menu", self)
        main_menu_action.triggered.connect(self.go_to_main_menu)

        logout_action = QAction("Logout", self)
        logout_action.triggered.connect(self.confirm_logout)

        drawer.addAction(main_menu_action)
        drawer.addAction(logout_action)

        self.menuBar().addMenu(drawer)
    
    def create_search_bar(self):
        """Create a search bar to filter favorites."""
        self.search_bar = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by item or vendor name")
        self.search_input.textChanged.connect(self.filter_favorites)
        self.search_bar.addWidget(self.search_input)

    def updated_favorites_list(self, filtered_favorites):
        """Update the favorites list dynamically based on the filtered results."""
        # Clear the current layout
        for i in reversed(range(self.favorite_layout.count())):
            widget = self.favorite_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        # Repopulate with filtered favorites
        for favorite in filtered_favorites:
            self.add_favorite_box(favorite)

    def filter_favorites(self):
        """Filter favorite items based on search input and update display dynamically."""
        search_text = self.search_input.text().lower()
        filtered_favorites = [
            favorite for favorite in self.favorites
            if search_text in favorite['Name'].lower() or search_text in favorite['Vendor'].lower()
        ]
        self.updated_favorites_list(filtered_favorites)
    
    def open_vendor_menu(self, vendor_id):
        """Open the UserBuyMenu for a specific vendor."""
        from user_vendor_menu import UserBuyMenu
        self.hide()
        self.vendor_menu = UserBuyMenu(user_id=self.user_id, vendor_id=vendor_id)
        self.vendor_menu.show()
    
    def open_cart(self):
        from user_cart_view import UserCartScreen
        self.hide()
        self.cartScreen = UserCartScreen(self.user_id)
        self.cartScreen.show()

    def fetch_favorites(self):
        """Fetch favorite items for the user from the database."""
        infos = self.db_manager.fetch_user_favorite_items(self.user_id)
        return [{
            'ID': info[0],
            'Name': info[1],
            'Vendor': info[2],
            'Date': info[3].strftime("%Y-%m-%d %H:%M"),
            'Price': f"Rs {info[4]:.2f}",
            'VendorID': info[5]  # Make sure vendor_id is the last item in the tuple
        } for info in infos]

    def create_favorites_list(self):
        # Scrollable favorite items list
        self.favorite_layout = QVBoxLayout()
        self.favorite_scroll_area = QScrollArea()
        self.favorite_scroll_area.setWidgetResizable(True)

        # Populate with favorite items
        for favorite in self.favorites:
            self.add_favorite_box(favorite)

        favorite_widget = QWidget()
        favorite_widget.setLayout(self.favorite_layout)
        self.favorite_scroll_area.setWidget(favorite_widget)

    def add_favorite_box(self, favorite):
        """Display each favorite item in a stylized box with item details and add button."""
        favorite_box = QFrame()
        favorite_box.setStyleSheet("background-color: #1A1A3F; padding: 10px; border-radius: 8px;")
        favorite_box.setFixedHeight(300)
        favorite_box_layout = QVBoxLayout()

        # Item Name (bold) and ID
        name_label = QLabel(f"<b>{favorite['Name']}</b>")
        name_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        id_label = QLabel(f"ID: {favorite['ID']}")
        id_label.setStyleSheet("font-size: 12px; color: #A9A9A9;")

        # Date Added and Vendor Name
        date_label = QLabel(f"Date Added: {favorite['Date']}")
        date_label.setStyleSheet("font-size: 12px; color: #A9A9A9;")
        vendor_price_layout = QHBoxLayout()
        vendor_label = QLabel(favorite['Vendor'])
        price_label = QLabel(favorite['Price'])
        vendor_price_layout.addWidget(vendor_label)
        vendor_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        price_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        vendor_price_layout.addStretch()
        vendor_price_layout.addWidget(price_label)

        # Add to Cart Button
        add_button = QPushButton()
        add_button.setIcon(QIcon("icons/add.png"))
        add_button.setFixedSize(30, 30)
        add_button.setStyleSheet("background-color: #ADD8E6; border-radius: 15px;")
        # Pass both item ID and vendor ID to add_to_cart
        add_button.clicked.connect(lambda _, item_id=favorite['ID'], vendor_id=favorite['VendorID']: self.add_to_cart(item_id, vendor_id))

        # Remove from Favorites Button
        remove_button = QPushButton()
        remove_button.setIcon(QIcon("icons/bin.png"))
        remove_button.setFixedSize(30, 30)
        remove_button.setStyleSheet("background-color: #808080; border-radius: 15px;")
        remove_button.clicked.connect(lambda _, item_id=favorite['ID']: self.remove_from_favorites(item_id))

        # Add widgets to favorite box layout
        favorite_box_layout.addWidget(name_label)
        favorite_box_layout.addWidget(id_label)
        favorite_box_layout.addWidget(date_label)
        favorite_box_layout.addLayout(vendor_price_layout)
        favorite_box_layout.addWidget(remove_button, alignment=Qt.AlignmentFlag.AlignRight)
        favorite_box_layout.addWidget(add_button, alignment=Qt.AlignmentFlag.AlignRight)
        

        favorite_box.setLayout(favorite_box_layout)
        self.favorite_layout.addWidget(favorite_box)

    def add_to_cart(self, item_id, vendor_id):
        """Add selected favorite item to the user's cart."""
        try:
            success, status = self.db_manager.add_or_update_cart_item(self.user_id, vendor_id, item_id)
            if success:
                QMessageBox.information(self, "Added to Cart", f"Item '{item_id}' was added to your cart successfully!")
            else:
                QMessageBox.warning(self, "Error", f"Could not add item to cart: {status}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")
    
    def remove_from_favorites(self, item_id):
        """Remove selected favorite item from the user's favorites dynamically."""
        reply = QMessageBox.question(
            self, "Remove Favorite", f"Are you sure you want to remove item ID: {item_id} from favorites?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            try:
                success, status = self.db_manager.remove_favorites(self.user_id, item_id)
                if success:
                    QMessageBox.information(self, "Removed from Favorites", f"Item '{item_id}' was removed successfully!")
                    
                    # Update the favorites list in memory
                    self.favorites = [favorite for favorite in self.favorites if favorite['ID'] != item_id]
                    
                    # Rebuild the favorites list UI dynamically
                    self.update_favorites_list()
                else:
                    QMessageBox.warning(self, "Error", f"Could not remove item from favorites: {status}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"An error occurred while removing the favorite: {str(e)}")

    def update_favorites_list(self):
        """Rebuild the favorites list UI dynamically."""
        # Clear the current layout
        for i in reversed(range(self.favorite_layout.count())):
            widget = self.favorite_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        # Repopulate with updated favorites
        for favorite in self.favorites:
            self.add_favorite_box(favorite)


    

    def confirm_logout(self):
        reply = QMessageBox.question(self, "Logout", "Are you sure you want to logout?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.logout()
        
    def logout(self):
        self.hide()
        self.login_screen = LoginScreen()
        self.login_screen.show()

    def go_to_main_menu(self):
        from user_main_menu import MainMenuUser
        self.hide()
        self.main_menu = MainMenuUser(self.user_id)
        self.main_menu.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    user_id = 1000
    favorites_screen = FavoritesScreen(user_id=user_id)
    favorites_screen.show()
    sys.exit(app.exec())
