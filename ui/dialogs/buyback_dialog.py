from PySide6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout,
                               QComboBox, QSpinBox, QDoubleSpinBox,
                               QLabel, QPushButton, QHBoxLayout, QMessageBox, QSlider)
from PySide6.QtCore import Qt
from logic.calculator import Calculator
from utils.helpers import format_rupiah

class BuybackDialog(QDialog):
    def __init__(self, parent=None, gold_price=0):
        super().__init__(parent)
        self.setWindowTitle("Transaksi Buyback")
        self.gold_price = gold_price
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.karat_combo = QComboBox()
        self.karat_combo.addItems(["24", "22", "18", "14"])

        self.berat_input = QDoubleSpinBox()
        self.berat_input.setMaximum(1000)
        self.berat_input.setDecimals(2)

        self.potongan_slider = QSlider(Qt.Orientation.Horizontal)
        self.potongan_slider.setRange(0, 50)
        self.potongan_label = QLabel("0%")

        slider_layout = QHBoxLayout()
        slider_layout.addWidget(self.potongan_slider)
        slider_layout.addWidget(self.potongan_label)

        self.preview_label = QLabel(format_rupiah(0))
        self.preview_label.setStyleSheet("font-size: 16px; font-weight: bold; color: green;")

        form.addRow("Kadar Karat:", self.karat_combo)
        form.addRow("Berat (gram):", self.berat_input)
        form.addRow("Potongan Harga (%):", slider_layout)
        form.addRow("Harga Beli (Total):", self.preview_label)

        layout.addLayout(form)

        btn_layout = QHBoxLayout()
        self.save_btn = QPushButton("Konfirmasi Transaksi")
        self.save_btn.clicked.connect(self.validate_and_accept)
        self.cancel_btn = QPushButton("Batal")
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)

        self.karat_combo.currentIndexChanged.connect(self.calculate_total)
        self.berat_input.valueChanged.connect(self.calculate_total)
        self.potongan_slider.valueChanged.connect(self.on_slider_changed)

    def on_slider_changed(self, value):
        self.potongan_label.setText(f"{value}%")
        self.calculate_total()

    def calculate_total(self):
        berat = self.berat_input.value()
        karat = int(self.karat_combo.currentText())
        potongan = self.potongan_slider.value()

        harga = Calculator.calculate_buyback_price(berat, self.gold_price, karat, potongan)
        self.preview_label.setText(format_rupiah(harga))

    def validate_and_accept(self):
        if self.berat_input.value() <= 0:
            QMessageBox.warning(self, "Error", "Berat emas harus lebih dari 0!")
            return
        self.accept()

    def get_data(self):
        berat = self.berat_input.value()
        karat = int(self.karat_combo.currentText())
        potongan = self.potongan_slider.value()
        total_harga = Calculator.calculate_buyback_price(berat, self.gold_price, karat, potongan)

        return {
            'total_harga': total_harga,
            'catatan': f"Karat: {karat}, Berat: {berat}g, Potongan: {potongan}%"
        }
