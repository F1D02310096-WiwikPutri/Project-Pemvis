import sqlite3
import os
import hashlib
from datetime import datetime

class DatabaseManager:
    def __init__(self, db_name="goldata.db"):
        self.db_path = os.path.join(os.path.dirname(__file__), db_name)
        self.init_db()

    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'kasir',
                is_active INTEGER NOT NULL DEFAULT 1,
                created_at TEXT NOT NULL
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS inventory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                kode_sku TEXT NOT NULL UNIQUE,
                nama_item TEXT NOT NULL,
                jenis TEXT NOT NULL,
                kadar_karat INTEGER NOT NULL,
                berat_gram REAL NOT NULL,
                stok INTEGER NOT NULL DEFAULT 0,
                harga_beli_ref REAL DEFAULT 0
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tanggal TEXT NOT NULL,
                user_id INTEGER NOT NULL,
                item_id INTEGER,
                tipe_transaksi TEXT NOT NULL,
                jumlah INTEGER NOT NULL DEFAULT 1,
                total_harga REAL NOT NULL,
                catatan TEXT DEFAULT '',
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (item_id) REFERENCES inventory (id)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tanggal TEXT NOT NULL,
                user_id INTEGER NOT NULL,
                kategori TEXT NOT NULL,
                deskripsi TEXT NOT NULL,
                jumlah_pengeluaran REAL NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS gold_price_cache (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                harga_per_gram REAL NOT NULL,
                timestamp_update TEXT NOT NULL
            )
        ''')

        cursor.execute("SELECT COUNT(*) as count FROM users WHERE role='admin'")
        if cursor.fetchone()['count'] == 0:
            pw_hash = hashlib.sha256("admin123".encode()).hexdigest()
            now = datetime.now().isoformat()
            cursor.execute('''
                INSERT INTO users (username, password_hash, role, created_at)
                VALUES (?, ?, ?, ?)
            ''', ('admin', pw_hash, 'admin', now))

        conn.commit()
        conn.close()

    def get_user_by_username(self, username):
        conn = self.get_connection()
        user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        conn.close()
        return dict(user) if user else None

    def get_all_users(self):
        conn = self.get_connection()
        users = conn.execute("SELECT * FROM users").fetchall()
        conn.close()
        return [dict(u) for u in users]

    def add_user(self, username, password, role):
        conn = self.get_connection()
        pw_hash = hashlib.sha256(password.encode()).hexdigest()
        now = datetime.now().isoformat()
        try:
            conn.execute('''
                INSERT INTO users (username, password_hash, role, created_at)
                VALUES (?, ?, ?, ?)
            ''', (username, pw_hash, role, now))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()

    def update_user(self, user_id, username, password=None, role=None, is_active=None):
        conn = self.get_connection()
        try:
            if password:
                pw_hash = hashlib.sha256(password.encode()).hexdigest()
                conn.execute("UPDATE users SET username=?, password_hash=?, role=?, is_active=? WHERE id=?",
                             (username, pw_hash, role, is_active, user_id))
            else:
                conn.execute("UPDATE users SET username=?, role=?, is_active=? WHERE id=?",
                             (username, role, is_active, user_id))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()

    def get_all_inventory(self):
        conn = self.get_connection()
        items = conn.execute("SELECT * FROM inventory").fetchall()
        conn.close()
        return [dict(i) for i in items]

    def get_inventory_by_id(self, item_id):
        conn = self.get_connection()
        item = conn.execute("SELECT * FROM inventory WHERE id=?", (item_id,)).fetchone()
        conn.close()
        return dict(item) if item else None

    def add_inventory(self, sku, nama, jenis, karat, berat, stok, harga_ref):
        conn = self.get_connection()
        try:
            conn.execute('''
                INSERT INTO inventory (kode_sku, nama_item, jenis, kadar_karat, berat_gram, stok, harga_beli_ref)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (sku, nama, jenis, karat, berat, stok, harga_ref))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()

    def update_inventory(self, item_id, sku, nama, jenis, karat, berat, stok, harga_ref):
        conn = self.get_connection()
        try:
            conn.execute('''
                UPDATE inventory SET kode_sku=?, nama_item=?, jenis=?, kadar_karat=?, berat_gram=?, stok=?, harga_beli_ref=?
                WHERE id=?
            ''', (sku, nama, jenis, karat, berat, stok, harga_ref, item_id))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()

    def delete_inventory(self, item_id):
        conn = self.get_connection()
        conn.execute("DELETE FROM inventory WHERE id=?", (item_id,))
        conn.commit()
        conn.close()

    def record_sale(self, user_id, item_id, jumlah, total_harga, catatan=""):
        conn = self.get_connection()
        now = datetime.now().isoformat()
        try:
            cursor = conn.cursor()

            stok = cursor.execute("SELECT stok FROM inventory WHERE id=?", (item_id,)).fetchone()['stok']
            if stok < jumlah:
                raise ValueError("Stok tidak mencukupi")

            cursor.execute('''
                INSERT INTO transactions (tanggal, user_id, item_id, tipe_transaksi, jumlah, total_harga, catatan)
                VALUES (?, ?, ?, 'penjualan', ?, ?, ?)
            ''', (now, user_id, item_id, jumlah, total_harga, catatan))

            cursor.execute("UPDATE inventory SET stok = stok - ? WHERE id=?", (jumlah, item_id))
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def record_buyback(self, user_id, total_harga, catatan=""):
        conn = self.get_connection()
        now = datetime.now().isoformat()
        try:
            conn.execute('''
                INSERT INTO transactions (tanggal, user_id, item_id, tipe_transaksi, jumlah, total_harga, catatan)
                VALUES (?, ?, NULL, 'buyback', 1, ?, ?)
            ''', (now, user_id, total_harga, catatan))
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def get_transactions(self, tipe=None, start_date=None, end_date=None, user_id=None):
        conn = self.get_connection()
        query = '''
            SELECT t.*, u.username, i.nama_item
            FROM transactions t
            JOIN users u ON t.user_id = u.id
            LEFT JOIN inventory i ON t.item_id = i.id
            WHERE 1=1
        '''
        params = []
        if tipe and tipe != 'Semua':
            query += " AND t.tipe_transaksi = ?"
            params.append(tipe.lower())
        if start_date:
            query += " AND date(t.tanggal) >= date(?)"
            params.append(start_date)
        if end_date:
            query += " AND date(t.tanggal) <= date(?)"
            params.append(end_date)
        if user_id:
            query += " AND t.user_id = ?"
            params.append(user_id)

        query += " ORDER BY t.tanggal DESC"

        items = conn.execute(query, params).fetchall()
        conn.close()
        return [dict(i) for i in items]

    def add_expense(self, user_id, kategori, deskripsi, jumlah):
        conn = self.get_connection()
        now = datetime.now().isoformat()
        conn.execute('''
            INSERT INTO expenses (tanggal, user_id, kategori, deskripsi, jumlah_pengeluaran)
            VALUES (?, ?, ?, ?, ?)
        ''', (now, user_id, kategori, deskripsi, jumlah))
        conn.commit()
        conn.close()

    def get_expenses(self, start_date=None, end_date=None):
        conn = self.get_connection()
        query = '''
            SELECT e.*, u.username
            FROM expenses e
            JOIN users u ON e.user_id = u.id
            WHERE 1=1
        '''
        params = []
        if start_date:
            query += " AND date(e.tanggal) >= date(?)"
            params.append(start_date)
        if end_date:
            query += " AND date(e.tanggal) <= date(?)"
            params.append(end_date)

        query += " ORDER BY e.tanggal DESC"

        items = conn.execute(query, params).fetchall()
        conn.close()
        return [dict(i) for i in items]

    def delete_expense(self, expense_id):
        conn = self.get_connection()
        conn.execute("DELETE FROM expenses WHERE id=?", (expense_id,))
        conn.commit()
        conn.close()

    def update_gold_price(self, price):
        conn = self.get_connection()
        now = datetime.now().isoformat()
        conn.execute("INSERT INTO gold_price_cache (harga_per_gram, timestamp_update) VALUES (?, ?)", (price, now))
        conn.commit()
        conn.close()

    def get_latest_gold_price(self):
        conn = self.get_connection()
        item = conn.execute("SELECT * FROM gold_price_cache ORDER BY id DESC LIMIT 1").fetchone()
        conn.close()
        return dict(item) if item else None

    def get_dashboard_stats(self, start_date, end_date):
        conn = self.get_connection()

        omzet = conn.execute('''
            SELECT SUM(total_harga) as total
            FROM transactions
            WHERE tipe_transaksi='penjualan' AND date(tanggal) >= date(?) AND date(tanggal) <= date(?)
        ''', (start_date, end_date)).fetchone()['total'] or 0

        buyback = conn.execute('''
            SELECT SUM(total_harga) as total
            FROM transactions
            WHERE tipe_transaksi='buyback' AND date(tanggal) >= date(?) AND date(tanggal) <= date(?)
        ''', (start_date, end_date)).fetchone()['total'] or 0

        expenses = conn.execute('''
            SELECT SUM(jumlah_pengeluaran) as total
            FROM expenses
            WHERE date(tanggal) >= date(?) AND date(tanggal) <= date(?)
        ''', (start_date, end_date)).fetchone()['total'] or 0

        stok = conn.execute("SELECT SUM(stok) as total FROM inventory").fetchone()['total'] or 0

        conn.close()
        return {
            'omzet': omzet,
            'buyback': buyback,
            'pengeluaran': expenses,
            'stok': stok
        }

db_manager = DatabaseManager()
