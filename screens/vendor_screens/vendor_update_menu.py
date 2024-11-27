from PyQt6 import QtWidgets, QtCore
from PyQt6.QtWidgets import QMainWindow, QLabel, QInputDialog, QMessageBox, QPushButton, QScrollArea, QVBoxLayout, QHBoxLayout, QWidget, QFrame, QGridLayout
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))
from screens.database import DatabaseManager, get_db_connection

class UpdateMenu(QMainWindow):
    def __init__(self, ID, name):
        super().__init__()
        self.setWindowTitle("Update Menu")
        self.setFixedSize(600, 700)
        self.setStyleSheet("background-color: #1A1A3F;")
        self.vendor_id = ID
        self.vendorname = name
        self.db_manager = DatabaseManager(conn=get_db_connection())

        qr = self.frameGeometry()
        cp = QtWidgets.QApplication.primaryScreen().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

        # Main layout
        self.centralwidget = QWidget(self)
        self.setCentralWidget(self.centralwidget)
        layout = QVBoxLayout(self.centralwidget)

        # Top button layout for Main Menu and Logout buttons
        left_button_layout = QVBoxLayout()
        
        # Main Menu button
        self.return_button = QPushButton("Main Menu", self.centralwidget)
        self.return_button.setStyleSheet("background-color: #9C2EF0; color: #FFFFFF; font-size: 14px; font-family: Arial;")
        self.return_button.clicked.connect(self.return_to_main)
        
        # Logout button positioned below the Main Menu button
        self.logout_button = QPushButton("Logout", self.centralwidget)
        self.logout_button.setStyleSheet("background-color: #9C2EF0; color: #FFFFFF; font-size: 14px; font-family: Arial;")
        self.logout_button.clicked.connect(self.logout)
        
        left_button_layout.addWidget(self.return_button)
        left_button_layout.addWidget(self.logout_button)

        # Top bar layout for left buttons and right-aligned "+" button
        top_bar_layout = QHBoxLayout()
        top_bar_layout.addLayout(left_button_layout)
        top_bar_layout.addStretch()

        # "+" Button to add a new item
        self.add_item_button = QPushButton("+", self.centralwidget)
        self.add_item_button.setFixedSize(40, 40)
        self.add_item_button.setStyleSheet(
            "background-color: #9C2EF0; color: #FFFFFF; font-size: 20px; font-weight: bold; "
            "border-radius: 20px;")
        self.add_item_button.setToolTip("Add New Item")
        self.add_item_button.clicked.connect(self.open_add_item_window)
        top_bar_layout.addWidget(self.add_item_button, alignment=QtCore.Qt.AlignmentFlag.AlignRight)

        layout.addLayout(top_bar_layout)

        # Title Label
        self.titleLabel = QLabel("Update Menu", self.centralwidget)
        self.titleLabel.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.titleLabel.setStyleSheet("color: #F0F6FF; font-weight: bold; font-size: 18px; font-family: Arial;")
        layout.addWidget(self.titleLabel)

        # Search Bar
        self.searchBar = QtWidgets.QLineEdit(self.centralwidget)
        self.searchBar.setPlaceholderText("Search by Name or ID")
        self.searchBar.setStyleSheet("font-size: 12px; color: #FFFFFF;")
        layout.addWidget(self.searchBar)

        # Scroll area for item grid
        scroll_area = QScrollArea(self.centralwidget)
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOn)

        # Widget to contain item grid
        self.grid_content = QWidget()
        self.grid_layout = QGridLayout(self.grid_content)
        self.grid_layout.setSpacing(10)
        scroll_area.setWidget(self.grid_content)
        layout.addWidget(scroll_area)

        # Sample Data for items (for demonstration purposes)

        # Populate the item Grid
        self.populate_item_grid()

        # Connect search bar text change to update item grid
        self.searchBar.textChanged.connect(self.update_item_grid)

    def populate_item_grid(self):
        """Create a grid layout with item details and edit buttons, displaying only active items."""
        # Clear existing widgets in the grid
        self.items = self.fetch_menu_items()
        self.filtered_items = self.items[:]
        for i in reversed(range(self.grid_layout.count())):
            widget = self.grid_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        # Filter for active items and display up to 5 at a time
        for row, item in enumerate(self.items[:]):
            # item information display
            self.grid_layout.setRowMinimumHeight(row, 50)
            id_label = QLabel(f"ID: {item['id']}", self.grid_content)
            id_label.setStyleSheet("color: #FFFFFF; font-size: 12px;")
            name_label = QLabel(f"{item['name']}", self.grid_content)
            name_label.setStyleSheet("color: #FFFFFF; font-size: 12px;")
            price_label = QLabel(f"PKR {item['price']}", self.grid_content)
            price_label.setStyleSheet("color: #FFFFFF; font-size: 12px;")
            subcat_label = QLabel(f"{item['subcat']}", self.grid_content)
            subcat_label.setStyleSheet("color: #FFFFFF; font-size: 12px;")
            stock_label=QLabel(f"In Stock: {item['stock']}", self.grid_content)
            stock_label.setStyleSheet("color: #FFFFFF; font-size: 12px;")

            # Edit button
            edit_button = QPushButton("Edit", self.grid_content)
            if self.db_manager.is_enable(item['id'])==1:
                edit_button.setStyleSheet("background-color: #9C2EF0; color: #FFFFFF; font-size: 12px; font-family: Arial;")
            else: 
                edit_button.setStyleSheet("background-color: #808080; color: #D3D3D3; font-size: 12px; font-family: Arial;")

            edit_button.clicked.connect(lambda _, i=item: self.show_edit_dialog(i))

            # Arrange item details and button in the grid
            self.grid_layout.addWidget(id_label, row, 0, alignment=QtCore.Qt.AlignmentFlag.AlignTop)
            self.grid_layout.addWidget(name_label, row, 1, alignment=QtCore.Qt.AlignmentFlag.AlignTop)
            self.grid_layout.addWidget(price_label, row, 2, alignment=QtCore.Qt.AlignmentFlag.AlignTop)
            self.grid_layout.addWidget(subcat_label, row, 3, alignment=QtCore.Qt.AlignmentFlag.AlignTop)
            self.grid_layout.addWidget(stock_label, row, 4, alignment=QtCore.Qt.AlignmentFlag.AlignTop)
            self.grid_layout.addWidget(edit_button, row, 5, alignment=QtCore.Qt.AlignmentFlag.AlignTop)
            self.grid_layout.setRowStretch(row,1)

    def update_item_grid(self):
        """Filter the item list based on the search bar input and refresh the grid."""
        search_text = self.searchBar.text().strip().lower()
        if search_text == "":
            self.filtered_items = self.items[:]
        else:
            self.filtered_items = [
                items for items in self.items
                if search_text in items["name"].lower() or search_text in str(items["id"]) 
            ]
        self.populate_item_grid()

    def update_stock(self,item):
        amount, ok = QInputDialog.getDouble(self, "Stock Update", f"Enter new stock for {item['name']}:",
                                            0, -10000, 10000, 2)
        if ok:
            self.db_manager.vendor_change_stock(self.vendor_id,item['id'],amount)
            self.populate_item_grid()
            message_text = f"Stock of {item['name']} is now {amount}."
            QMessageBox.information(self, "Success", message_text)

    def show_edit_dialog(self, item):
        """Provide options to edit item name, delete item, or update price."""
        options = ["Edit Item Name", "Update Price", "Edit Subcategory","Update Stock","Enable/Disable"]
        action, ok = QInputDialog.getItem(self, "Edit Options", f"Choose an action for {item['name']}:", options, 0, False)

        if ok and action:
            if action == "Edit Item Name":
                self.edit_item_name(item)
            elif action == "Update Price":
                self.update_price(item)
            elif action == "Edit Subcategory":
                self.update_subcategory(item)
            elif action == "Update Stock":
                self.update_stock(item)
            elif action == "Enable/Disable":
                self.enable_disable(item)

    def edit_item_name(self, item):
        """Edit item name."""
        new_name, ok = QInputDialog.getText(self, "Edit Name", "Enter new name:", text=item["name"])
        
        if new_name and ok:
            self.db_manager.vendor_change_name(self.vendor_id,item['id'],new_name)
            self.populate_item_grid()
            QMessageBox.information(self, "Success", f"Item {new_name} info updated successfully.")

    def update_price(self, item):
        """Prompt for new price."""
        amount, ok = QInputDialog.getDouble(self, "price Update", f"Enter new price for {item['name']}:",
                                            0, -10000, 10000, 2)
        if ok:
            self.db_manager.vendor_change_price(self.vendor_id,item['id'],amount)
            self.populate_item_grid()
            message_text = f"Price of {item['name']} is now PKR {amount}."
            QMessageBox.information(self, "Success", message_text)

    def update_subcategory(self,item):
        """Provide options to edit item name, delete item, or update price."""
        subcategories = self.db_manager.find_subcategories() 
        options = [row[0] for row in subcategories]  
        action, ok = QInputDialog.getItem(self, "Subcategory Options", f"Choose a subcategory for {item['name']}:", options, 0, False)
        sub_id=self.db_manager.find_subcategory_id(action)
        sub_id_value=sub_id[0][0]
        if ok and action:
            self.db_manager.update_subcategory_id(sub_id_value,self.vendor_id,item['id'])
            self.populate_item_grid()
            message_text = f"Subcategory of {item['name']} is now {action}."
            QMessageBox.information(self, "Success", message_text)

    def enable_disable(self,item):
        enabled=self.db_manager.is_enable(item['id'])
        if enabled==1:
            self.db_manager.vendor_disable_item(item['id'])
            message_text = f"{item['name']} has been discontinued."
            QMessageBox.information(self, "Success", message_text)
        else:
            self.db_manager.vendor_enable_item(item['id'])
            message_text = f"Sale of {item['name']} has been resumed."
            QMessageBox.information(self, "Success", message_text)
        self.populate_item_grid()
        
    def open_add_item_window(self):
        """Prompt for new item details and add the item."""
        name, ok1 = QInputDialog.getText(self, "New Item", "Enter new item name:")
        amount, ok2 = QInputDialog.getDouble(self, "New Item", "Enter new item's price:",
                                            0, -10000, 10000, 2)
        stock, ok3 = QInputDialog.getText(self, "New Item", "Enter new item stock:")
        subcategories = self.db_manager.find_subcategories() 
        options = [row[0] for row in subcategories]  
        subcat, ok4 = QInputDialog.getItem(self, "Subcategory Options", f"Choose a subcategory for:", options, 0, False)
        sub_id=self.db_manager.find_subcategory_id(subcat)
        sub_id_value=sub_id[0][0]
        if ok1 and name and amount and ok2 and stock and ok3 and subcat and ok4:
            self.db_manager.vendor_add_item(self.vendor_id,name,amount,sub_id_value,stock)
            self.filtered_items = self.items[:]
            self.populate_item_grid()
            QMessageBox.information(self, "Success", f"New item {name} added successfully.")

    def return_to_main(self):
        from screens.vendor_screens.vendor_home import VendorHome
        self.main_menu = VendorHome(self.vendor_id, self.vendorname)
        self.main_menu.show()
        self.close()

    def logout(self):
        from screens.login import LoginScreen
        self.login_screen = LoginScreen()
        self.login_screen.show()
        self.close()

    def fetch_menu_items(self):
        menu_items=self.db_manager.vendor_view_items(self.vendor_id)
        return [{'id':item[0], 'name':item[1],'price':item[2],'subcat':item[3],'stock':item[4],'is_sold':item[5]} for item in menu_items]

def main():
    app = QtWidgets.QApplication(sys.argv)
    window = UpdateMenu(101, "John Doe")
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
