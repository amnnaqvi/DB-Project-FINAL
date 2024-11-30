from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout, 
    QPushButton, QScrollArea, QMainWindow, QMenu, QFrame, QMessageBox, QToolButton
)
from PyQt6.QtGui import QFont, QAction, QIcon
from PyQt6.QtCore import Qt
from PyQt6 import QtWidgets
import sys
from pathlib import Path
from datetime import datetime

# Add the root directory to sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))
from screens.database import DatabaseManager, get_db_connection


class NotificationScreen(QMainWindow):
    def __init__(self, user_id):
        super().__init__()
        self.setWindowTitle("HU Eats - Notifications")
        self.setFixedSize(600, 700)  # Update screen dimensions to 600x700
        self.user_id = user_id
        print(self.user_id)
        # Initialize database manager
        self.db_manager = DatabaseManager(conn=get_db_connection())

        qr = self.frameGeometry()
        cp = QtWidgets.QApplication.primaryScreen().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

        # Create and set up the UI
        self.create_app_bar()
        self.create_notification_list()
        self.create_more_menu()

        # Set central widget layout
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.app_bar)
        main_layout.addWidget(self.notification_scroll_area)

        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

    def create_app_bar(self):
        self.app_bar = QFrame()
        app_bar_layout = QHBoxLayout()

        title = QLabel("HU_EATS")
        title.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        title.setStyleSheet("color: white;")

        app_bar_layout.addWidget(title)
        app_bar_layout.addStretch()

        self.app_bar.setLayout(app_bar_layout)
        self.app_bar.setStyleSheet("background-color: #9c2ef0;")

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

    def create_notification_list(self):
        # Scrollable notification list
        self.notification_layout = QVBoxLayout()
        self.notification_scroll_area = QScrollArea()
        self.notification_scroll_area.setWidgetResizable(True)

        # Fetch notifications from the database for the user
        notifications = self.fetch_notifications_from_database()

        # Add notification widgets to layout
        for notification in notifications:
            title = notification["title"]
            timestamp = notification["timestamp"].strftime("%I:%M %p")
            self.add_notification_box(title, timestamp)

        notification_widget = QWidget()
        notification_widget.setLayout(self.notification_layout)
        self.notification_scroll_area.setWidget(notification_widget)

    def fetch_notifications_from_database(self):
        """Fetch notifications for the user from the database."""
        notifications = self.db_manager.fetch_user_notifications(self.user_id)
        return [
            {"title": notif[1], "timestamp": notif[3]}  # Assuming (notif_no, message, priority, sent_at)
            for notif in notifications
        ]

    def add_notification_box(self, title, time):
        # Create a single notification box with updated color
        notification_box = QFrame()
        notification_layout = QHBoxLayout()

        title_label = QLabel(title)
        title_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        
        time_label = QLabel(time)
        time_label.setFont(QFont("Arial", 12))

        # Add components to layout
        notification_layout.addWidget(title_label)
        notification_layout.addWidget(time_label)

        notification_box.setFixedHeight(100) 
        notification_box.setLayout(notification_layout)
        notification_box.setStyleSheet("background-color: #1a1a3f; padding: 15px;")

        self.notification_layout.addWidget(notification_box)

    def confirm_logout(self):
        reply = QMessageBox.question(
            self, "Logout", "Are you sure you want to logout?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.logout()

    def logout(self):
        self.hide()
        from screens.login import LoginScreen
        self.login_screen = LoginScreen()
        self.login_screen.show()

    def go_to_main_menu(self):
        from user_main_menu import MainMenuUser
        self.hide()
        self.main_menu = MainMenuUser(self.user_id)
        self.main_menu.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    notification_screen = NotificationScreen(user_id=1003)  # Pass user_id for fetching notifications
    notification_screen.show()
    sys.exit(app.exec())
