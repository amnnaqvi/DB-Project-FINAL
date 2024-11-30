    def rate_order(self, order_id):
        dialog = QDialog(self)
        dialog.setWindowTitle("Rate Order")
        dialog.setFixedSize(300, 200)
        layout = QVBoxLayout()

        # Rating selection
        label = QLabel("Rate this order (1 to 5):", dialog)
        label.setFont(QFont("Arial", 12))
        combo = QComboBox(dialog)
        combo.addItems([str(i) for i in range(1, 6)])

        # Submit button
        submit_button = QPushButton("Submit", dialog)
        submit_button.clicked.connect(lambda: self.submit_rating(dialog, order_id, int(combo.currentText())))

        layout.addWidget(label)
        layout.addWidget(combo)
        layout.addWidget(submit_button)
        dialog.setLayout(layout)
        dialog.exec()

    def submit_rating(self, dialog, order_id, rating):
        try:
            self.db_manager.add_rating(self.user_id, order_id, rating)
            QMessageBox.information(self, "Success", "Thank you for rating the order!")
            dialog.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not submit rating: {e}")
            dialog.reject()
