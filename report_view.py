from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
                               QComboBox, QDateEdit, QFileDialog)
from PySide6.QtCore import QDate
from database.db_manager import db_manager
from utils.helpers import format_rupiah
from utils.exporter import Exporter

class ReportView(QWidget):
    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        self.main_window = main_window
        self.setup_ui()
        self.load_users_to_combo()
        self.load_data()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        filter_layout = QHBoxLayout()

        self.start_date = QDateEdit(QDate.currentDate().addDays(-30))
        self.start_date.setCalendarPopup(True)
        self.end_date = QDateEdit(QDate.currentDate())
        self.end_date.setCalendarPopup(True)

        self.jenis_combo = QComboBox()
        self.jenis_combo.addItems(["Semua", "Penjualan", "Buyback"])

        self.kasir_combo = QComboBox()
        self.kasir_combo.addItem("Semua Kasir", None)

        filter_btn = QPushButton("Filter Data")
        filter_btn.clicked.connect(self.load_data)

        filter_layout.addWidget(QLabel("Dari:"))
        filter_layout.addWidget(self.start_date)
        filter_layout.addWidget(QLabel("Sampai:"))
        filter_layout.addWidget(self.end_date)
        filter_layout.addWidget(QLabel("Jenis:"))
        filter_layout.addWidget(self.jenis_combo)
        filter_layout.addWidget(QLabel("Kasir:"))
        filter_layout.addWidget(self.kasir_combo)
        filter_layout.addWidget(filter_btn)

        layout.addLayout(filter_layout)

        export_layout = QHBoxLayout()
        self.export_csv_btn = QPushButton("Export ke CSV")
        self.export_csv_btn.clicked.connect(self.export_csv)
        self.export_pdf_btn = QPushButton("Export ke PDF")
        self.export_pdf_btn.clicked.connect(self.export_pdf)

        export_layout.addStretch()
        export_layout.addWidget(self.export_csv_btn)
        export_layout.addWidget(self.export_pdf_btn)
        layout.addLayout(export_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels(["No", "Tanggal", "Kasir", "Jenis", "Item", "Jumlah", "Total (Rp)", "Catatan"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout.addWidget(self.table)

        self.total_label = QLabel("Total: Rp 0,00")
        self.total_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(self.total_label)

    def load_users_to_combo(self):
        users = db_manager.get_all_users()
        for user in users:
            self.kasir_combo.addItem(user['username'], user['id'])

    def load_data(self):
        start = self.start_date.date().toString("yyyy-MM-dd")
        end = self.end_date.date().toString("yyyy-MM-dd")
        tipe = self.jenis_combo.currentText()
        user_id = self.kasir_combo.currentData()

        transactions = db_manager.get_transactions(tipe=tipe, start_date=start, end_date=end, user_id=user_id)

        self.table.setRowCount(0)
        total_omzet = 0

        for row_idx, trans in enumerate(transactions):
            self.table.insertRow(row_idx)
            self.table.setItem(row_idx, 0, QTableWidgetItem(str(trans['id'])))
            self.table.setItem(row_idx, 1, QTableWidgetItem(trans['tanggal']))
            self.table.setItem(row_idx, 2, QTableWidgetItem(trans['username']))
            self.table.setItem(row_idx, 3, QTableWidgetItem(trans['tipe_transaksi'].title()))
            self.table.setItem(row_idx, 4, QTableWidgetItem(trans['nama_item'] or '-'))
            self.table.setItem(row_idx, 5, QTableWidgetItem(str(trans['jumlah'])))
            self.table.setItem(row_idx, 6, QTableWidgetItem(format_rupiah(trans['total_harga'])))
            self.table.setItem(row_idx, 7, QTableWidgetItem(trans['catatan']))

            if trans['tipe_transaksi'] == 'penjualan':
                total_omzet += trans['total_harga']
            elif trans['tipe_transaksi'] == 'buyback':
                total_omzet -= trans['total_harga']

        self.total_label.setText(f"Total Bersih (Penjualan - Buyback): {format_rupiah(total_omzet)}")

    def export_csv(self):
        path, _ = QFileDialog.getSaveFileName(self, "Simpan CSV", "", "CSV Files (*.csv)")
        if path:
            success, msg = Exporter.export_csv(path, self.table)
            if success:
                QMessageBox.information(self, "Sukses", msg)
            else:
                QMessageBox.critical(self, "Error", msg)

    def export_pdf(self):
        path, _ = QFileDialog.getSaveFileName(self, "Simpan PDF", "", "PDF Files (*.pdf)")
        if path:
            success, msg = Exporter.export_pdf(path, self.table, title="Laporan Transaksi Goldata")
            if success:
                QMessageBox.information(self, "Sukses", msg)
            else:
                QMessageBox.critical(self, "Error", msg)
