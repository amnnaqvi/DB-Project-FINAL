from PyQt6 import QtWidgets, QtCore
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QMainWindow, QLabel, QPushButton,QApplication
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))
from screens.database import DatabaseManager, get_db_connection

class VendorHome(QMainWindow):
    def __init__(self,vendor_id,vendor_name):
        super().__init__()
        self.vendor_id=vendor_id
        self.vendor_name=vendor_name
        self.db_manager = DatabaseManager(conn=get_db_connection())
        self.setupUi()


    def setupUi(self):
        self.setObjectName('MainWindow')
        self.setWindowTitle("Vendor Home")
        self.setFixedSize(600, 700)

        self.setStyleSheet("background-color: #1A1A3F;")

        self.centralwidget = QtWidgets.QWidget(self)
        self.setCentralWidget(self.centralwidget)

        self.rating = QLabel(self.centralwidget)
        self.rating.setObjectName('label')
        self.rating.setGeometry(QtCore.QRect(190, 90,250, 50))
        mean_rating=self.db_manager.fetch_vendor_rating(self.vendor_id)
        self.rating.setText(f'Your mean rating is {mean_rating}')
        self.rating.setStyleSheet("color: #F0F6FF; font-weight: bold; font-size: 20px; font-family: Arial;")

        # Label for Vendor title
        self.label = QLabel(self.centralwidget)
        self.label.setObjectName('label')
        self.label.setGeometry(QtCore.QRect(265, 150, 180, 50))
        self.label.setText('Vendor')
        self.label.setStyleSheet("color: #F0F6FF; font-weight: bold; font-size: 20px; font-family: Arial;")

        self.pushButton = QPushButton(self.centralwidget)
        self.pushButton.setObjectName('pushButton')
        self.pushButton.setGeometry(QtCore.QRect(200, 220, 200, 50))
        self.pushButton.setText('View Live Orders')
        self.pushButton.setStyleSheet("background-color: #9C2EF0; color: #F0F6FF; font-size: 14px; font-family: Arial;")
        self.pushButton.clicked.connect(self.live_order)

        self.pushButton_3 = QPushButton(self.centralwidget)
        self.pushButton_3.setObjectName('pushButton_3')
        self.pushButton_3.setGeometry(QtCore.QRect(200, 320, 200, 50))
        self.pushButton_3.setText('View Pickup Orders')
        self.pushButton_3.setStyleSheet("background-color: #9C2EF0; color: #F0F6FF; font-size: 14px; font-family: Arial;")
        self.pushButton_3.clicked.connect(self.view_pickup) 

        self.pushButton_3 = QPushButton(self.centralwidget)
        self.pushButton_3.setObjectName('pushButton_3')
        self.pushButton_3.setGeometry(QtCore.QRect(200, 420, 200, 50))
        self.pushButton_3.setText('View Order History')
        self.pushButton_3.setStyleSheet("background-color: #9C2EF0; color: #F0F6FF; font-size: 14px; font-family: Arial;")
        self.pushButton_3.clicked.connect(self.order_history) 

        self.pushButton_4 = QPushButton(self.centralwidget)
        self.pushButton_4.setObjectName('pushButton_4')
        self.pushButton_4.setGeometry(QtCore.QRect(200, 520, 200, 50))
        self.pushButton_4.setText('Update Menu')
        self.pushButton_4.setStyleSheet("background-color: #9C2EF0; color: #F0F6FF; font-size: 14px; font-family: Arial;")
        self.pushButton_4.clicked.connect(self.update_menu) 

        # Welcome label
        self.label_2 = QLabel(self.centralwidget)
        self.label_2.setObjectName('label_2')
        self.label_2.setGeometry(QtCore.QRect(175, 40, 270, 50))
        self.label_2.setText(f'Welcome {self.vendor_name}!')
        self.label_2.setStyleSheet("color: #F0F6FF; font-weight: bold; font-size: 20px; font-family: Arial;")
        self.label_2.setAlignment(Qt.AlignmentFlag.AlignCenter)



    def live_order(self):
        from vendor_live_order import View_Live_Orders
        self.hide()
        self.live_order_view = View_Live_Orders(self.vendor_id,self.vendor_name)
        self.live_order_view.show()
    def update_menu(self):
        from vendor_update_menu import UpdateMenu
        self.hide()
        self.vendor_menu_update = UpdateMenu(self.vendor_id,self.vendor_name)
        self.vendor_menu_update.show()
    def view_pickup(self):
        from vendor_view_pickup import View_Pickup_Orders
        self.hide()
        self.pickup_order_view = View_Pickup_Orders(self.vendor_id,self.vendor_name)
        self.pickup_order_view.show()
    def order_history(self):
        from vendor_order_history import View_Order_History
        self.hide
        self.vendor_order_history=View_Order_History(self.vendor_id,self.vendor_name)
        self.vendor_order_history.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    user_vendor_home = VendorHome(100,'Tapal')
    user_vendor_home.show()
    sys.exit(app.exec())