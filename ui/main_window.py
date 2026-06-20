from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                               QPushButton, QStackedWidget, QLabel, QMenuBar, QMenu, QStatusBar, QMessageBox, QFrame)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import QFileDialog

from utils.importer import Importer
from ui.dialogs.help_dialog import HelpDialog
from ui.dashboard_view import DashboardView
from ui.inventory_view import InventoryView
from ui.transaction_view import TransactionView
from ui.expense_view import ExpenseView
from ui.report_view import ReportView
from ui.user_mgmt_view import UserMgmtView

class MainWindow(QMainWindow):
    def __init__(self, current_user):
        super().__init__()
        self.current_user = current_user
        self.setWindowTitle("Goldata - Sistem Manajemen Toko Emas")
        self.setMinimumSize(800, 600)
        self.setup_ui()

    def setup_ui(self):

        # Menu Bar
        menu_bar = self.menuBar()
        
        file_menu = menu_bar.addMenu("File")
        
        upload_action = QAction("Upload CSV (Inventaris)", self)
        upload_action.triggered.connect(self.upload_csv)
        file_menu.addAction(upload_action)
        
        file_menu.addSeparator()
        
        logout_action = QAction("Logout", self)
        logout_action.triggered.connect(self.logout)
        file_menu.addAction(logout_action)
        
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        help_menu = menu_bar.addMenu("Help")
        about_action = QAction("Tentang Aplikasi", self)
        about_action.triggered.connect(self.show_help)
        help_menu.addAction(about_action)

        status_bar = QStatusBar()
        self.setStatusBar(status_bar)
        status_bar.showMessage(f"Login sebagai: {self.current_user['username']} ({self.current_user['role'].upper()})")
        
        student_info = QLabel("Dikembangkan oleh: Pudael Zikri (F1D02310088), Wiwik Putri (F1D02310096), Rara Apriliana (F1D020086)")
        student_info.setStyleSheet("color: gray;")
        status_bar.addPermanentWidget(student_info)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        sidebar = QFrame()
        sidebar.setFixedWidth(220)
        sidebar.setStyleSheet("background-color: #2c3e50; color: white;")
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(10, 20, 10, 20)
        sidebar_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        app_title = QLabel("GOLDATA")
        app_title.setStyleSheet("font-size: 24px; font-weight: bold; color: #f1c40f; margin-bottom: 20px;")
        app_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sidebar_layout.addWidget(app_title)

        self.stacked_widget = QStackedWidget()

        self.dashboard_view = DashboardView()
        self.inventory_view = InventoryView()
        self.transaction_view = TransactionView(self)
        self.expense_view = ExpenseView(self)

        self.stacked_widget.addWidget(self.dashboard_view)
        self.stacked_widget.addWidget(self.inventory_view)
        self.stacked_widget.addWidget(self.transaction_view)
        self.stacked_widget.addWidget(self.expense_view)

        if self.current_user['role'] == 'admin':
            self.report_view = ReportView(self)
            self.user_mgmt_view = UserMgmtView()
            self.stacked_widget.addWidget(self.report_view)
            self.stacked_widget.addWidget(self.user_mgmt_view)

        self.add_nav_btn(sidebar_layout, "Dashboard", 0)
        self.add_nav_btn(sidebar_layout, "Inventaris", 1)
        self.add_nav_btn(sidebar_layout, "Transaksi", 2)
        self.add_nav_btn(sidebar_layout, "Pengeluaran", 3)

        if self.current_user['role'] == 'admin':
            self.add_nav_btn(sidebar_layout, "Laporan Global", 4)
            self.add_nav_btn(sidebar_layout, "Manajemen Akun", 5)

        sidebar_layout.addStretch()

        theme_btn = QPushButton("Toggle Dark/Light")
        theme_btn.setStyleSheet("""
            QPushButton {
                background-color: #34495e; color: white; padding: 10px; border: none; border-radius: 5px;
            }
            QPushButton:hover { background-color: #4cd137; }
        """)
        theme_btn.clicked.connect(self.toggle_theme)
        sidebar_layout.addWidget(theme_btn)

        main_layout.addWidget(sidebar)
        main_layout.addWidget(self.stacked_widget)

        self.stacked_widget.setCurrentIndex(0)

        self.is_dark = False

    def add_nav_btn(self, layout, text, index):
        btn = QPushButton(text)
        btn.setStyleSheet("""
            QPushButton {
                background-color: transparent; color: white; padding: 12px; font-size: 14px;
                text-align: left; border: none; border-radius: 5px; margin-bottom: 5px;
            }
            QPushButton:hover { background-color: #34495e; }
        """)
        btn.clicked.connect(lambda: self.switch_view(index))
        layout.addWidget(btn)

    def switch_view(self, index):
        self.stacked_widget.setCurrentIndex(index)

        current_widget = self.stacked_widget.currentWidget()
        if hasattr(current_widget, 'load_data'):
            current_widget.load_data()
        if hasattr(current_widget, 'update_dashboard'):
            current_widget.update_dashboard()

    def get_gold_price(self):
        return self.dashboard_view.gold_price

    def toggle_theme(self):

        app = self.window().parent()

        from PySide6.QtWidgets import QApplication
        q_app = QApplication.instance()

        if not self.is_dark:

            q_app.setStyleSheet("""
                QWidget { background-color: #1e1e1e; color: #ffffff; }
                QTableWidget { background-color: #2d2d2d; color: #ffffff; gridline-color: #555555; }
                QHeaderView::section { background-color: #333333; color: white; }
                QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox { background-color: #333333; color: white; border: 1px solid #555; }
                QPushButton { background-color: #0d6efd; color: white; border-radius: 4px; padding: 5px; }
                QPushButton:hover { background-color: #0b5ed7; }
            """)
        else:
            q_app.setStyleSheet("")

        self.is_dark = not self.is_dark

    def upload_csv(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Pilih File CSV", "", "CSV Files (*.csv)")
        if file_path:
            success, message = Importer.import_csv_inventory(file_path)
            if success:
                QMessageBox.information(self, "Sukses", message)
                # Refresh inventory view if it's currently loaded
                if hasattr(self.inventory_view, 'load_data'):
                    self.inventory_view.load_data()
            else:
                QMessageBox.warning(self, "Error", message)

    def show_help(self):
        dialog = HelpDialog(self)
        dialog.exec()

    def logout(self):
        reply = QMessageBox.question(self, 'Konfirmasi Logout', 'Apakah Anda yakin ingin logout?',
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            self.close()

            self.parent().show_login() if self.parent() else None

    def closeEvent(self, event):
        reply = QMessageBox.question(self, 'Keluar', 'Apakah Anda yakin ingin keluar dari aplikasi?',
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            event.accept()
        else:
            event.ignore()
