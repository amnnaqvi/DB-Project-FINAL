from PyQt6 import QtWidgets, QtCore
from PyQt6.QtWidgets import QMainWindow, QInputDialog, QLabel, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox, QHeaderView,QHBoxLayout
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))
from screens.database import DatabaseManager, get_db_connection

class UpdateAdmin(QMainWindow):
    def __init__(self, adminID, adminname):
        super().__init__()
        self.adminID = adminID
        self.adminname = adminname
        self.db_manager = DatabaseManager(conn=get_db_connection())
        self.setupUi()

    def setupUi(self):
        self.setObjectName('UpdateAdmin')
        self.setWindowTitle("Update Admins")
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
        self.title_label.setText(f"Admin Management - {self.adminname}")
        self.title_label.setStyleSheet(
            "color: #FFFFFF; font-weight: bold; font-size: 20px; font-family: Arial;")
        self.title_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        self.searchBar = QtWidgets.QLineEdit(self.centralwidget)
        self.searchBar.setGeometry(QtCore.QRect(50, 60, 500, 30))
        self.searchBar.setPlaceholderText("Search...")
        self.searchBar.setStyleSheet(
            "font-size: 14px; color: #FFFFFF; background-color: #2A2A5F; padding: 5px; border-radius: 5px;")
        self.searchBar.textChanged.connect(self.filter_admin_table)

        self.admin_table = QTableWidget(self.centralwidget)
        self.admin_table.setGeometry(QtCore.QRect(50, 100, 500, 400))
        self.admin_table.setColumnCount(5)
        self.admin_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.admin_table.verticalHeader().setVisible(False)
        self.admin_table.setStyleSheet("background-color: #1A1A3F; font-family: Arial; font-size: 14px;")
        self.admin_table.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        self.admin_table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.admin_table.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
        self.admin_table.horizontalHeader().setStyleSheet("font-weight: bold; font-size: 14px; color: #1A1A3F;")
        self.populate_admin_table()

        self.add_button = QPushButton(self.centralwidget)
        self.add_button.setGeometry(QtCore.QRect(100, 520, 100, 40))
        self.add_button.setText("Add Admin")
        self.add_button.setStyleSheet("background-color: #9C2EF0; color: #F0F6FF; font-family: Arial;")
        self.add_button.clicked.connect(self.add_admin)

        self.edit_button = QPushButton(self.centralwidget)
        self.edit_button.setGeometry(QtCore.QRect(250, 520, 100, 40))
        self.edit_button.setText("Edit Admin Info")
        self.edit_button.setStyleSheet("background-color: #9C2EF0; color: #F0F6FF; font-family: Arial;")
        self.edit_button.clicked.connect(self.edit_admin)

        self.delete_button = QPushButton(self.centralwidget)
        self.delete_button.setGeometry(QtCore.QRect(400, 520, 100, 40))
        self.delete_button.setText("Toggle Status")
        self.delete_button.setStyleSheet("background-color: #9C2EF0; color: #F0F6FF; font-family: Arial;")
        self.delete_button.clicked.connect(self.delete_admin)

    def populate_admin_table(self):
        try:
            column_names = self.db_manager.get_column_names("Admin")
            self.admin_table.setColumnCount(len(column_names))
            self.admin_table.setHorizontalHeaderLabels(column_names)
            self.admin_table.horizontalHeader().setStyleSheet("QHeaderView::section {background-color: #2A2A5F; color: #FFFFFF; font-weight: bold; font-size: 14px; font-family: Arial; border: 1px solid #4A4A7D;}")
            
            self.admin_data = self.db_manager.view_admin()
            sorted_admin_data = sorted(self.admin_data, key=lambda x: not x[4])
            self.admin_table.setRowCount(len(sorted_admin_data))

            for row, record in enumerate(sorted_admin_data):
                for col, value in enumerate(record):
                    item = QTableWidgetItem(str(value))
                    self.admin_table.setItem(row, col, item)
                    self.admin_table.item(row, col).setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to populate admin table: {str(e)}")
            
    def filter_admin_table(self):
        search_text = self.searchBar.text().strip().lower()
        filtered_data = []
        for record in self.admin_data:
            if any(search_text in str(value).lower() for value in record):
                filtered_data.append(record)

        self.admin_table.setRowCount(len(filtered_data)) 
        self.admin_table.setColumnCount(len(self.admin_data[0])) 

        for row, record in enumerate(filtered_data):
            for col, value in enumerate(record):
                item = QTableWidgetItem(str(value))
                self.admin_table.setItem(row, col, item)
                self.admin_table.item(row, col).setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

    def add_admin(self):
            try:
                new_id = self.db_manager.count_admin()[0][0] + 1
                existing_emails = [record[2].lower() for record in self.admin_data] 

                name, ok1 = QInputDialog.getText(self, "New Admin", "Enter name:")
                while ok1 and (not name.strip() or not name.replace(" ", "").isalnum() or name.isdigit()):
                    if not name.strip():
                        QMessageBox.warning(self, "Input Error", "Name cannot be empty. Please enter a valid name.")
                    elif not name.replace(" ", "").isalnum():
                        QMessageBox.warning(self, "Input Error", "Name can only contain letters, numbers, and spaces.")
                    elif name.isdigit():
                        QMessageBox.warning(self, "Input Error", "Name must include at least one letter.")
                    name, ok1 = QInputDialog.getText(self, "New Admin", "Enter name:")

                if not ok1:
                    return

                email, ok2 = QInputDialog.getText(self, "New Admin", "Enter email (must end with @habib.edu.pk):")
                while ok2 and (not email.strip() or not email.endswith("@habib.edu.pk") or len(email) <= 13 or email.lower() in existing_emails):
                    if not email.strip():
                        QMessageBox.warning(self, "Input Error", "Email cannot be empty. Please enter a valid email.")
                    elif not email.endswith("@habib.edu.pk"):
                        QMessageBox.warning(self, "Input Error", "Email must end with '@habib.edu.pk'.")
                    elif len(email) <= 13:
                        QMessageBox.warning(self, "Input Error", "Email is too short. Please enter a valid email.")
                    elif email.lower() in existing_emails:
                        QMessageBox.warning(self, "Input Error", "This email is already in use. Please enter a unique email.")
                    email, ok2 = QInputDialog.getText(self, "New Admin", "Enter email (must end with @habib.edu.pk):")

                if not ok2:
                    return

                password, ok3 = QInputDialog.getText(self, "New Admin", "Set password:")
                while ok3 and (not password.strip() or len(password) < 8):
                    if not password.strip():
                        QMessageBox.warning(self, "Input Error", "Password cannot be empty. Please enter a valid password.")
                    elif len(password) < 8:
                        QMessageBox.warning(self, "Input Error", "Password must be at least 8 characters long.")
                    password, ok3 = QInputDialog.getText(self, "New Admin", "Set password:")

                if not ok3:
                    return

                result = self.db_manager.add_admin(new_id, name.strip(), email.strip(), password.strip())
                if result:
                    self.populate_admin_table()
                    QMessageBox.information(self, "Success", f"New admin '{name}' added successfully.")
                else:
                    QMessageBox.warning(self, "Failure", f"Failed to add new admin '{name}'. Please try again.")

            except Exception as e:
                QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")


    def edit_admin(self):
        try:
            selected_row = self.admin_table.currentRow()
            if selected_row == -1:
                QMessageBox.warning(self, "No Selection", "Please select an admin to edit.")
                return

            admin_id = int(self.admin_table.item(selected_row, 0).text())

            if admin_id == 1:
                QMessageBox.warning(self, "Error", "Cannot edit the admin with ID 1.")
                return

            current_name = self.admin_table.item(selected_row, 1).text()
            current_email = self.admin_table.item(selected_row, 2).text()
            current_pass = self.admin_table.item(selected_row, 3).text()

            existing_emails = [record[2].lower() for record in self.admin_data if record[0] != admin_id]

            new_name, ok1 = QInputDialog.getText(self, "Edit Admin", "Enter new name:", text=current_name)
            while ok1 and (
                not new_name.strip() or
                not new_name.replace(" ", "").isalnum() or
                new_name.isdigit()
            ):
                if not new_name.strip():
                    QMessageBox.warning(self, "Input Error", "Name cannot be empty. Please enter a valid name.")
                elif not new_name.replace(" ", "").isalnum():
                    QMessageBox.warning(self, "Input Error", "Name can only contain letters, numbers, and spaces.")
                elif new_name.isdigit():
                    QMessageBox.warning(self, "Input Error", "Name must include at least one letter.")
                new_name, ok1 = QInputDialog.getText(self, "Edit Admin", "Enter new name:", text=current_name)

            if not ok1:
                return

            new_email, ok2 = QInputDialog.getText(self, "Edit Admin", "Enter new email (must end with @habib.edu.pk):", text=current_email)
            while ok2 and (not new_email.strip() or not new_email.endswith("@habib.edu.pk") or len(new_email) <= 13 or new_email.lower() in existing_emails):
                if not new_email.strip():
                    QMessageBox.warning(self, "Input Error", "Email cannot be empty. Please enter a valid email.")
                elif not new_email.endswith("@habib.edu.pk"):
                    QMessageBox.warning(self, "Input Error", "Email must end with '@habib.edu.pk'.")
                elif len(new_email) <= 13:
                    QMessageBox.warning(self, "Input Error", "Email is too short. Please enter a valid email.")
                elif new_email.lower() in existing_emails:
                    QMessageBox.warning(self, "Input Error", "This email is already in use. Please enter a unique email.")
                new_email, ok2 = QInputDialog.getText(self, "Edit Admin", "Enter new email (must end with @habib.edu.pk):", text=current_email)

            if not ok2:
                return

            new_password, ok3 = QInputDialog.getText(self, "Edit Admin", "Set new password:", text=current_pass)
            while ok3 and (not new_password.strip() or len(new_password) < 8):
                if not new_password.strip():
                    QMessageBox.warning(self, "Input Error", "Password cannot be empty. Please enter a valid password.")
                elif len(new_password) < 8:
                    QMessageBox.warning(self, "Input Error", "Password must be at least 8 characters long.")
                new_password, ok3 = QInputDialog.getText(self, "Edit Admin", "Set new password:", text=current_pass)

            if not ok3:
                return

            result = self.db_manager.edit_admin(admin_id, new_name.strip(), new_email.strip(), new_password.strip())
            if result:
                self.populate_admin_table()
                QMessageBox.information(self, "Success", f"Admin with ID {admin_id} updated successfully.")
            else:
                QMessageBox.warning(self, "Failure", f"Failed to update admin with ID {admin_id}. Please try again.")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")


    def delete_admin(self):
        selected_row = self.admin_table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "No Selection", "Please select an admin.")
            return
        
        admin_id = int(self.admin_table.item(selected_row, 0).text())
        
        if admin_id == 1:
            QMessageBox.warning(self, "Error", "Cannot delete the admin with ID 1.")
            return
        
        current_status = self.admin_table.item(selected_row, 4).text()

        new_status = 0 if current_status == "True" else 1
        action = "disable" if new_status == 0 else "enable"

        reply = QMessageBox.question(self, "Confirm Action",
                                    f"Are you sure you want to {action} this admin?",
                                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            result = self.db_manager.update_admin_status(admin_id, new_status)
            if result:
                self.populate_admin_table()
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
    window = UpdateAdmin(1, "John Doe")
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
