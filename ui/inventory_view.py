from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                               QLineEdit, QComboBox, QPushButton,
                               QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox)
from database.db_manager import db_manager
from ui.dialogs.item_dialog import ItemDialog
from utils.helpers import format_rupiah

class InventoryView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        toolbar = QHBoxLayout()

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Cari nama item atau SKU...")
        self.search_input.textChanged.connect(self.filter_data)

        self.jenis_combo = QComboBox()
        self.jenis_combo.addItems(["Semua", "Cincin", "Gelang", "Kalung", "Anting", "Liontin"])
        self.jenis_combo.currentTextChanged.connect(self.filter_data)

        toolbar.addWidget(self.search_input)
        toolbar.addWidget(self.jenis_combo)
        layout.addLayout(toolbar)

        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels(["ID", "Kode SKU", "Nama Item", "Jenis", "Karat", "Berat (g)", "Stok", "Harga Beli Ref"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout.addWidget(self.table)

        btn_layout = QHBoxLayout()
        self.add_btn = QPushButton("Tambah Item")
        self.add_btn.clicked.connect(self.add_item)

        self.edit_btn = QPushButton("Edit Item")
        self.edit_btn.clicked.connect(self.edit_item)

        self.delete_btn = QPushButton("Hapus Item")
        self.delete_btn.clicked.connect(self.delete_item)

        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.edit_btn)
        btn_layout.addWidget(self.delete_btn)
        layout.addLayout(btn_layout)

    def load_data(self):
        self.all_items = db_manager.get_all_inventory()
        self.filter_data()

    def filter_data(self):
        keyword = self.search_input.text().lower()
        jenis = self.jenis_combo.currentText()

        filtered = []
        for item in self.all_items:
            match_keyword = keyword in item['nama_item'].lower() or keyword in item['kode_sku'].lower()
            match_jenis = (jenis == "Semua") or (jenis == item['jenis'])

            if match_keyword and match_jenis:
                filtered.append(item)

        self.table.setRowCount(0)
        for row_idx, item in enumerate(filtered):
            self.table.insertRow(row_idx)
            self.table.setItem(row_idx, 0, QTableWidgetItem(str(item['id'])))
            self.table.setItem(row_idx, 1, QTableWidgetItem(item['kode_sku']))
            self.table.setItem(row_idx, 2, QTableWidgetItem(item['nama_item']))
            self.table.setItem(row_idx, 3, QTableWidgetItem(item['jenis']))
            self.table.setItem(row_idx, 4, QTableWidgetItem(str(item['kadar_karat'])))
            self.table.setItem(row_idx, 5, QTableWidgetItem(str(item['berat_gram'])))
            self.table.setItem(row_idx, 6, QTableWidgetItem(str(item['stok'])))
            self.table.setItem(row_idx, 7, QTableWidgetItem(format_rupiah(item['harga_beli_ref'])))

    def add_item(self):
        dialog = ItemDialog(self)
        if dialog.exec():
            data = dialog.get_data()
            if db_manager.add_inventory(data['kode_sku'], data['nama_item'], data['jenis'],
                                        data['kadar_karat'], data['berat_gram'], data['stok'], data['harga_beli_ref']):
                QMessageBox.information(self, "Sukses", "Item berhasil ditambahkan!")
                self.load_data()
            else:
                QMessageBox.warning(self, "Error", "Gagal menambahkan item. SKU mungkin sudah ada.")

    def edit_item(self):
        selected = self.table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, "Warning", "Pilih item yang akan diedit!")
            return

        item_id = int(self.table.item(selected, 0).text())
        item_data = db_manager.get_inventory_by_id(item_id)

        if item_data:
            dialog = ItemDialog(self, item_data=item_data)
            if dialog.exec():
                data = dialog.get_data()
                if db_manager.update_inventory(item_id, data['kode_sku'], data['nama_item'], data['jenis'],
                                            data['kadar_karat'], data['berat_gram'], data['stok'], data['harga_beli_ref']):
                    QMessageBox.information(self, "Sukses", "Item berhasil diupdate!")
                    self.load_data()
                else:
                    QMessageBox.warning(self, "Error", "Gagal mengupdate item.")

    def delete_item(self):
        selected = self.table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, "Warning", "Pilih item yang akan dihapus!")
            return

        item_id = int(self.table.item(selected, 0).text())
        nama = self.table.item(selected, 2).text()

        reply = QMessageBox.question(self, "Konfirmasi", f"Yakin ingin menghapus {nama}?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            db_manager.delete_inventory(item_id)
            QMessageBox.information(self, "Sukses", "Item berhasil dihapus!")
            self.load_data()
