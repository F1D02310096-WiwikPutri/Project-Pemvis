class Validator:
    @staticmethod
    def is_not_empty(value, field_name):
        if not str(value).strip():
            return False, f"Field '{field_name}' tidak boleh kosong!"
        return True, ""

    @staticmethod
    def is_positive_number(value, field_name):
        try:
            val = float(value)
            if val <= 0:
                return False, f"Nilai '{field_name}' harus lebih besar dari 0!"
            return True, ""
        except ValueError:
            return False, f"Nilai '{field_name}' harus berupa angka!"

    @staticmethod
    def is_valid_integer(value, field_name):
        try:
            val = int(value)
            if val < 0:
                return False, f"Nilai '{field_name}' tidak boleh negatif!"
            return True, ""
        except ValueError:
            return False, f"Nilai '{field_name}' harus berupa bilangan bulat!"

    @staticmethod
    def check_stock(available, requested):
        if requested > available:
            return False, f"Stok tidak mencukupi! Tersedia: {available} item."
        return True, ""
