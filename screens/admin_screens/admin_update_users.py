from PyQt6 import QtWidgets, QtCore
from PyQt6.QtWidgets import QMainWindow, QInputDialog, QLabel, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox, QHeaderView,QHBoxLayout
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))
from screens.database import DatabaseManager, get_db_connection

class UpdateUsers(QMainWindow):
    def __init__(self, adminID, adminname):
        super().__init__()
        self.adminID = adminID
        self.adminname = adminname
        self.db_manager = DatabaseManager(conn=get_db_connection())
        self.setupUi()

    def setupUi(self):
        self.setObjectName('UpdateUser')
        self.setWindowTitle("Update Users")
        self.setFixedSize(600, 700)

        qr = self.frameGeometry()
        cp = QtWidgets.QApplication.primaryScreen().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

        self.setStyleSheet("background-color: #1A1A3F;")

        self.centralwidget = QtWidgets.QWidget(self)
        self.setCentralWidget(self.centralwidget)

        self.button_widget = QtWidgets.QWidget(self.centralwidget)
        self.button_widget.setGeometry(QtCore.QRect(40, 580, 500, 60))
        self.button_layout = QHBoxLayout(self.button_widget)

        self.return_button = QPushButton("Return to Main Menu", self.button_widget)
        self.return_button.setStyleSheet(
            "background-color: #9C2EF0; color: #FFFFFF; font-size: 14px; font-family: Arial; padding: 5px;")
        self.return_button.clicked.connect(self.return_to_main)

        self.logout_button = QPushButton("Logout", self.button_widget)
        self.logout_button.setStyleSheet(
            "background-color: #9C2EF0; color: #FFFFFF; font-size: 14px; font-family: Arial; padding: 5px;")
        self.logout_button.clicked.connect(self.logout)

        self.button_layout.addWidget(self.return_button)
        self.button_layout.addWidget(self.logout_button)

        self.title_label = QLabel(self.centralwidget)
        self.title_label.setGeometry(QtCore.QRect(50, 5, 500, 50))
        self.title_label.setText(f"User Management - {self.adminname}")
        self.title_label.setStyleSheet(
            "color: #FFFFFF; font-weight: bold; font-size: 20px; font-family: Arial;")
        self.title_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        self.searchBar = QtWidgets.QLineEdit(self.centralwidget)
        self.searchBar.setGeometry(QtCore.QRect(50, 60, 500, 30))
        self.searchBar.setPlaceholderText("Search...")
        self.searchBar.setStyleSheet(
            "font-size: 14px; color: #FFFFFF; background-color: #2A2A5F; padding: 5px; border-radius: 5px;")
        self.searchBar.textChanged.connect(self.filter_user_table)

        self.user_table = QTableWidget(self.centralwidget)
        self.user_table.setGeometry(QtCore.QRect(50, 100, 500, 400))
        self.user_table.setColumnCount(5)
        self.user_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.user_table.verticalHeader().setVisible(False)
        self.user_table.setStyleSheet("background-color: #1A1A3F; font-family: Arial; font-size: 14px;")
        self.user_table.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        self.user_table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.user_table.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
        self.user_table.horizontalHeader().setStyleSheet("font-weight: bold; font-size: 14px; color: #1A1A3F;")
        self.populate_user_table()

        self.add_button = QPushButton(self.centralwidget)
        self.add_button.setGeometry(QtCore.QRect(100, 520, 100, 40))
        self.add_button.setText("Add User")
        self.add_button.setStyleSheet("background-color: #9C2EF0; color: #F0F6FF; font-family: Arial;")
        self.add_button.clicked.connect(self.add_user)

        self.edit_button = QPushButton(self.centralwidget)
        self.edit_button.setGeometry(QtCore.QRect(250, 520, 100, 40))
        self.edit_button.setText("Edit User Info")
        self.edit_button.setStyleSheet("background-color: #9C2EF0; color: #F0F6FF; font-family: Arial;")
        self.edit_button.clicked.connect(self.edit_user)

        self.delete_button = QPushButton(self.centralwidget)
        self.delete_button.setGeometry(QtCore.QRect(400, 520, 100, 40))
        self.delete_button.setText("Toggle Status")
        self.delete_button.setStyleSheet("background-color: #9C2EF0; color: #F0F6FF; font-family: Arial;")
        self.delete_button.clicked.connect(self.delete_user)

    def populate_user_table(self):
        self.user_data = self.db_manager.view_users()
        sorted_user_data = sorted(self.user_data, key=lambda x: not x[6])
        self.user_table.setRowCount(len(sorted_user_data))
        self.user_table.setColumnCount(len(self.user_data[0]))
        
        for row, record in enumerate(sorted_user_data):
            for col, value in enumerate(record):
                item = QTableWidgetItem(str(value))
                self.user_table.setItem(row, col, item)
                self.user_table.item(row, col).setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

    def filter_user_table(self):
        search_text = self.searchBar.text().strip().lower()
        filtered_data = []
        for record in self.user_data:
            if any(search_text in str(value).lower() for value in record):
                filtered_data.append(record)

        self.user_table.setRowCount(len(filtered_data)) 
        self.user_table.setColumnCount(len(self.user_data[0])) 

        for row, record in enumerate(filtered_data):
            for col, value in enumerate(record):
                item = QTableWidgetItem(str(value))
                self.user_table.setItem(row, col, item)
                self.user_table.item(row, col).setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

    def add_user(self):
        try:
            new_id = self.db_manager.count_users()[0][0] + 1

            name, ok1 = QInputDialog.getText(self, "New User", "Enter Full Name:")
            while ok1 and not name.strip(): 
                QMessageBox.warning(self, "Input Error", "Name cannot be empty. Please try again.")
                name, ok1 = QInputDialog.getText(self, "New User", "Enter Full Name:")

            if not ok1: 
                return
            
            type, ok1 = QInputDialog.getInt(self, "New User", "Enter Type - 1 for Student, 2 for Faculty, 3 for Staff:")
            while ok1 and not type in [1, 2, 3]: 
                QMessageBox.warning(self, "Input Error", "Please try again.")
                type, ok1 = QInputDialog.getInt(self, "New User", "Enter Type - 1 for Student, 2 for Faculty, 3 for Staff:")

            if not ok1: 
                return

            email, ok1 = QInputDialog.getText(self, "New User", "Enter email (must end with habib.edu.pk):")
            while ok1 and (not email.strip() or not email.endswith("habib.edu.pk") or not len(email) > 12):
                QMessageBox.warning(self, "Input Error", "Invalid email. Please ensure it ends with '.habib.edu.pk'.")
                email, ok1 = QInputDialog.getText(self, "New User", "Enter email (must end with habib.edu.pk):")

            if not ok1: 
                return

            password, ok1 = QInputDialog.getText(self, "New User", "Set password:")
            while ok1 and not password.strip():
                QMessageBox.warning(self, "Input Error", "Password cannot be empty. Please try again.")
                password, ok1 = QInputDialog.getText(self, "New User", "Set password:")

            if not ok1: 
                return

            result = self.db_manager.add_users(new_id, name.strip(), type, email.strip(), password.strip())
            if result:
                self.populate_user_table() 
                QMessageBox.information(self, "Success", f"New user '{name}' added successfully.")
            else:
                QMessageBox.warning(self, "Failure", f"Failed to add new user '{name}'. Please try again.")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")

    def edit_user(self):
        try:
            selected_row = self.user_table.currentRow()
            if selected_row == -1:
                QMessageBox.warning(self, "No Selection", "Please select a user to edit.")
                return

            user_id = int(self.user_table.item(selected_row, 0).text())

            current_name = self.user_table.item(selected_row, 1).text()
            current_type = int(self.user_table.item(selected_row, 2).text())
            current_bal = float(self.user_table.item(selected_row, 3).text())
            current_email = self.user_table.item(selected_row, 4).text()
            current_pass = self.user_table.item(selected_row, 5).text()

            new_name, ok1 = QInputDialog.getText(self, "Edit User", "Enter new name:", text=current_name)
            while ok1 and not new_name.strip():
                QMessageBox.warning(self, "Input Error", "Name cannot be empty. Please try again.")
                new_name, ok1 = QInputDialog.getText(self, "Edit User", "Enter new name:", text=current_name)

            if not ok1:
                return
            
            new_type, ok1 = QInputDialog.getInt(self, "Edit User", "Enter new type - 1 for Student, 2 for Faculty, 3 for Staff:", value=current_type)
            while ok1 and not new_type in [1, 2, 3]:
                QMessageBox.warning(self, "Input Error", "Please try again.")
                new_type, ok1 = QInputDialog.getInt(self, "Edit User", "Enter new type - 1 for Student, 2 for Faculty, 3 for Staff:", value=current_type)

            if not ok1:
                return
            
            deposit_amount, ok1 = QInputDialog.getInt(self, "Edit User", "Enter deposit amount:", min=1)
            while ok1 and deposit_amount < 0:
                QMessageBox.warning(self, "Input Error", "Deposit amount must be greater than 0. Please try again.")
                deposit_amount, ok1 = QInputDialog.getInt(self, "Edit User", "Enter deposit amount:", min=1)

            if not ok1:
                return

            new_bal = current_bal + deposit_amount

            new_email, ok1 = QInputDialog.getText(self, "Edit User", "Enter new email (must end with habib.edu.pk):", text=current_email)
            while ok1 and (not new_email.strip() or not new_email.endswith("habib.edu.pk") or len(new_email) <= 12):
                QMessageBox.warning(self, "Input Error", "Invalid email. Please ensure it ends with '@habib.edu.pk'.")
                new_email, ok1 = QInputDialog.getText(self, "Edit User", "Enter new email (must end with habib.edu.pk):", text=current_email)

            if not ok1:
                return

            new_password, ok1 = QInputDialog.getText(self, "Edit User", "Set new password:", text=current_pass)
            while ok1 and not new_password.strip():
                QMessageBox.warning(self, "Input Error", "Password cannot be empty. Please try again.")
                new_password, ok1 = QInputDialog.getText(self, "Edit User", "Set new password:", text=current_pass)

            if not ok1:
                return
            
            result1 = self.db_manager.update_users_balance(user_id, deposit_amount, self.adminID)
            result2 = self.db_manager.edit_users(user_id, new_name.strip(), new_type, new_bal, new_email.strip(), new_password.strip())
            if not result1:
                QMessageBox.warning(self, "Failure", f"Failed to update the user's balance. Please try again.")
            elif not result2:
                QMessageBox.warning(self, "Failure", f"Failed to update user details. Please try again.")
            else:
                self.populate_user_table()
                QMessageBox.information(self, "Success", f"User with ID {user_id} updated successfully.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")

    def delete_user(self):
        selected_row = self.user_table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "No Selection", "Please select an admin to delete.")
            return
        
        user_id = int(self.user_table.item(selected_row, 0).text())
        
        current_status = self.user_table.item(selected_row, 6).text()

        new_status = 0 if current_status == "True" else 1
        action = "disable" if new_status == 0 else "enable"

        reply = QMessageBox.question(self, "Confirm Action",
                                    f"Are you sure you want to {action} this admin?",
                                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            result = self.db_manager.update_users_status(user_id, new_status)
            if result:
                self.populate_user_table()
                QMessageBox.information(self, "Success", f"Admin successfully {action}d.")
            else:
                QMessageBox.warning(self, "Error", f"Failed to {action} the admin. Please try again.")


    def return_to_main(self):
        from screens.admin_screens.admin_home import AdminHome
        self.main_menu = AdminHome(self.adminID, self.adminname)
        self.main_menu.show()
        self.close()

    def logout(self):
        from screens.login import LoginScreen
        self.login_screen = LoginScreen()
        self.login_screen.show()
        self.close()

def main():
    app = QtWidgets.QApplication(sys.argv)
    window = UpdateUsers(1, "John Doe")
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
