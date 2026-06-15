import os

APP_TITLE = "RPi Media System"
WINDOW_SIZE = (800, 480)

API_URL = "https://all.api.radio-browser.info/json/stations/byname/{}?order=clickcount&reverse=true"
USER_AGENT = "PythonRadioPro/1.0"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ALARM_SOUND_PATH = os.path.join(BASE_DIR, "resources", "alarm.mp3")
FAVORITES_PATH = os.path.join(BASE_DIR, "favorites.json")
TIMER_PRESETS_PATH = os.path.join(BASE_DIR, "timer_presets.json")

MAIN_STYLE = """
    QMainWindow, QWidget { background-color: #2b2b2b; color: #ffffff; }
    
    QLineEdit {
        font-size: 24px;
        padding: 10px; color: #ddd;
        background-color: #444; border: 1px solid #555; border-radius: 5px;
    }
    
    QLabel { font-size: 16px; color: #ffffff; }
    
    QSpinBox {
        font-size: 30px; padding: 10px;
        background-color: #444; color: white; border: 1px solid #555; border-radius: 5px;
    }
    QSpinBox::up-button, QSpinBox::down-button { width: 60px; }

    QScrollBar:vertical {
        border: none;
        background: #333;
        width: 45px; 
        margin: 0px;
    }
    QScrollBar::handle:vertical {
        background: #0078d7;
        min-height: 60px;
        border-radius: 10px;
    }
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
        height: 0px;
    }
"""

MENU_CARD_STYLE = """
    QPushButton {
        background-color: #3a3a3a;
        color: white;
        font-size: 40px;
        font-weight: bold;
        border-radius: 30px;
        border: 4px solid #0078d7;
        margin: 0px;
    }
    QPushButton:pressed { background-color: #0078d7; }
"""

SIDE_CARD_STYLE = """
    QPushButton {
        background-color: #222;
        color: #777;
        font-size: 20px;
        font-weight: bold;
        border-radius: 20px;
        border: 2px solid #444;
        margin: 0px;
    }
    QPushButton:pressed { background-color: #333; color: #ddd; }
"""

BTN_STYLE_BLUE = """
    QPushButton {
        background-color: #0078d7; color: white;
        font-size: 20px; font-weight: bold;
        border-radius: 8px; padding: 10px; min-height: 60px;
    }
    QPushButton:pressed { background-color: #005a9e; }
"""

BTN_STYLE_RED = """
    QPushButton {
        background-color: #d70000; 
        color: white;
        font-size: 20px; 
        font-weight: bold;
        border-radius: 30px;
        border: none;
    }
    QPushButton:pressed { background-color: #a00000; }
"""

BTN_STYLE_ORANGE = """
    QPushButton {
        background-color: #ff8c00; color: white;
        font-size: 20px; font-weight: bold;
        border-radius: 8px; padding: 10px; min-height: 60px;
        animation: blinking 1s infinite;
    }
    QPushButton:pressed { background-color: #e07b00; }
"""

BTN_STYLE_GRAY = """
    QPushButton {
        background-color: #555555; color: white;
        font-size: 18px; font-weight: bold;
        border: 2px solid #777; border-radius: 8px; padding: 5px;
    }
    QPushButton:pressed { background-color: #333333; }
"""

BTN_STYLE_FAV_ON = """
    QPushButton {
        background-color: #d70050; color: white;
        font-size: 24px; border-radius: 8px; border: 2px solid #ff6699;
    }
"""

BTN_STYLE_FAV_OFF = """
    QPushButton {
        background-color: #444; color: #888;
        font-size: 24px; border-radius: 8px; border: 2px solid #555;
    }
"""

PRESET_BTN_STYLE = """
    QPushButton {
        background-color: #333;
        color: #ddd;
        font-size: 18px;
        font-weight: bold;
        border-radius: 15px;
        border: 2px solid #444;
        padding: 5px;
    }
    QPushButton:pressed {
        background-color: #0078d7; border-color: #0078d7; color: white;
    }
"""

LIST_STYLE = """
    QListWidget {
        font-size: 22px; color: #ddd; background-color: #333;
        border: none; outline: none;
    }
    QListWidget::item {
        height: 80px; padding-left: 15px; border-bottom: 2px solid #444;
    }
    QListWidget::item:selected { background-color: #0078d7; color: white; }
"""

SLIDER_STYLE = """
    QSlider::groove:horizontal {
        border: 1px solid #999; height: 10px; background: #555;
        margin: 2px 0; border-radius: 5px;
    }
    QSlider::handle:horizontal {
        background: #0078d7; border: 1px solid #5c5c5c;
        width: 40px; height: 40px; margin: -15px 0; border-radius: 20px;
    }
"""

KB_BTN_STYLE = """
    QPushButton {
        background-color: #444; color: white;
        font-size: 24px; font-weight: bold;
        border-radius: 8px; border: 1px solid #666;
    }
    QPushButton:pressed { background-color: #0078d7; border: 1px solid #0078d7; }
"""