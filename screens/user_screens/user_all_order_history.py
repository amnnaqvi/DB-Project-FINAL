from PyQt6.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout, 
    QHBoxLayout, QScrollArea, QFrame, QMenu, QMessageBox, QApplication, QSpacerItem, QSizePolicy, QToolButton, QDialog, QComboBox
)
from PyQt6.QtGui import QAction, QFont, QIcon
from PyQt6.QtCore import Qt, QPoint
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))
from screens.database import DatabaseManager, get_db_connection


class OrderHistoryScreen(QWidget):
    def __init__(self, user_id):
        super().__init__()
        self.user_id = user_id
        self.db_manager = DatabaseManager(get_db_connection())
        print(self.user_id)
        
        self.setWindowTitle("Order History")
        self.setFixedSize(600, 700)

        main_layout = QVBoxLayout()

        # Add "More" button
        more_button = QPushButton("More", self)
        more_button.setStyleSheet("background-color: black; color: white; font-weight: bold; padding: 5px;")
        more_button.setFixedSize(60, 30)
        more_button.clicked.connect(self.show_drawer_menu)
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(more_button)
        main_layout.addLayout(button_layout)

        # App bar setup
        self.create_app_bar()
        main_layout.addWidget(self.app_bar)

        # Scroll Area for dynamic order history display
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)

        self.display_order_history()

        self.scroll_area.setWidget(self.scroll_content)
        main_layout.addWidget(self.scroll_area)

        main_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        self.setLayout(main_layout)

        # Create the drawer menu
        self.drawer_menu = QMenu(self)
        self.create_drawer_menu()

    def create_app_bar(self):
        self.app_bar = QFrame()
        app_bar_layout = QHBoxLayout()

        # Empty label for spacing on the left
        spacer_left = QLabel()
        app_bar_layout.addWidget(spacer_left)

        # Centered title
        title = QLabel("Order History")
        title.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        title.setStyleSheet("color: white;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        app_bar_layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignCenter)


        spacer_right = QLabel()
        app_bar_layout.addWidget(spacer_right)

        self.app_bar.setLayout(app_bar_layout)
        self.app_bar.setStyleSheet("background-color: #9c2ef0;")

    def create_drawer_menu(self):
        main_menu_action = QAction("Main Menu", self)
        main_menu_action.triggered.connect(self.go_to_main_menu)

        logout_action = QAction("Logout", self)
        logout_action.triggered.connect(self.confirm_logout)

        self.drawer_menu.addAction(main_menu_action)
        self.drawer_menu.addAction(logout_action)

    def show_drawer_menu(self):
        button_position = self.sender().mapToGlobal(QPoint(0, self.sender().height()))
        self.drawer_menu.exec(button_position)

    def fetch_order_history(self):
        return self.db_manager.fetch_user_order_history(self.user_id)

    def display_order_history(self):
        order_history = self.fetch_order_history()
        print(order_history)
        for order in order_history:
            order_box = QFrame(self)
            order_box.setFixedHeight(250)
            order_box.setStyleSheet("background-color: #1A1A3F; color: white; padding: 10px; border-radius: 5px;")
            order_layout = QVBoxLayout(order_box)

            # Vendor and cost
            vendor_label = QLabel(f"<b>{order['vendor_name']}</b>", self)
            vendor_label.setStyleSheet("font-size: 14px; color: white;")
            cost_label = QLabel(f"Rs. {order['total_cost']}", self)
            cost_label.setStyleSheet("font-size: 14px; color: white;")

            # Horizontal layout for vendor and cost
            vendor_cost_layout = QHBoxLayout()
            vendor_cost_layout.addWidget(vendor_label)
            vendor_cost_layout.addStretch()
            vendor_cost_layout.addWidget(cost_label)

            # Order date and status
            date_label = QLabel(f"<i>{order['order_date']}</i>", self)
            date_label.setStyleSheet("font-size: 12px; color: #C0C0C0;")
            status_label = QLabel(f"Status: {order['order_status']}", self)
            status_label.setStyleSheet("font-size: 12px; color: white;")

            # Add components to order_layout
            order_layout.addLayout(vendor_cost_layout)
            order_layout.addWidget(date_label)
            order_layout.addWidget(status_label)

            # "Rate Order" Button
            rate_order_button = QPushButton("Rate Order", self)
            rate_order_button.setFixedHeight(40)
            rate_order_button.setStyleSheet("background-color: #00aaff; color: white; font-weight: bold; padding: 5px;")
            rate_order_button.clicked.connect(lambda checked, order_id=order['order_id']: self.rate_order(order_id))
            order_layout.addWidget(rate_order_button)

            # "View Details" Button
            view_details_button = QPushButton("View Details", self)
            view_details_button.setFixedHeight(40)
            view_details_button.setStyleSheet("background-color: #EDD147; color: white; padding: 5px; font-weight: bold;")
            view_details_button.clicked.connect(lambda checked, order_id=order['order_id']: self.view_order_details(order_id))
            order_layout.addWidget(view_details_button)

            self.scroll_layout.addWidget(order_box)

    def view_order_details(self, order_id):
        from user_order_history import OrderDetailsPopup
        self.hide()
        self.order_detailspop = OrderDetailsPopup(user_id=self.user_id, order_id=order_id)
        self.order_detailspop.show()
    
    def rate_order(self, order_id):
        dialog = QDialog(self)
        dialog.setWindowTitle("Rate Order")
        dialog.setFixedSize(300, 200)
        layout = QVBoxLayout()

        # Rating selection
        label = QLabel("Rate this order (1 to 5):", dialog)
        label.setFont(QFont("Arial", 12))
        combo = QComboBox(dialog)
        combo.addItems([str(i) for i in range(1, 6)])

        # Submit button
        submit_button = QPushButton("Submit", dialog)
        submit_button.clicked.connect(lambda: self.submit_rating(dialog, order_id, int(combo.currentText())))

        layout.addWidget(label)
        layout.addWidget(combo)
        layout.addWidget(submit_button)
        dialog.setLayout(layout)
        dialog.exec()

    def submit_rating(self, dialog, order_id, rating):
        try:
            self.db_manager.add_rating(self.user_id, order_id, rating)
            QMessageBox.information(self, "Success", "Thank you for rating the order!")
            dialog.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not submit rating: {e}")
            dialog.reject()

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
    order_history_screen = OrderHistoryScreen(user_id=1000)
    order_history_screen.show()
    sys.exit(app.exec())
