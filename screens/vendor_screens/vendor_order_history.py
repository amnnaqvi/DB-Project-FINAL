from PyQt6 import QtWidgets, QtCore
from PyQt6.QtWidgets import QMainWindow, QLabel, QInputDialog, QMessageBox, QPushButton, QScrollArea, QVBoxLayout, QHBoxLayout, QWidget, QFrame, QGridLayout
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))
from screens.database import DatabaseManager, get_db_connection

class View_Order_History(QMainWindow):
    def __init__(self, ID, name):
        super().__init__()
        self.setWindowTitle("Order History")
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
        layout.addLayout(top_bar_layout)

        # Title Label
        self.titleLabel = QLabel("Order History", self.centralwidget)
        self.titleLabel.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.titleLabel.setStyleSheet("color: #F0F6FF; font-weight: bold; font-size: 18px; font-family: Arial;")
        layout.addWidget(self.titleLabel)

        # Search Bar
        self.searchBar = QtWidgets.QLineEdit(self.centralwidget)
        self.searchBar.setPlaceholderText("Search by Name or ID")
        self.searchBar.setStyleSheet("font-size: 12px; color: #FFFFFF;")
        layout.addWidget(self.searchBar)

        # Scroll area for order grid
        scroll_area = QScrollArea(self.centralwidget)
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOn)

        # Widget to contain order grid
        self.grid_content = QWidget()
        self.grid_layout = QGridLayout(self.grid_content)
        self.grid_layout.setSpacing(10)
        scroll_area.setWidget(self.grid_content)
        layout.addWidget(scroll_area)

        # Sample Data for orders (for demonstration purposes)

        # Populate the order Grid
        self.populate_order_grid()

        # Connect search bar text change to update order grid
        self.searchBar.textChanged.connect(self.update_order_grid)

    def fetch_order_history(self):
        order_history=self.db_manager.fetch_vendor_order_history(self.vendor_id)
        return [{'id':order[0],'order':order[1],'user':order[2],'quantity':order[3],'price':order[4],'placed':order[5],'received':order[6],'pickup':order[7]} for order in order_history]

    

    def populate_order_grid(self):
        """Create a grid layout with order details and edit buttons, displaying only active orders."""
        # Clear existing widgets in the grid
        order_history_list= self.fetch_order_history()
        display_list=[]
        for order1 in order_history_list:
            order_dict={
                'order_id':order1['id'], 
                'user_id':order1['user'], 
                'orders_and_quantity':[[order1['order'],order1['quantity']]],
                'price':order1['price'],
                'placed':order1['placed'],
                'received':order1['received'],
                'pickup':order1['pickup']
                }
            
            for order2 in order_history_list:
                if order2==order1:
                    pass
                elif order1['id']==order2['id']:
                    order_dict['orders_and_quantity'].append([order2['order'],order2['quantity']])
                    order_dict['price']+=order2['price']
                    order_history_list.remove(order2)
            display_list.append(order_dict)
            order_history_list.remove(order1)
            order_dict={}
        

                    
                    
        self.orders = display_list
        self.filtered_orders = self.orders[:]
        for i in reversed(range(self.grid_layout.count())):
            widget = self.grid_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        # Filter for active orders and display up to 5 at a time
        for row, order in enumerate(self.filtered_orders[:6]):
            # order information display
            self.grid_layout.setRowMinimumHeight(row, 50)
            order_id_label = QLabel(f"Order ID: {order['order_id']}", self.grid_content)
            order_id_label.setStyleSheet("color: #FFFFFF; font-size: 12px;")
            user_id_label = QLabel(f"Cust ID: {order['user_id']}", self.grid_content)
            user_id_label.setStyleSheet("color: #FFFFFF; font-size: 12px;")
            items_str = '\n'.join([f"{item[1]} {item[0]}" for item in order['orders_and_quantity']])
            items_label = QLabel(items_str, self.grid_content)
            items_label.setStyleSheet("color: #FFFFFF; font-size: 12px;")
            price_label = QLabel(f"PKR {order['price']}", self.grid_content)
            price_label.setStyleSheet("color: #FFFFFF; font-size: 12px;")
            received_label = QLabel(f"{order['received']}", self.grid_content)
            received_label.setStyleSheet("color: #FFFFFF; font-size: 12px;")
            if order['pickup']==1:
                pickup_label=QLabel("Pickup Order", self.grid_content)
                pickup_label.setStyleSheet("color: #FFFFFF; font-size: 12px;")
            elif order['pickup']==0:
                pickup_label=QLabel("Live Order", self.grid_content)
                pickup_label.setStyleSheet("color: #FFFFFF; font-size: 12px;")
            # Arrange order details and button in the grid
            self.grid_layout.addWidget(order_id_label, row, 0, alignment=QtCore.Qt.AlignmentFlag.AlignTop)
            self.grid_layout.addWidget(user_id_label, row, 1, alignment=QtCore.Qt.AlignmentFlag.AlignTop)
            self.grid_layout.addWidget(items_label, row, 2, alignment=QtCore.Qt.AlignmentFlag.AlignTop)
            self.grid_layout.addWidget(price_label, row, 3, alignment=QtCore.Qt.AlignmentFlag.AlignTop)
            self.grid_layout.addWidget(received_label, row, 4, alignment=QtCore.Qt.AlignmentFlag.AlignTop)
            self.grid_layout.addWidget(pickup_label, row, 5, alignment=QtCore.Qt.AlignmentFlag.AlignTop)


    def update_order_grid(self):
        """Filter the order list based on the search bar input and refresh the grid."""
        search_text = self.searchBar.text().strip().lower()
        if search_text == "":
            self.filtered_orders = self.orders[:]
        else:
            self.filtered_orders = [
                orders for orders in self.orders
                if search_text in str(orders["order_id"]) or search_text in str(orders["user_id"]) 
            ]
        self.populate_order_grid()

    
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

def main():
    app = QtWidgets.QApplication(sys.argv)
    window = View_Order_History(101, "John Doe")
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
