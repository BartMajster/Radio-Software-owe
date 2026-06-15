import json
import os
import config
class FavoritesManager:
    def __init__(self):
        self.file_path = config.FAVORITES_PATH
        self.favorites = self._load_favorites()
    def _load_favorites(self):
        if not os.path.exists(self.file_path):
            return []
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return []
    def _save_favorites(self):
        try:
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(self.favorites, f, ensure_ascii=False, indent=4)
        except IOError as e:
            print(f"Error saving favorites: {e}")
    def add_station(self, station_data):
        if not self.is_favorite(station_data):
            clean_data = {
                'name': station_data.get('name', 'Unknown'),
                'url_resolved': station_data.get('url_resolved', ''),
                'countrycode': station_data.get('countrycode', ''),
                'tags': station_data.get('tags', '')
            }
            self.favorites.append(clean_data)
            self._save_favorites()
    def remove_station(self, station_data):
        url = station_data.get('url_resolved')
        self.favorites = [s for s in self.favorites if s.get('url_resolved') != url]
        self._save_favorites()
    def is_favorite(self, station_data):
        if not station_data:
            return False
        url = station_data.get('url_resolved')
        for s in self.favorites:
            if s.get('url_resolved') == url:
                return True
        return False
    def get_all(self):
        return self.favorites