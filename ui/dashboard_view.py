from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                               QLabel, QFrame, QComboBox, QSplitter)
from PySide6.QtCore import Qt, QThread
import matplotlib
matplotlib.use('QtAgg')
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import pandas as pd
from database.db_manager import db_manager
from utils.helpers import format_rupiah
from api.gold_api_worker import GoldPriceWorker
from datetime import datetime, timedelta

class DashboardView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.gold_price = 0.0
        self.setup_ui()
        self.setup_api_worker()
        self.update_dashboard()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        header_layout = QHBoxLayout()
        title = QLabel("Dashboard")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")

        self.gold_price_label = QLabel("Harga Emas (Live): Mengambil data...")
        self.gold_price_label.setStyleSheet("font-size: 16px; color: #b8860b; font-weight: bold;")

        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(self.gold_price_label)
        layout.addLayout(header_layout)

        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Periode:"))
        self.period_combo = QComboBox()
        self.period_combo.addItems(["Hari Ini", "Minggu Ini", "Bulan Ini"])
        self.period_combo.currentTextChanged.connect(self.update_dashboard)
        filter_layout.addWidget(self.period_combo)
        filter_layout.addStretch()
        layout.addLayout(filter_layout)

        kpi_layout = QHBoxLayout()
        self.card_omzet = self.create_kpi_card("Total Omzet", format_rupiah(0))
        self.card_pengeluaran = self.create_kpi_card("Total Pengeluaran", format_rupiah(0))
        self.card_buyback = self.create_kpi_card("Total Buyback", format_rupiah(0))
        self.card_stok = self.create_kpi_card("Total Stok Item", "0")

        kpi_layout.addWidget(self.card_omzet['frame'])
        kpi_layout.addWidget(self.card_pengeluaran['frame'])
        kpi_layout.addWidget(self.card_buyback['frame'])
        kpi_layout.addWidget(self.card_stok['frame'])

        layout.addLayout(kpi_layout)

        self.splitter = QSplitter(Qt.Orientation.Horizontal)

        self.fig_bar = Figure()
        self.canvas_bar = FigureCanvas(self.fig_bar)

        self.fig_pie = Figure()
        self.canvas_pie = FigureCanvas(self.fig_pie)

        self.splitter.addWidget(self.canvas_bar)
        self.splitter.addWidget(self.canvas_pie)

        layout.addWidget(self.splitter, 1)

    def create_kpi_card(self, title, initial_value):
        frame = QFrame()
        frame.setFrameShape(QFrame.Shape.StyledPanel)
        frame.setStyleSheet("background-color: #f0f0f0; border-radius: 10px; padding: 10px;")

        lay = QVBoxLayout(frame)
        lbl_title = QLabel(title)
        lbl_title.setStyleSheet("font-size: 14px; color: #555;")

        lbl_val = QLabel(initial_value)
        lbl_val.setStyleSheet("font-size: 18px; font-weight: bold; color: #333;")

        lay.addWidget(lbl_title)
        lay.addWidget(lbl_val)

        return {'frame': frame, 'value_label': lbl_val}

    def setup_api_worker(self):
        self.worker = GoldPriceWorker()
        self.thread = QThread()
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.result.connect(self.on_price_fetched)
        self.worker.error.connect(self.on_price_error)
        self.worker.finished.connect(self.thread.quit)

        self.thread.start()

    def on_price_fetched(self, price):
        self.gold_price = price
        db_manager.update_gold_price(price)
        self.gold_price_label.setText(f"Harga Emas (Live): {format_rupiah(price)} / gram")

    def on_price_error(self, error_msg):

        cached = db_manager.get_latest_gold_price()
        if cached:
            self.gold_price = cached['harga_per_gram']
            self.gold_price_label.setText(f"Harga Emas (Cached): {format_rupiah(self.gold_price)} / gram")
        else:
            self.gold_price_label.setText("Gagal mengambil harga emas & tidak ada cache!")
            self.gold_price = 0

    def get_date_range(self):
        now = datetime.now()
        period = self.period_combo.currentText()
        if period == "Hari Ini":
            return now.strftime("%Y-%m-%d"), now.strftime("%Y-%m-%d")
        elif period == "Minggu Ini":
            start = now - timedelta(days=now.weekday())
            return start.strftime("%Y-%m-%d"), now.strftime("%Y-%m-%d")
        elif period == "Bulan Ini":
            start = now.replace(day=1)
            return start.strftime("%Y-%m-%d"), now.strftime("%Y-%m-%d")

    def update_dashboard(self):
        start_date, end_date = self.get_date_range()
        stats = db_manager.get_dashboard_stats(start_date, end_date)

        self.card_omzet['value_label'].setText(format_rupiah(stats['omzet']))
        self.card_buyback['value_label'].setText(format_rupiah(stats['buyback']))
        self.card_pengeluaran['value_label'].setText(format_rupiah(stats['pengeluaran']))
        self.card_stok['value_label'].setText(str(stats['stok']))

        self.draw_charts(start_date, end_date)

    def draw_charts(self, start_date, end_date):
        self.fig_bar.clear()
        self.fig_pie.clear()

        ax_bar = self.fig_bar.add_subplot(111)
        ax_pie = self.fig_pie.add_subplot(111)

        transactions = db_manager.get_transactions(tipe='penjualan', start_date=start_date, end_date=end_date)
        if transactions:
            df_t = pd.DataFrame(transactions)
            df_t['tanggal'] = pd.to_datetime(df_t['tanggal']).dt.date
            omzet_harian = df_t.groupby('tanggal')['total_harga'].sum()

            x = [str(date) for date in omzet_harian.index]
            y = omzet_harian.values
            ax_bar.bar(x, y, color='blue')
            ax_bar.set_title("Omzet Penjualan")
            ax_bar.tick_params(axis='x', rotation=45)
        else:
            ax_bar.text(0.5, 0.5, 'Tidak ada data penjualan', ha='center', va='center')

        expenses = db_manager.get_expenses(start_date=start_date, end_date=end_date)
        if expenses:
            df_e = pd.DataFrame(expenses)
            pengeluaran_kat = df_e.groupby('kategori')['jumlah_pengeluaran'].sum()
            ax_pie.pie(pengeluaran_kat.values, labels=pengeluaran_kat.index, autopct='%1.1f%%', startangle=90)
            ax_pie.set_title("Komposisi Pengeluaran")
        else:
            ax_pie.text(0.5, 0.5, 'Tidak ada data pengeluaran', ha='center', va='center')

        self.fig_bar.tight_layout()
        self.fig_pie.tight_layout()

        self.canvas_bar.draw()
        self.canvas_pie.draw()
