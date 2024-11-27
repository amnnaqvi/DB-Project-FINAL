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
