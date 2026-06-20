import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.db_manager import db_manager
from datetime import datetime, timedelta

def seed_data():
    print("Mulai menambahkan data dummy ke database...")

    if not db_manager.get_inventory_by_id(1):
        db_manager.add_inventory('SKU-001', 'Cincin Emas 24K', 'Cincin', 24, 5.5, 10, 5000000)
        db_manager.add_inventory('SKU-002', 'Kalung Emas Putih', 'Kalung', 18, 12.0, 5, 8000000)
        db_manager.add_inventory('SKU-003', 'Gelang Rantai', 'Gelang', 22, 8.5, 15, 6000000)
        db_manager.add_inventory('SKU-004', 'Anting Mutiara', 'Anting', 20, 3.0, 8, 2500000)
        db_manager.add_inventory('SKU-005', 'Liontin Berlian', 'Liontin', 18, 2.5, 3, 15000000)
        print("Data inventory ditambahkan.")

    user = db_manager.get_user_by_username('admin')
    user_id = user['id'] if user else 1

    transaksi = db_manager.get_transactions()
    if not transaksi:

        try:
            db_manager.record_sale(user_id, 1, 2, 12000000, "Penjualan 2 Cincin")
            db_manager.record_sale(user_id, 2, 1, 9500000, "Penjualan 1 Kalung")
            db_manager.record_sale(user_id, 3, 3, 20000000, "Penjualan Gelang")
            db_manager.record_sale(user_id, 4, 1, 3000000, "Penjualan Anting")

            db_manager.record_buyback(user_id, 4500000, "Buyback cincin lama 24K")
            db_manager.record_buyback(user_id, 2000000, "Buyback anting")
            print("Data transaksi ditambahkan.")
        except Exception as e:
            print(f"Gagal menambahkan transaksi: {e}")

    pengeluaran = db_manager.get_expenses()
    if not pengeluaran:
        db_manager.add_expense(user_id, 'Operasional', 'Listrik', 500000)
        db_manager.add_expense(user_id, 'Operasional', 'Internet', 350000)
        db_manager.add_expense(user_id, 'Gaji', 'Gaji Kasir', 3000000)
        db_manager.add_expense(user_id, 'Lain-lain', 'Beli lakban dan alat tulis', 150000)
        print("Data pengeluaran ditambahkan.")

    print("Seeding database selesai!")

if __name__ == '__main__':
    seed_data()
