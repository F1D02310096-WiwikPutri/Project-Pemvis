import csv
from database.db_manager import db_manager

class Importer:
    @staticmethod
    def import_csv_inventory(file_path):
        success_count = 0
        error_count = 0
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                reader = csv.reader(file)
                headers = next(reader, None) # skip header
                
                for row in reader:
                    if len(row) >= 7:
                        # Asumsi format CSV: Kode SKU, Nama Item, Jenis, Karat, Berat (g), Stok, Harga Beli Ref
                        sku = row[0].strip()
                        nama = row[1].strip()
                        jenis = row[2].strip()
                        
                        try:
                            karat = int(row[3])
                            berat = float(row[4])
                            stok = int(row[5])
                            harga = float(row[6])
                            
                            if db_manager.add_inventory(sku, nama, jenis, karat, berat, stok, harga):
                                success_count += 1
                            else:
                                error_count += 1
                        except ValueError:
                            error_count += 1
                    else:
                        error_count += 1
            return True, f"Berhasil mengimpor {success_count} item. Gagal: {error_count} item."
        except Exception as e:
            return False, f"Terjadi kesalahan saat import CSV: {str(e)}"
