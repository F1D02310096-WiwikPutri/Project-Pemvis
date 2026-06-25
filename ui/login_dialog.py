from PySide6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout,
                               QLineEdit, QPushButton, QLabel, QHBoxLayout, QWidget)
from PySide6.QtCore import Qt
import hashlib
from database.db_manager import db_manager

class LoginDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Login Goldata")
        self.setMinimumSize(400, 300)
        self.current_user = None
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)

        container = QWidget()
        container.setMinimumWidth(300)
        layout = QVBoxLayout(container)

        title = QLabel("Goldata System")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 22px; font-weight: bold; margin-bottom: 20px;")
        layout.addWidget(title)

        form_layout = QFormLayout()

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Masukkan username...")
        self.username_input.setMinimumHeight(35)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Masukkan password...")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setMinimumHeight(35)

        form_layout.addRow("Username:", self.username_input)
        form_layout.addRow("Password:", self.password_input)

        layout.addLayout(form_layout)

        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: red;")
        self.error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.error_label)

        btn_layout = QHBoxLayout()
        self.login_btn = QPushButton("Login")
        self.login_btn.setMinimumHeight(35)
        self.login_btn.clicked.connect(self.validate_login)

        self.exit_btn = QPushButton("Keluar")
        self.exit_btn.setMinimumHeight(35)
        self.exit_btn.clicked.connect(self.reject)

        btn_layout.addWidget(self.login_btn)
        btn_layout.addWidget(self.exit_btn)

        layout.addLayout(btn_layout)

        main_layout.addWidget(container, 0, Qt.AlignmentFlag.AlignCenter)

    def validate_login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        if not username or not password:
            self.error_label.setText("Username dan Password harus diisi!")
            return

        user = db_manager.get_user_by_username(username)
        if user:

            if not user['is_active']:
                self.error_label.setText("Akun tidak aktif!")
                return

            pw_hash = hashlib.sha256(password.encode()).hexdigest()
            if user['password_hash'] == pw_hash:
                self.current_user = user
                self.accept()
            else:
                self.error_label.setText("Password salah!")
        else:
            self.error_label.setText("Username tidak ditemukan!")
