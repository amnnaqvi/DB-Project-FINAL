from PyQt6 import QtWidgets, QtCore
from PyQt6.QtWidgets import QMainWindow, QLabel, QPushButton, QMessageBox, QToolButton
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

class AdminHome(QMainWindow):
    def __init__(self, ID, name):
        super().__init__()
        self.adminID = ID
        self.adminname = name
        self.setupUi()

    def setupUi(self):
        self.setObjectName('AdminHome')
        self.setWindowTitle("Admin Home")
        self.setFixedSize(600, 700)

        qr = self.frameGeometry()
        cp = QtWidgets.QApplication.primaryScreen().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

        self.setStyleSheet("background-color: #1A1A3F;")

        self.centralwidget = QtWidgets.QWidget(self)
        self.setCentralWidget(self.centralwidget)

        self.welcome_label = QLabel(self.centralwidget)
        self.welcome_label.setGeometry(QtCore.QRect(50, 30, 500, 50))
        self.welcome_label.setText(f"Welcome, {self.adminname}")
        self.welcome_label.setStyleSheet("color: #F0F6FF; font-weight: bold; font-size: 20px; font-family: Arial;")
        self.welcome_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        self.edit_vendors_button = QPushButton(self.centralwidget)
        self.edit_vendors_button.setGeometry(QtCore.QRect(200, 200, 200, 50))
        self.edit_vendors_button.setText('Edit Vendors')
        self.edit_vendors_button.setStyleSheet("background-color: #9C2EF0; color: #F0F6FF; font-size: 14px; font-family: Arial;")
        self.edit_vendors_button.clicked.connect(self.open_update_vendors)

        self.edit_users_button = QPushButton(self.centralwidget)
        self.edit_users_button.setGeometry(QtCore.QRect(200, 300, 200, 50))
        self.edit_users_button.setText('Edit Users')
        self.edit_users_button.setStyleSheet("background-color: #9C2EF0; color: #F0F6FF; font-size: 14px; font-family: Arial;")
        self.edit_users_button.clicked.connect(self.open_update_users)

        if self.adminID == 1:
            self.edit_admin_button = QPushButton(self.centralwidget)
            self.edit_admin_button.setGeometry(QtCore.QRect(200, 400, 200, 50))
            self.edit_admin_button.setText('Edit Admin')
            self.edit_admin_button.setStyleSheet("background-color: #9C2EF0; color: #F0F6FF; font-size: 14px; font-family: Arial;")
            self.edit_admin_button.clicked.connect(self.open_update_admin)

        self.logout_button = QToolButton(self)
        self.logout_button.setText("Logout")
        self.logout_button.setStyleSheet("background-color: #9C2EF0; color: #F0F6FF; font-family: Arial;")
        self.logout_button.setGeometry(40, 20, 60, 30)
        self.logout_button.clicked.connect(self.confirm_logout)

    def open_update_vendors(self):
        from screens.admin_screens.admin_update_vendors import UpdateVendors
        self.hide()
        self.vendorscreen = UpdateVendors(self.adminID, self.adminname)
        self.vendorscreen.show()

    def open_update_users(self):
        from screens.admin_screens.admin_update_users import UpdateUsers
        self.hide()
        self.vendorscreen = UpdateUsers(self.adminID, self.adminname)
        self.vendorscreen.show()

    def open_update_admin(self):
        from screens.admin_screens.admin_update_admin import UpdateAdmin
        self.hide()
        self.vendorscreen = UpdateAdmin(self.adminID, self.adminname)
        self.vendorscreen.show()

    def confirm_logout(self):
        reply = QMessageBox.question(self, 'Logout Confirmation',
                                     "Are you sure you want to logout?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.logout()

    def logout(self):
        from screens.login import LoginScreen 
        self.login_window = LoginScreen()
        self.login_window.show()
        self.close()

def main():
    app = QtWidgets.QApplication(sys.argv)
    window = AdminHome(1, "John Doe")
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
