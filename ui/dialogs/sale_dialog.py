from PySide6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout,
                               QComboBox, QSpinBox, QDoubleSpinBox,
                               QLabel, QPushButton, QHBoxLayout, QMessageBox)
from database.db_manager import db_manager
from logic.calculator import Calculator
from utils.helpers import format_rupiah

class SaleDialog(QDialog):
    def __init__(self, parent=None, gold_price=0):
        super().__init__(parent)
        self.setWindowTitle("Transaksi Penjualan")
        self.gold_price = gold_price
        self.items = db_manager.get_all_inventory()
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.item_combo = QComboBox()
        for item in self.items:

            if item['stok'] > 0:
                self.item_combo.addItem(f"{item['kode_sku']} - {item['nama_item']}", item)

        self.jumlah_input = QSpinBox()
        self.jumlah_input.setMinimum(1)

        self.ongkos_input = QDoubleSpinBox()
        self.ongkos_input.setMaximum(1e9)
        self.ongkos_input.setDecimals(0)

        self.preview_label = QLabel(format_rupiah(0))
        self.preview_label.setStyleSheet("font-size: 16px; font-weight: bold; color: blue;")

        form.addRow("Pilih Item:", self.item_combo)
        form.addRow("Jumlah:", self.jumlah_input)
        form.addRow("Ongkos Bikin (Rp):", self.ongkos_input)
        form.addRow("Total Estimasi:", self.preview_label)

        layout.addLayout(form)

        btn_layout = QHBoxLayout()
        self.save_btn = QPushButton("Konfirmasi Transaksi")
        self.save_btn.clicked.connect(self.validate_and_accept)
        self.cancel_btn = QPushButton("Batal")
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)

        self.item_combo.currentIndexChanged.connect(self.calculate_total)
        self.jumlah_input.valueChanged.connect(self.calculate_total)
        self.ongkos_input.valueChanged.connect(self.calculate_total)

        self.calculate_total()

    def calculate_total(self):
        item_data = self.item_combo.currentData()
        if not item_data:
            self.preview_label.setText(format_rupiah(0))
            return

        jumlah = self.jumlah_input.value()
        ongkos = self.ongkos_input.value()

        total_berat = item_data['berat_gram'] * jumlah
        harga = Calculator.calculate_sale_price(total_berat, self.gold_price, item_data['kadar_karat'], ongkos)
        self.preview_label.setText(format_rupiah(harga))

    def validate_and_accept(self):
        item_data = self.item_combo.currentData()
        if not item_data:
            QMessageBox.warning(self, "Error", "Tidak ada item yang dipilih!")
            return

        if self.jumlah_input.value() > item_data['stok']:
            QMessageBox.warning(self, "Error", f"Stok tidak mencukupi! Sisa: {item_data['stok']}")
            return

        self.accept()

    def get_data(self):
        item_data = self.item_combo.currentData()
        jumlah = self.jumlah_input.value()
        ongkos = self.ongkos_input.value()
        total_berat = item_data['berat_gram'] * jumlah
        total_harga = Calculator.calculate_sale_price(total_berat, self.gold_price, item_data['kadar_karat'], ongkos)

        return {
            'item_id': item_data['id'],
            'jumlah': jumlah,
            'total_harga': total_harga,
            'catatan': f"Ongkos bikin: {ongkos}"
        }
