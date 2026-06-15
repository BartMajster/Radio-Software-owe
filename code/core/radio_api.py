import requests
from PyQt6.QtCore import QThread, pyqtSignal
import config
class SearchWorker(QThread):
    results_found = pyqtSignal(list)
    error_occurred = pyqtSignal(str)
    def __init__(self, mode, query=""):
        super().__init__()
        self.mode = mode
        self.query = query
    def run(self):
        base_url = "https://all.api.radio-browser.info/json/stations"
        if self.mode == 'top':
            url = f"{base_url}/topclick?limit=100"
        elif self.mode == 'bycountry':
            url = f"{base_url}/bycountry/{self.query}?order=clickcount&reverse=true"
        elif self.mode == 'bytag':
            url = f"{base_url}/bytag/{self.query}?order=clickcount&reverse=true"
        else:
            url = f"{base_url}/byname/{self.query}?order=clickcount&reverse=true"
        headers = {'User-Agent': config.USER_AGENT}
        try:
            print(f"API Request: {url}")
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            self.results_found.emit(data)
        except Exception as e:
            print(f"API Error: {e}")
            self.error_occurred.emit(str(e))