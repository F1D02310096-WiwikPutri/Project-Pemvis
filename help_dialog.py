from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt

class HelpDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Bantuan & Informasi")
        self.setFixedSize(400, 250)
        
        layout = QVBoxLayout(self)
        
        title = QLabel("Goldata - Sistem Manajemen Toko Emas")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #b8860b;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        desc = QLabel(
            "Aplikasi ini dikembangkan untuk memanajemen inventaris, \n"
            "mencatat transaksi penjualan dan buyback, serta mencatat \n"
            "pengeluaran operasional toko emas.\n\n"
            "Panduan Singkat:\n"
            "- Gunakan File > Upload CSV untuk menambah stok massal.\n"
            "- Gunakan menu samping untuk navigasi.\n"
            "- Admin memiliki akses Laporan dan Manajemen Akun."
        )
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(desc)
        
        layout.addStretch()
        
        btn_close = QPushButton("Tutup")
        btn_close.clicked.connect(self.accept)
        btn_close.setStyleSheet("background-color: #34495e; color: white; padding: 8px;")
        layout.addWidget(btn_close)
