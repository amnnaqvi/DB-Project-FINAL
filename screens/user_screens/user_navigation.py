# user_navigation.py
import sys
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6 import QtWidgets
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

class UserNavigation:
    _instance = None

    qr = self.frameGeometry()
    cp = QtWidgets.QApplication.primaryScreen().availableGeometry().center()
    qr.moveCenter(cp)
    self.move(qr.topLeft())

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(UserNavigation, cls).__new__(cls)
            cls._instance.current_screen = None
            cls._instance.user_id = None
        return cls._instance

    def set_user_id(self, user_id):
        """Set the user_id for navigation use."""
        self.user_id = user_id

    def open_main_menu(self):
        from user_main_menu import MainMenuUser
        self._show_screen(MainMenuUser(self.user_id))

    def open_notifications(self):
        from user_notifications import NotificationScreen
        self._show_screen(NotificationScreen(self.user_id))

    def open_order_history(self):
        from user_all_order_history import OrderHistoryScreen
        self._show_screen(OrderHistoryScreen(self.user_id))

    def open_balance_history(self):
        from user_balance_history import UserBalanceHistory
        self._show_screen(UserBalanceHistory(self.user_id))

    def open_favorites(self):
        from user_favorites import FavoritesScreen
        self._show_screen(FavoritesScreen(self.user_id))

    def open_cart(self):
        from user_cart_view import UserCartScreen
        self._show_screen(UserCartScreen(self.user_id))

    def logout(self):
        """Logout user and show the login screen."""
        reply = QMessageBox.question(None, "Logout", "Are you sure you want to logout?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            from screens.login import LoginScreen
            self.current_screen = LoginScreen()
            self.current_screen.show()

    def _show_screen(self, screen_instance):
        """Helper function to display the screen and manage transitions."""
        if self.current_screen is not None:
            self.current_screen.close()
        self.current_screen = screen_instance
        self.current_screen.show()

# Example of initializing the application with UserNavigation and user_id
if __name__ == "__main__":
    app = QApplication(sys.argv)
    navigator = UserNavigation()
    navigator.set_user_id(1000)  # Assuming user_id is fetched after login
    navigator.open_main_menu()  # Starting with the main menu
    sys.exit(app.exec())
