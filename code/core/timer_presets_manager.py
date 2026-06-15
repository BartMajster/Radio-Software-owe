import json
import os
import config
class TimerPresetsManager:
    def __init__(self):
        self.file_path = config.TIMER_PRESETS_PATH
        self.default_presets = [
            {"name": "Eggs (5m)", "seconds": 300},
            {"name": "Pasta (10m)", "seconds": 600},
            {"name": "Rice (15m)", "seconds": 900},
            {"name": "Nap (20m)", "seconds": 1200}
        ]
        self.presets = self._load_presets()
    def _load_presets(self):
        if not os.path.exists(self.file_path):
            return list(self.default_presets)
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return list(self.default_presets)
    def _save_presets(self):
        try:
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(self.presets, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"Error saving presets: {e}")
    def get_presets(self):
        return self.presets
    def update_preset(self, index, name, seconds):
        if 0 <= index < len(self.presets):
            self.presets[index] = {"name": name, "seconds": seconds}
            self._save_presets()