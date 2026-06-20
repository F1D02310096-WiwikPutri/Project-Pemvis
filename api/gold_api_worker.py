from PySide6.QtCore import QObject, Signal
from api.gold_api_service import GoldApiService

class GoldPriceWorker(QObject):
    result = Signal(float)
    error = Signal(str)
    finished = Signal()

    def run(self):
        try:
            price = GoldApiService.get_live_price_per_gram()
            self.result.emit(price)
        except Exception as e:
            self.error.emit(str(e))
        finally:
            self.finished.emit()
