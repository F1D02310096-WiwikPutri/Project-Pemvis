import sys
import os
from PySide6.QtWidgets import QApplication, QMessageBox
from ui.login_dialog import LoginDialog
from ui.main_window import MainWindow

class AppController:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.main_window = None
        self.login_dialog = None
        self.load_theme("style_light.qss")

    def load_theme(self, filename):
        path = os.path.join(os.path.dirname(__file__), "assets", filename)
        if os.path.exists(path):
            with open(path, "r") as f:
                self.app.setStyleSheet(f.read())

    def start(self):
        self.show_login()
        sys.exit(self.app.exec())

    def show_login(self):
        if self.main_window:
            self.main_window.close()
            self.main_window = None

        self.login_dialog = LoginDialog()
        if self.login_dialog.exec():

            user = self.login_dialog.current_user
            self.show_main_window(user)
        else:

            self.app.quit()

    def show_main_window(self, user):
        self.main_window = MainWindow(user)

        self.main_window.app_controller = self

        def toggle_theme_override():
            if not self.main_window.is_dark:
                self.load_theme("style_dark.qss")
            else:
                self.load_theme("style_light.qss")
            self.main_window.is_dark = not self.main_window.is_dark

        self.main_window.toggle_theme = toggle_theme_override

        def logout_override():
            reply = QMessageBox.question(self.main_window, 'Konfirmasi Logout', 'Apakah Anda yakin ingin logout?',
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                self.show_login()

        self.main_window.logout = logout_override

        self.main_window.showMaximized()

if __name__ == "__main__":
    controller = AppController()
    controller.start()
