from PyQt6.QtWidgets import (
    QWidget, QApplication, QLabel, QVBoxLayout, 
    QHBoxLayout, QScrollArea, QFrame, QTextEdit, QMenu, QPushButton, QMessageBox
)
from PyQt6.QtGui import QTextCursor, QAction, QFont, QIcon
from PyQt6.QtCore import Qt, QPoint
from PyQt6 import QtWidgets
import sys
from pathlib import Path

# Add the root directory to sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))
from screens.database import DatabaseManager, get_db_connection

# Order Details Popup Class
class OrderDetailsPopup(QWidget):
    def __init__(self, user_id, order_id):
        super().__init__()
        self.user_id = user_id
        self.order_id = order_id
        self.db_manager = DatabaseManager(get_db_connection())
        print(self.user_id)

        qr = self.frameGeometry()
        cp = QtWidgets.QApplication.primaryScreen().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

        # Set up window properties for a smaller popup
        self.setWindowTitle("Order Details")
        self.setFixedSize(400, 500)

        # Main layout
        main_layout = QVBoxLayout()

        # "More" Button positioned at the top right of the window
        more_button = QPushButton("More", self)
        more_button.setStyleSheet("background-color: black; color: white; font-weight: bold; padding: 5px;")
        more_button.setFixedSize(60, 30)
        more_button.clicked.connect(self.show_drawer_menu)

        # Align "More" button to the top right of the screen
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(more_button)
        main_layout.addLayout(button_layout)

        # App bar setup
        self.create_app_bar()
        main_layout.addWidget(self.app_bar)

        # Order Details Title
        title_label = QLabel("Order Details", self)
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; margin-top: 10px;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)

        # Text Box for Order Details
        self.order_text = QTextEdit(self)
        self.order_text.setFixedHeight(300)
        self.order_text.setReadOnly(True)
        self.order_text.setStyleSheet("background-color: #1A1A3F; color: white; font-size: 14px; padding: 10px;")

        # Fetch and display order details
        self.display_order_details()

        # Center the cursor to the start of the text box
        self.order_text.moveCursor(QTextCursor.MoveOperation.Start)
        
        # Add the text box to the main layout
        main_layout.addWidget(self.order_text)

        # Set main layout
        self.setLayout(main_layout)

        # Create the drawer menu
        self.drawer_menu = QMenu(self)
        self.create_drawer_menu()

    def create_app_bar(self):
        """Create the application bar with centered title."""
        self.app_bar = QFrame()
        app_bar_layout = QHBoxLayout()

        # Centered title
        title = QLabel("Order History")
        title.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        title.setStyleSheet("color: white;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        app_bar_layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignCenter)

        self.app_bar.setLayout(app_bar_layout)
        self.app_bar.setStyleSheet("background-color: #9c2ef0; padding: 5px;")

    def create_drawer_menu(self):
        """Create the drawer menu with options for Main Menu and Logout actions."""
        main_menu_action = QAction("Main Menu", self)
        main_menu_action.triggered.connect(self.go_to_main_menu)

        logout_action = QAction("Logout", self)
        logout_action.triggered.connect(self.confirm_logout)

        self.drawer_menu.addAction(main_menu_action)
        self.drawer_menu.addAction(logout_action)

    def show_drawer_menu(self):
        """Display the drawer menu at the More button's position."""
        button_position = self.sender().mapToGlobal(QPoint(0, self.sender().height()))
        self.drawer_menu.exec(button_position)

    def fetch_order_details(self):
        """Fetch order details from the database."""
        return self.db_manager.fetch_order_details(self.order_id)

    def display_order_details(self):
        """Display fetched order details in the text box in a receipt format."""
        order_details = self.fetch_order_details()
        if order_details:
            items_and_quantities = order_details[4].replace('\n', '<br>')
            self.order_text.setHtml(
                f"""
                <p><u>Transaction ID:</u> {order_details[8]}<br>
                <u>Customer:</u> {order_details[3]}<br>
                Vendor: {order_details[2]}</p>
                <hr>
                <p>{items_and_quantities}</p>
                <hr>
                <p><b>Subtotal:</b> <span style="float: right;">Rs {order_details[5]}</span></p>
                <p><b>Total:</b> <span style="float: right;">Rs {order_details[5]}</span></p>
                <p><b>Order Date:</b> {order_details[6]}</p>
                <p><b>Pickup:</b> {"Yes" if order_details[7] else "No"}</p>
                """
            )
        else:
            self.order_text.setText("Order details not available.")


    def go_to_main_menu(self):
        from user_main_menu import MainMenuUser
        self.hide()
        self.main_menu = MainMenuUser(self.user_id)
        self.main_menu.show()

    def confirm_logout(self):
        reply = QMessageBox.question(self, "Logout", "Are you sure you want to logout?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.logout()

    def logout(self):
        from screens.login import LoginScreen
        self.hide()
        self.login_screen = LoginScreen()
        self.login_screen.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    order_details_popup = OrderDetailsPopup(user_id=1003, order_id=3)
    order_details_popup.show()
    sys.exit(app.exec())
