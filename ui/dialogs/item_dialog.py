from PySide6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout,
                               QLineEdit, QPushButton, QHBoxLayout,
                               QComboBox, QSpinBox, QDoubleSpinBox, QMessageBox)
from logic.validator import Validator

class ItemDialog(QDialog):
    def __init__(self, parent=None, item_data=None):
        super().__init__(parent)
        self.item_data = item_data
        self.setWindowTitle("Tambah Item" if not item_data else "Edit Item")
        self.setup_ui()
        if self.item_data:
            self.populate_data()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        self.sku_input = QLineEdit()
        self.nama_input = QLineEdit()

        self.jenis_combo = QComboBox()
        self.jenis_combo.addItems(["Cincin", "Gelang", "Kalung", "Anting", "Liontin"])

        self.karat_combo = QComboBox()
        self.karat_combo.addItems(["24", "22", "18", "14"])

        self.berat_input = QDoubleSpinBox()
        self.berat_input.setMaximum(1000)
        self.berat_input.setDecimals(2)

        self.stok_input = QSpinBox()
        self.stok_input.setMaximum(10000)

        self.harga_ref_input = QDoubleSpinBox()
        self.harga_ref_input.setMaximum(1e9)
        self.harga_ref_input.setDecimals(0)

        form_layout.addRow("Kode SKU:", self.sku_input)
        form_layout.addRow("Nama Item:", self.nama_input)
        form_layout.addRow("Jenis:", self.jenis_combo)
        form_layout.addRow("Kadar Karat:", self.karat_combo)
        form_layout.addRow("Berat (gram):", self.berat_input)
        form_layout.addRow("Stok:", self.stok_input)
        form_layout.addRow("Harga Beli Ref (Rp):", self.harga_ref_input)

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
        self.sku_input.setText(self.item_data['kode_sku'])
        self.sku_input.setEnabled(False)
        self.nama_input.setText(self.item_data['nama_item'])
        self.jenis_combo.setCurrentText(self.item_data['jenis'])
        self.karat_combo.setCurrentText(str(self.item_data['kadar_karat']))
        self.berat_input.setValue(self.item_data['berat_gram'])
        self.stok_input.setValue(self.item_data['stok'])
        self.harga_ref_input.setValue(self.item_data['harga_beli_ref'])

    def validate_and_accept(self):
        v1, m1 = Validator.is_not_empty(self.sku_input.text(), "Kode SKU")
        v2, m2 = Validator.is_not_empty(self.nama_input.text(), "Nama Item")
        v3, m3 = Validator.is_positive_number(self.berat_input.value(), "Berat")

        if not (v1 and v2 and v3):
            QMessageBox.warning(self, "Validasi Gagal", m1 or m2 or m3)
            return

        self.accept()

    def get_data(self):
        return {
            'kode_sku': self.sku_input.text().strip(),
            'nama_item': self.nama_input.text().strip(),
            'jenis': self.jenis_combo.currentText(),
            'kadar_karat': int(self.karat_combo.currentText()),
            'berat_gram': self.berat_input.value(),
            'stok': self.stok_input.value(),
            'harga_beli_ref': self.harga_ref_input.value()
        }
