from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                               QTabWidget, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox)
from database.db_manager import db_manager
from ui.dialogs.sale_dialog import SaleDialog
from ui.dialogs.buyback_dialog import BuybackDialog
from utils.helpers import format_rupiah

class TransactionView(QWidget):
    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        self.main_window = main_window
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        self.tabs = QTabWidget()

        self.tab_penjualan = QWidget()
        self.setup_penjualan_tab()

        self.tab_buyback = QWidget()
        self.setup_buyback_tab()

        self.tabs.addTab(self.tab_penjualan, "Penjualan")
        self.tabs.addTab(self.tab_buyback, "Buyback")

        layout.addWidget(self.tabs)

    def setup_penjualan_tab(self):
        layout = QVBoxLayout(self.tab_penjualan)

        btn = QPushButton("Catat Transaksi Penjualan")
        btn.clicked.connect(self.new_sale)
        layout.addWidget(btn)

        self.table_penjualan = QTableWidget()
        self.table_penjualan.setColumnCount(7)
        self.table_penjualan.setHorizontalHeaderLabels(["ID", "Tanggal", "Kasir", "Item", "Jumlah", "Total Harga", "Catatan"])
        self.table_penjualan.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table_penjualan.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout.addWidget(self.table_penjualan)

    def setup_buyback_tab(self):
        layout = QVBoxLayout(self.tab_buyback)

        btn = QPushButton("Catat Transaksi Buyback")
        btn.clicked.connect(self.new_buyback)
        layout.addWidget(btn)

        self.table_buyback = QTableWidget()
        self.table_buyback.setColumnCount(6)
        self.table_buyback.setHorizontalHeaderLabels(["ID", "Tanggal", "Kasir", "Jumlah", "Total Harga", "Catatan"])
        self.table_buyback.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table_buyback.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout.addWidget(self.table_buyback)

    def load_data(self):

        sales = db_manager.get_transactions(tipe='penjualan')
        self.table_penjualan.setRowCount(0)
        for row_idx, sale in enumerate(sales):
            self.table_penjualan.insertRow(row_idx)
            self.table_penjualan.setItem(row_idx, 0, QTableWidgetItem(str(sale['id'])))
            self.table_penjualan.setItem(row_idx, 1, QTableWidgetItem(sale['tanggal']))
            self.table_penjualan.setItem(row_idx, 2, QTableWidgetItem(sale['username']))
            self.table_penjualan.setItem(row_idx, 3, QTableWidgetItem(sale['nama_item'] or 'N/A'))
            self.table_penjualan.setItem(row_idx, 4, QTableWidgetItem(str(sale['jumlah'])))
            self.table_penjualan.setItem(row_idx, 5, QTableWidgetItem(format_rupiah(sale['total_harga'])))
            self.table_penjualan.setItem(row_idx, 6, QTableWidgetItem(sale['catatan']))

        buybacks = db_manager.get_transactions(tipe='buyback')
        self.table_buyback.setRowCount(0)
        for row_idx, bb in enumerate(buybacks):
            self.table_buyback.insertRow(row_idx)
            self.table_buyback.setItem(row_idx, 0, QTableWidgetItem(str(bb['id'])))
            self.table_buyback.setItem(row_idx, 1, QTableWidgetItem(bb['tanggal']))
            self.table_buyback.setItem(row_idx, 2, QTableWidgetItem(bb['username']))
            self.table_buyback.setItem(row_idx, 3, QTableWidgetItem(str(bb['jumlah'])))
            self.table_buyback.setItem(row_idx, 4, QTableWidgetItem(format_rupiah(bb['total_harga'])))
            self.table_buyback.setItem(row_idx, 5, QTableWidgetItem(bb['catatan']))

    def new_sale(self):
        dialog = SaleDialog(self, gold_price=self.main_window.get_gold_price())
        if dialog.exec():
            data = dialog.get_data()
            try:
                db_manager.record_sale(self.main_window.current_user['id'], data['item_id'],
                                       data['jumlah'], data['total_harga'], data['catatan'])
                QMessageBox.information(self, "Sukses", "Transaksi Penjualan berhasil dicatat!")
                self.load_data()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Gagal mencatat transaksi: {str(e)}")

    def new_buyback(self):
        dialog = BuybackDialog(self, gold_price=self.main_window.get_gold_price())
        if dialog.exec():
            data = dialog.get_data()
            try:
                db_manager.record_buyback(self.main_window.current_user['id'],
                                          data['total_harga'], data['catatan'])
                QMessageBox.information(self, "Sukses", "Transaksi Buyback berhasil dicatat!")
                self.load_data()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Gagal mencatat transaksi: {str(e)}")
