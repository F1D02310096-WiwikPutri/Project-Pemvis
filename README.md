# Goldata - Sistem Manajemen Toko Emas

Aplikasi Desktop GUI berbasis Python dan PySide6 untuk manajemen inventaris dan transaksi toko emas. Aplikasi ini dilengkapi dengan fitur integrasi *real-time* harga emas melalui API.

## Persyaratan Sistem
- Python 3.9 atau lebih baru.
- Modul yang tercantum dalam file `requirements.txt`.

## Cara Instalasi dan Setup

Ikuti langkah-langkah di bawah ini untuk menjalankan aplikasi di komputer Anda:

### 1. Instalasi Dependensi
Buka terminal/CMD di dalam *folder* proyek ini, lalu jalankan perintah berikut untuk menginstal pustaka yang dibutuhkan:
```bash
pip install -r requirements.txt
```

### 2. Konfigurasi API Key
Aplikasi ini membutuhkan API Key dari [goldapi.io](https://www.goldapi.io/) untuk menarik data harga emas secara *real-time*.
1. *Copy* atau *rename* file `config.example.py` menjadi **`config.py`**.
2. Buka file `config.py` tersebut.
3. Masukkan `API_KEY` yang telah diberikan oleh tim ke dalam variabel `GOLD_API_KEY`.

*(Catatan: File `config.py` sudah diatur di dalam `.gitignore` sehingga API Key Anda aman dan tidak akan ter-push ke GitHub).*

### 3. Inisialisasi Database (Data Dummy)
Jika ini adalah pertama kalinya Anda menjalankan aplikasi, Anda perlu membuat *database* awal beserta akun *login* default dan data *dummy* transaksi. Jalankan skrip ini:
```bash
python seed_db.py
```
Perintah ini akan secara otomatis membuat file `database/goldata.db`.

### 4. Menjalankan Aplikasi
Setelah *setup* selesai, Anda bisa membuka aplikasi dengan menjalankan perintah:
```bash
python main.py
```

## Kredensial Login Default
Jika Anda menggunakan data *dummy* dari `seed_db.py`, Anda dapat *login* dengan menggunakan akun admin bawaan:
- **Username:** `admin`
- **Password:** `admin123`
*(Catatan: Anda bisa menambahkan user baru lewat menu Manajemen User di dalam aplikasi).*

---
**Catatan untuk Anggota Kelompok:** Pastikan Anda **tidak** meng-commit file `config.py` atau `database/goldata.db`. Semua aturan ini sudah diatur dengan aman di file `.gitignore` bawaan.
