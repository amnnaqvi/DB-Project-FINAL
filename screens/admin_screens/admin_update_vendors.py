from PyQt6 import QtWidgets, QtCore
from PyQt6.QtWidgets import QMainWindow, QInputDialog, QLabel, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox, QHeaderView,QHBoxLayout
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))
from screens.database import DatabaseManager, get_db_connection

class UpdateVendors(QMainWindow):
    def __init__(self, adminID, adminname):
        super().__init__()
        self.adminID = adminID
        self.adminname = adminname
        self.db_manager = DatabaseManager(conn=get_db_connection())
        self.setupUi()

    def setupUi(self):
        self.setObjectName('UpdateVendors')
        self.setWindowTitle("Update Vendors")
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
        self.title_label.setText(f"Vendor Management - {self.adminname}")
        self.title_label.setStyleSheet(
            "color: #FFFFFF; font-weight: bold; font-size: 20px; font-family: Arial;")
        self.title_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        self.searchBar = QtWidgets.QLineEdit(self.centralwidget)
        self.searchBar.setGeometry(QtCore.QRect(50, 60, 500, 30))
        self.searchBar.setPlaceholderText("Search...")
        self.searchBar.setStyleSheet(
            "font-size: 14px; color: #FFFFFF; background-color: #2A2A5F; padding: 5px; border-radius: 5px;")
        self.searchBar.textChanged.connect(self.filter_vendor_table)

        self.vendor_table = QTableWidget(self.centralwidget)
        self.vendor_table.setGeometry(QtCore.QRect(50, 100, 500, 400))
        self.vendor_table.setColumnCount(5)
        self.vendor_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.vendor_table.verticalHeader().setVisible(False)
        self.vendor_table.setStyleSheet("background-color: #1A1A3F; font-family: Arial; font-size: 14px;")
        self.vendor_table.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        self.vendor_table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.vendor_table.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
        self.vendor_table.horizontalHeader().setStyleSheet("font-weight: bold; font-size: 14px; color: #1A1A3F;")
        self.populate_vendor_table()

        self.add_button = QPushButton(self.centralwidget)
        self.add_button.setGeometry(QtCore.QRect(100, 520, 100, 40))
        self.add_button.setText("Add Vendor")
        self.add_button.setStyleSheet("background-color: #9C2EF0; color: #F0F6FF; font-family: Arial;")
        self.add_button.clicked.connect(self.add_vendor)

        self.edit_button = QPushButton(self.centralwidget)
        self.edit_button.setGeometry(QtCore.QRect(250, 520, 100, 40))
        self.edit_button.setText("Edit Vendor Info")
        self.edit_button.setStyleSheet("background-color: #9C2EF0; color: #F0F6FF; font-family: Arial;")
        self.edit_button.clicked.connect(self.edit_vendor)

        self.delete_button = QPushButton(self.centralwidget)
        self.delete_button.setGeometry(QtCore.QRect(400, 520, 100, 40))
        self.delete_button.setText("Toggle Status")
        self.delete_button.setStyleSheet("background-color: #9C2EF0; color: #F0F6FF; font-family: Arial;")
        self.delete_button.clicked.connect(self.delete_vendor)

    def populate_vendor_table(self):
        self.vendor_data = self.db_manager.view_vendors()
        sorted_vendor_data = sorted(self.vendor_data, key=lambda x: not x[4])
        self.vendor_table.setRowCount(len(sorted_vendor_data))
        self.vendor_table.setColumnCount(len(self.vendor_data[0]))
        
        for row, record in enumerate(sorted_vendor_data):
            for col, value in enumerate(record):
                item = QTableWidgetItem(str(value))
                self.vendor_table.setItem(row, col, item)
                self.vendor_table.item(row, col).setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

    def filter_vendor_table(self):
        search_text = self.searchBar.text().strip().lower()
        filtered_data = []
        for record in self.vendor_data:
            if any(search_text in str(value).lower() for value in record):
                filtered_data.append(record)

        self.vendor_table.setRowCount(len(filtered_data)) 
        self.vendor_table.setColumnCount(len(self.vendor_data[0])) 

        for row, record in enumerate(filtered_data):
            for col, value in enumerate(record):
                item = QTableWidgetItem(str(value))
                self.vendor_table.setItem(row, col, item)
                self.vendor_table.item(row, col).setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

    def add_vendor(self):
        try:
            new_id = self.db_manager.count_vendors()[0][0] + 1

            name, ok1 = QInputDialog.getText(self, "New Vendor", "Enter Name:")
            while ok1 and not name.strip(): 
                QMessageBox.warning(self, "Input Error", "Name cannot be empty. Please try again.")
                name, ok1 = QInputDialog.getText(self, "New Vendor", "Enter Name:")

            if not ok1: 
                return
            
            img, ok1 = QInputDialog.getText(self, "New Vendor", "Enter Image Path:")
            while ok1 and not img.strip(): 
                QMessageBox.warning(self, "Input Error", "Image Path cannot be empty. Please try again.")
                img, ok1 = QInputDialog.getText(self, "New Vendor", "Enter Image Path:")

            if not ok1: 
                return
            
            password, ok1 = QInputDialog.getText(self, "New Vendor", "Set password:")
            while ok1 and not password.strip():
                QMessageBox.warning(self, "Input Error", "Password cannot be empty. Please try again.")
                password, ok1 = QInputDialog.getText(self, "New Vendor", "Set password:")

            if not ok1: 
                return
            
            contact, ok1 = QInputDialog.getText(self, "New Vendor", "Enter Contact Info:")
            while ok1 and not contact.strip(): 
                QMessageBox.warning(self, "Input Error", "Contact cannot be empty. Please try again.")
                contact, ok1 = QInputDialog.getText(self, "New Vendor", "Enter Contact Info:")

            if not ok1: 
                return

            email, ok1 = QInputDialog.getText(self, "New Vendor", "Enter email (must end with @habib.edu.pk):")
            while ok1 and (not email.strip() or not email.endswith("@habib.edu.pk") or not len(email) > 13):
                QMessageBox.warning(self, "Input Error", "Invalid email. Please ensure it ends with '@habib.edu.pk'.")
                email, ok1 = QInputDialog.getText(self, "New Vendor", "Enter email (must end with @habib.edu.pk):")

            if not ok1: 
                return

            result = self.db_manager.add_vendors(new_id, name.strip(), img.strip(), password.strip(), contact.strip(), email.strip(), self.adminID)
            if result:
                self.populate_vendor_table() 
                QMessageBox.information(self, "Success", f"New vendor '{name}' added successfully.")
            else:
                QMessageBox.warning(self, "Failure", f"Failed to add new vendor '{name}'. Please try again.")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")

    def edit_vendor(self):
        try:
            selected_row = self.vendor_table.currentRow()
            if selected_row == -1:
                QMessageBox.warning(self, "No Selection", "Please select a vendor to edit.")
                return

            vendor_id = int(self.vendor_table.item(selected_row, 0).text())

            current_name = self.vendor_table.item(selected_row, 1).text()
            current_image = self.vendor_table.item(selected_row, 2).text()
            current_pass = self.vendor_table.item(selected_row, 3).text()
            current_contact = self.vendor_table.item(selected_row, 4).text()
            current_email = self.vendor_table.item(selected_row, 5).text()
            admin_id = int(self.vendor_table.item(selected_row, 6).text())


            name, ok1 = QInputDialog.getText(self, "Edit Vendor", "Enter new name:", text=current_name)
            while ok1 and not name.strip():
                QMessageBox.warning(self, "Input Error", "Name cannot be empty. Please try again.")
                name, ok1 = QInputDialog.getText(self, "Edit Vendor", "Enter new name:", text=current_name)

            if not ok1:
                return
            
            img, ok1 = QInputDialog.getText(self, "New Vendor", "Enter Image Path:", text=current_image)
            while ok1 and not img.strip(): 
                QMessageBox.warning(self, "Input Error", "Image Path cannot be empty. Please try again.")
                img, ok1 = QInputDialog.getText(self, "New Vendor", "Enter Image Path:", text=current_image)

            if not ok1: 
                return
            
            password, ok1 = QInputDialog.getText(self, "New Vendor", "Set password:", text=current_pass)
            while ok1 and not password.strip():
                QMessageBox.warning(self, "Input Error", "Password cannot be empty. Please try again.")
                password, ok1 = QInputDialog.getText(self, "New Vendor", "Set password:", text=current_pass)

            if not ok1: 
                return
            
            contact, ok1 = QInputDialog.getText(self, "New Vendor", "Enter Contact Info:", text=current_contact)
            while ok1 and not contact.strip(): 
                QMessageBox.warning(self, "Input Error", "Contact cannot be empty. Please try again.")
                contact, ok1 = QInputDialog.getText(self, "New Vendor", "Enter Contact Info:", text=current_contact)

            if not ok1: 
                return

            email, ok1 = QInputDialog.getText(self, "New Vendor", "Enter email (must end with @habib.edu.pk):", text=current_email)
            while ok1 and (not email.strip() or not email.endswith("@habib.edu.pk") or not len(email) > 13):
                QMessageBox.warning(self, "Input Error", "Invalid email. Please ensure it ends with '@habib.edu.pk'.")
                email, ok1 = QInputDialog.getText(self, "New Vendor", "Enter email (must end with @habib.edu.pk):", text=current_email)

            if not ok1: 
                return

            result = self.db_manager.edit_vendors(vendor_id, name.strip(), img.strip(), password.strip(), contact.strip(), email.strip(), self.adminID)
            if result:
                self.populate_vendor_table()
                QMessageBox.information(self, "Success", f"Vendor with ID {vendor_id} updated successfully.")
            else:
                QMessageBox.warning(self, "Failure", f"Failed to update vendor with ID {vendor_id}. Please try again.")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")

    def delete_vendor(self):
        selected_row = self.vendor_table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "No Selection", "Please select an admin to delete.")
            return
        
        vendor_id = int(self.vendor_table.item(selected_row, 0).text())
        
        current_status = self.vendor_table.item(selected_row, 4).text()

        new_status = 0 if current_status == "True" else 1
        action = "disable" if new_status == 0 else "enable"

        reply = QMessageBox.question(self, "Confirm Action",
                                    f"Are you sure you want to {action} this admin?",
                                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            result = self.db_manager.update_vendors_status(vendor_id, new_status)
            if result:
                self.populate_vendor_table()
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
    window = UpdateVendors(1, "John Doe")
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
