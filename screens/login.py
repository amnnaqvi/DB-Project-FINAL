import sys
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QMessageBox
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
from pathlib import Path

# Add the root directory to sys.path
sys.path.append(str(Path(__file__).resolve().parent))
sys.path.append(str(Path(__file__).resolve().parent / 'user_screens')) 
from database import get_db_connection, DatabaseManager

class LoginScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("HU Eats - Login")
        self.setFixedSize(400, 300)

        # Initialize database connection
        self.conn = get_db_connection()
        self.db_manager = DatabaseManager(self.conn)

        # Create UI elements
        self.create_app_bar()
        self.create_login_form()

    def create_app_bar(self):
        app_bar_layout = QHBoxLayout()
        app_bar_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        app_bar_label = QLabel("HU_EATS")
        app_bar_label.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        app_bar_label.setStyleSheet("color: white;")
        app_bar_layout.addWidget(app_bar_label)

        self.app_bar_widget = QWidget()
        self.app_bar_widget.setLayout(app_bar_layout)
        self.app_bar_widget.setStyleSheet("background-color: #9c2ef0;")

    def create_login_form(self):
        form_layout = QVBoxLayout()
        form_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Email")
        self.email_input.setFont(QFont("Arial", 12))

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setFont(QFont("Arial", 12))
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

        login_button = QPushButton("Login")
        login_button.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        login_button.clicked.connect(self.handle_login)

        form_layout.addWidget(self.email_input)
        form_layout.addWidget(self.password_input)
        form_layout.addWidget(login_button)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.app_bar_widget)
        main_layout.addStretch(1)
        main_layout.addLayout(form_layout)
        main_layout.addStretch(2)

        self.setLayout(main_layout)

    def handle_login(self):
        try:
            email = self.email_input.text().strip()
            password = self.password_input.text().strip()

            # Ensure both email and password are provided
            if not email or not password:
                QMessageBox.warning(self, "Input Error", "Please enter both email and password.")
                return

            # Check email format
            if not email.endswith("habib.edu.pk"):
                QMessageBox.warning(self, "Invalid Email", "Email must end with 'habib.edu.pk'.")
                return

            # Check credentials in the Users table
            user_info = self.db_manager.get_user_info_login(email)
            if user_info:
                user_id, user_stored_password, user_active = user_info
                if user_active and password == user_stored_password:
                    self.redirect_to_user_menu(user_id)
                    return
                else:
                    QMessageBox.warning(self, "Login Failed", "Inactive account or incorrect password.")
                    return

            # Check credentials in the Admin table
            admin_info = self.db_manager.get_admin_info_login(email)
            if admin_info:
                admin_id, admin_stored_password, name = admin_info
                if password == admin_stored_password:
                    self.redirect_to_admin_menu(admin_id, name)
                    return
                else:
                    QMessageBox.warning(self, "Login Failed", "Incorrect password.")
                    return

            # Check credentials in the Vendors table
            vendor_info = self.db_manager.get_vendor_info_login(email)
            if vendor_info:
                vendor_id, vendor_stored_password, vendor_active = vendor_info
                if vendor_active and password == vendor_stored_password:
                    self.redirect_to_vendor_menu(vendor_id)
                    return
                else:
                    QMessageBox.warning(self, "Login Failed", "Inactive account or incorrect password.")
                    return

            QMessageBox.warning(self, "Login Failed", "Invalid email or user not found.")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"An unexpected error occurred: {e}")
            print(f"Login error: {e}")

    def redirect_to_user_menu(self, user_id):
        from user_screens.user_main_menu import MainMenuUser
        self.hide()
        self.main_menu = MainMenuUser(user_id)
        self.main_menu.show()

    def redirect_to_admin_menu(self, admin_id, name):
        from admin_screens.admin_home import AdminHome
        self.hide()
        self.main_menu = AdminHome(admin_id, name)
        self.main_menu.show()

    def redirect_to_vendor_menu(self, vendor_id):
        from vendor_screens.vendor_home import AdminHome
        self.hide()
        self.main_menu = AdminHome(vendor_id)
        self.main_menu.show()
        

if __name__ == "__main__":
    app = QApplication(sys.argv)
    login_screen = LoginScreen()
    login_screen.show()
    sys.exit(app.exec())
