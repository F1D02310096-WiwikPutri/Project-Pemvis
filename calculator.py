class Calculator:
    KARAT_FACTOR = {
        24: 1.0,
        22: 0.916,
        18: 0.75,
        14: 0.583
    }

    @staticmethod
    def calculate_sale_price(berat_gram, harga_emas_per_gram, karat, biaya_pembuatan=0):
        """
        Total = (Berat * Harga Emas * Faktor Karat) + Biaya Pembuatan
        """
        faktor = Calculator.KARAT_FACTOR.get(karat, 1.0)
        harga_dasar = berat_gram * harga_emas_per_gram * faktor
        return harga_dasar + biaya_pembuatan

    @staticmethod
    def calculate_buyback_price(berat_gram, harga_emas_per_gram, karat, persen_potongan):
        """
        Harga beli = (Berat * Harga Emas * Faktor Karat) * (1 - Potongan/100)
        """
        faktor = Calculator.KARAT_FACTOR.get(karat, 1.0)
        harga_dasar = berat_gram * harga_emas_per_gram * faktor
        potongan = harga_dasar * (persen_potongan / 100.0)
        return harga_dasar - potongan
