from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                               QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
                               QDialog, QFormLayout, QLineEdit, QDoubleSpinBox, QComboBox)
from database.db_manager import db_manager
from utils.helpers import format_rupiah

class ExpenseDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Catat Pengeluaran")
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.kategori_combo = QComboBox()
        self.kategori_combo.addItems(["Listrik/Air", "Gaji Karyawan", "Perawatan Toko", "Alat Tulis", "Lain-lain"])

        self.deskripsi_input = QLineEdit()

        self.jumlah_input = QDoubleSpinBox()
        self.jumlah_input.setMaximum(1e9)
        self.jumlah_input.setDecimals(0)

        form.addRow("Kategori:", self.kategori_combo)
        form.addRow("Deskripsi:", self.deskripsi_input)
        form.addRow("Jumlah (Rp):", self.jumlah_input)

        layout.addLayout(form)

        btn_layout = QHBoxLayout()
        self.save_btn = QPushButton("Simpan")
        self.save_btn.clicked.connect(self.validate_and_accept)
        self.cancel_btn = QPushButton("Batal")
        self.cancel_btn.clicked.connect(self.reject)

        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)

    def validate_and_accept(self):
        if not self.deskripsi_input.text().strip():
            QMessageBox.warning(self, "Error", "Deskripsi tidak boleh kosong!")
            return
        if self.jumlah_input.value() <= 0:
            QMessageBox.warning(self, "Error", "Jumlah pengeluaran harus lebih dari 0!")
            return
        self.accept()

    def get_data(self):
        return {
            'kategori': self.kategori_combo.currentText(),
            'deskripsi': self.deskripsi_input.text().strip(),
            'jumlah': self.jumlah_input.value()
        }

class ExpenseView(QWidget):
    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        self.main_window = main_window
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        btn_layout = QHBoxLayout()
        self.add_btn = QPushButton("Catat Pengeluaran Baru")
        self.add_btn.clicked.connect(self.add_expense)

        self.delete_btn = QPushButton("Hapus Pengeluaran")
        self.delete_btn.clicked.connect(self.delete_expense)

        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.delete_btn)
        layout.addLayout(btn_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["ID", "Tanggal", "Kasir", "Kategori", "Deskripsi", "Jumlah (Rp)"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout.addWidget(self.table)

    def load_data(self):
        expenses = db_manager.get_expenses()
        self.table.setRowCount(0)
        for row_idx, exp in enumerate(expenses):
            self.table.insertRow(row_idx)
            self.table.setItem(row_idx, 0, QTableWidgetItem(str(exp['id'])))
            self.table.setItem(row_idx, 1, QTableWidgetItem(exp['tanggal']))
            self.table.setItem(row_idx, 2, QTableWidgetItem(exp['username']))
            self.table.setItem(row_idx, 3, QTableWidgetItem(exp['kategori']))
            self.table.setItem(row_idx, 4, QTableWidgetItem(exp['deskripsi']))
            self.table.setItem(row_idx, 5, QTableWidgetItem(format_rupiah(exp['jumlah_pengeluaran'])))

    def add_expense(self):
        dialog = ExpenseDialog(self)
        if dialog.exec():
            data = dialog.get_data()
            db_manager.add_expense(self.main_window.current_user['id'], data['kategori'], data['deskripsi'], data['jumlah'])
            QMessageBox.information(self, "Sukses", "Pengeluaran berhasil dicatat!")
            self.load_data()

    def delete_expense(self):

        if self.main_window.current_user['role'] != 'admin':
            QMessageBox.warning(self, "Akses Ditolak", "Hanya Admin yang dapat menghapus pengeluaran.")
            return

        selected = self.table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, "Warning", "Pilih pengeluaran yang akan dihapus!")
            return

        exp_id = int(self.table.item(selected, 0).text())
        reply = QMessageBox.question(self, "Konfirmasi", "Yakin ingin menghapus pengeluaran ini?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            db_manager.delete_expense(exp_id)
            QMessageBox.information(self, "Sukses", "Pengeluaran berhasil dihapus!")
            self.load_data()
