from PySide6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout,
                               QLineEdit, QPushButton, QHBoxLayout,
                               QComboBox, QMessageBox)

class UserDialog(QDialog):
    def __init__(self, parent=None, user_data=None):
        super().__init__(parent)
        self.user_data = user_data
        self.setWindowTitle("Tambah Akun" if not user_data else "Edit Akun")
        self.setup_ui()
        if self.user_data:
            self.populate_data()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        self.username_input = QLineEdit()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText("Biarkan kosong jika tidak ingin ubah password" if self.user_data else "")

        self.role_combo = QComboBox()
        self.role_combo.addItems(["kasir", "admin"])

        form_layout.addRow("Username:", self.username_input)
        form_layout.addRow("Password:", self.password_input)
        form_layout.addRow("Role:", self.role_combo)

        layout.addLayout(form_layout)

        btn_layout = QHBoxLayout()
        self.save_btn = QPushButton("Simpan")
        self.save_btn.clicked.connect(self.validate_and_accept)
        self.cancel_btn = QPushButton("Batal")
        self.cancel_btn.clicked.connect(self.reject)

        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)

    def populate_data(self):
        self.username_input.setText(self.user_data['username'])
        self.role_combo.setCurrentText(self.user_data['role'])

    def validate_and_accept(self):
        if not self.username_input.text().strip():
            QMessageBox.warning(self, "Error", "Username tidak boleh kosong!")
            return

        if not self.user_data and not self.password_input.text().strip():
            QMessageBox.warning(self, "Error", "Password wajib diisi untuk akun baru!")
            return

        self.accept()

    def get_data(self):
        return {
            'username': self.username_input.text().strip(),
            'password': self.password_input.text().strip() if self.password_input.text().strip() else None,
            'role': self.role_combo.currentText()
        }
