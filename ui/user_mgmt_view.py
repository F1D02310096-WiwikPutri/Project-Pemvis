from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                               QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox)
from database.db_manager import db_manager
from ui.dialogs.user_dialog import UserDialog

class UserMgmtView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        btn_layout = QHBoxLayout()
        self.add_btn = QPushButton("Tambah Akun")
        self.add_btn.clicked.connect(self.add_user)

        self.edit_btn = QPushButton("Edit Akun")
        self.edit_btn.clicked.connect(self.edit_user)

        self.toggle_btn = QPushButton("Aktif/Nonaktifkan Akun")
        self.toggle_btn.clicked.connect(self.toggle_user)

        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.edit_btn)
        btn_layout.addWidget(self.toggle_btn)
        layout.addLayout(btn_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "Username", "Role", "Status"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout.addWidget(self.table)

    def load_data(self):
        users = db_manager.get_all_users()
        self.table.setRowCount(0)
        for row_idx, user in enumerate(users):
            self.table.insertRow(row_idx)
            self.table.setItem(row_idx, 0, QTableWidgetItem(str(user['id'])))
            self.table.setItem(row_idx, 1, QTableWidgetItem(user['username']))
            self.table.setItem(row_idx, 2, QTableWidgetItem(user['role']))
            status = "Aktif" if user['is_active'] else "Nonaktif"
            self.table.setItem(row_idx, 3, QTableWidgetItem(status))

    def add_user(self):
        dialog = UserDialog(self)
        if dialog.exec():
            data = dialog.get_data()
            if db_manager.add_user(data['username'], data['password'], data['role']):
                QMessageBox.information(self, "Sukses", "Akun berhasil ditambahkan!")
                self.load_data()
            else:
                QMessageBox.warning(self, "Error", "Gagal! Username mungkin sudah digunakan.")

    def edit_user(self):
        selected = self.table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, "Warning", "Pilih akun yang akan diedit!")
            return

        user_id = int(self.table.item(selected, 0).text())
        username = self.table.item(selected, 1).text()

        if username == 'admin' and self.table.item(selected, 2).text() == 'admin':

            pass

        user_data = db_manager.get_user_by_username(username)
        dialog = UserDialog(self, user_data=user_data)
        if dialog.exec():
            data = dialog.get_data()
            is_active = user_data['is_active']
            if db_manager.update_user(user_id, data['username'], data['password'], data['role'], is_active):
                QMessageBox.information(self, "Sukses", "Akun berhasil diupdate!")
                self.load_data()
            else:
                QMessageBox.warning(self, "Error", "Gagal mengupdate akun.")

    def toggle_user(self):
        selected = self.table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, "Warning", "Pilih akun yang akan dinonaktifkan/diaktifkan!")
            return

        user_id = int(self.table.item(selected, 0).text())
        username = self.table.item(selected, 1).text()

        if username == 'admin':
            QMessageBox.warning(self, "Error", "Akun admin utama tidak boleh dinonaktifkan!")
            return

        user_data = db_manager.get_user_by_username(username)
        new_status = 0 if user_data['is_active'] else 1

        if db_manager.update_user(user_id, username, None, user_data['role'], new_status):
            status_text = "diaktifkan" if new_status else "dinonaktifkan"
            QMessageBox.information(self, "Sukses", f"Akun {username} berhasil {status_text}!")
            self.load_data()
