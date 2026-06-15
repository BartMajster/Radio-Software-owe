from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, 
                             QPushButton, QListWidget, QListWidgetItem, 
                             QLabel, QSlider, QScroller, QStackedWidget, QSizePolicy, QDialog)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QDateTime, QLocale
import config
from core.audio_player import RadioPlayer
from core.radio_api import SearchWorker
from core.favorites_manager import FavoritesManager
from ui.components.virtual_keyboard import VirtualKeyboard

class RadioScreen(QWidget):
    go_back = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.player = RadioPlayer()
        self.worker = None
        self.fav_manager = FavoritesManager()
        
        self.was_playing_before_alarm = False
        self.current_search_mode = 'byname'
        self.current_station_data = None
        
        self.meta_timer = QTimer()
        self.meta_timer.timeout.connect(self._update_metadata)
        
        self.clock_timer = QTimer()
        self.clock_timer.timeout.connect(self._update_clock)
        
        self._init_ui()
        self.clock_timer.start(1000)
        self._update_clock()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        header_widget = QWidget()
        header_widget.setStyleSheet("background-color: #222; border-bottom: 2px solid #444;")
        header_widget.setFixedHeight(100)
        header_layout = QGridLayout(header_widget)
        header_layout.setContentsMargins(10, 10, 10, 10)

        clock_container = QWidget()
        clock_layout = QVBoxLayout(clock_container)
        clock_layout.setContentsMargins(0,0,0,0)
        clock_layout.setSpacing(0)
        self.time_label = QLabel("--:--")
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.time_label.setStyleSheet("font-size: 40px; font-weight: bold; color: white;")
        self.date_label = QLabel("...")
        self.date_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.date_label.setStyleSheet("font-size: 14px; color: #bbb;")
        clock_layout.addWidget(self.time_label)
        clock_layout.addWidget(self.date_label)
        header_layout.addWidget(clock_container, 0, 0, Qt.AlignmentFlag.AlignCenter)

        self.btn_back = QPushButton("⬅")
        self.btn_back.setFixedSize(80, 80)
        self.btn_back.setStyleSheet(config.SIDE_CARD_STYLE + "font-size: 40px;")
        self.btn_back.clicked.connect(self._handle_back_nav)
        header_layout.addWidget(self.btn_back, 0, 0, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        
        main_layout.addWidget(header_widget)

        self.stack = QStackedWidget()
        main_layout.addWidget(self.stack)

        self.page_menu = QWidget()
        self._setup_menu_page()
        self.stack.addWidget(self.page_menu)

        self.page_list = QWidget()
        self._setup_list_page()
        self.stack.addWidget(self.page_list)

        controls_container = QWidget()
        controls_container.setStyleSheet("background-color: #222; border-top: 2px solid #444;")
        controls_layout = QHBoxLayout(controls_container)
        controls_layout.setContentsMargins(10, 10, 10, 10)
        
        self.btn_fav = QPushButton("❤")
        self.btn_fav.setFixedSize(60, 50)
        self.btn_fav.setStyleSheet(config.BTN_STYLE_FAV_OFF)
        self.btn_fav.hide() 
        self.btn_fav.clicked.connect(self._toggle_favorite)
        controls_layout.addWidget(self.btn_fav)

        self.info_label = QLabel("Ready")
        self.info_label.setStyleSheet("font-size: 16px; color: #4db8ff; font-weight: bold; margin-left: 10px;")
        controls_layout.addWidget(self.info_label, stretch=1)
        
        stop_btn = QPushButton("STOP")
        stop_btn.setFixedSize(90, 50)
        stop_btn.setStyleSheet(config.BTN_STYLE_RED)
        stop_btn.clicked.connect(self._stop_radio)
        controls_layout.addWidget(stop_btn)
        
        self.vol_slider = QSlider(Qt.Orientation.Horizontal)
        self.vol_slider.setStyleSheet(config.SLIDER_STYLE)
        self.vol_slider.setFixedWidth(150)
        self.vol_slider.setRange(0, 100)
        self.vol_slider.setValue(80)
        self.vol_slider.valueChanged.connect(self.player.set_volume)
        controls_layout.addWidget(self.vol_slider)
        
        main_layout.addWidget(controls_container)

    def _setup_menu_page(self):
        layout = QGridLayout(self.page_menu)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        options = [
            ("❤️\nFavorites", "favorites", "#d70050"),
            ("🔍\nSearch Name", "byname", "#0078d7"),
            ("🌍\nSearch Country", "bycountry", "#28a745"),
            ("🏷️\nSearch Genre", "bytag", "#6f42c1"),
            ("⭐\nTop 100", "top", "#ffc107")
        ]

        positions = [(0,0), (0,1), (0,2), (1,0), (1,1)]

        for i, (text, mode, color) in enumerate(options):
            btn = QPushButton(text)
            btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: #3a3a3a;
                    border: 2px solid {color};
                    border-radius: 15px;
                    font-size: 22px;
                    font-weight: bold;
                    color: white;
                }}
                QPushButton:pressed {{ background-color: {color}; }}
            """)
            btn.clicked.connect(lambda _, m=mode: self._switch_to_search(m))
            if i < len(positions):
                layout.addWidget(btn, positions[i][0], positions[i][1])

    def _setup_list_page(self):
        layout = QVBoxLayout(self.page_list)
        layout.setContentsMargins(10, 10, 10, 10)
        
        self.search_container = QWidget()
        search_layout = QHBoxLayout(self.search_container)
        search_layout.setContentsMargins(0, 0, 0, 0)
        
        self.search_input_btn = QPushButton("Enter text here...")
        self.search_input_btn.setStyleSheet("""
            text-align: left; padding: 10px; font-size: 24px; 
            background-color: #444; border: 1px solid #555; color: #aaa; border-radius: 5px;
        """)
        self.search_input_btn.setFixedHeight(60)
        self.search_input_btn.clicked.connect(self._open_keyboard)
        
        search_layout.addWidget(self.search_input_btn)
        layout.addWidget(self.search_container)

        self.status_label = QLabel("Results")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("color: #aaa; font-size: 16px; margin: 5px;")
        layout.addWidget(self.status_label)

        self.station_list = QListWidget()
        self.station_list.setStyleSheet(config.LIST_STYLE)
        QScroller.grabGesture(self.station_list.viewport(), QScroller.ScrollerGestureType.TouchGesture)
        QScroller.grabGesture(self.station_list.viewport(), QScroller.ScrollerGestureType.LeftMouseButtonGesture)
        self.station_list.itemClicked.connect(self._play_station)
        layout.addWidget(self.station_list)

    def _open_keyboard(self):
        current_text = self.search_input_btn.text()
        
        if current_text in ["Enter text here...", "Enter name...", "Enter country (e.g. Poland)...", "Enter genre (e.g. Rock)..."]:
            current_text = ""
            
        kb = VirtualKeyboard(initial_text=current_text, parent=self)
        
        if kb.exec(): 
            query = kb.get_text()
            if query:
                self.search_input_btn.setText(query)
                self.search_input_btn.setStyleSheet("text-align: left; padding: 10px; font-size: 24px; background-color: #444; border: 1px solid #555; color: #fff; border-radius: 5px;")
                self._execute_search(query)

    def _switch_to_search(self, mode):
        self.current_search_mode = mode
        self.stack.setCurrentIndex(1)
        self.station_list.clear()
        self.status_label.setText("")

        if mode == 'favorites':
            self.search_container.hide()
            self.status_label.setText("Your favorite stations")
            self._load_favorites_list()
        elif mode == 'top':
            self.search_container.hide()
            self.status_label.setText("Loading Top 100...")
            self._execute_search("")
        else:
            self.search_container.show()
            placeholders = {
                'byname': "Enter name...",
                'bycountry': "Enter country (e.g. Poland)...",
                'bytag': "Enter genre (e.g. Rock)..."
            }
            self.search_input_btn.setText(placeholders.get(mode, "..."))
            self.search_input_btn.setStyleSheet("text-align: left; padding: 10px; font-size: 24px; background-color: #444; border: 1px solid #555; color: #aaa; border-radius: 5px;")

    def _load_favorites_list(self):
        stations = self.fav_manager.get_all()
        self._on_results(stations)
        if not stations:
            self.status_label.setText("No favorites. Add some with the heart!")

    def _execute_search(self, query):
        if self.current_search_mode not in ['top', 'favorites'] and not query:
            return

        self.status_label.setText("Loading data...")
        self.station_list.clear()
        
        self.worker = SearchWorker(self.current_search_mode, query)
        self.worker.results_found.connect(self._on_results)
        self.worker.error_occurred.connect(lambda e: self.status_label.setText(f"Error: {e}"))
        self.worker.start()

    def _on_results(self, stations):
        self.status_label.setText(f"Found: {len(stations)}")
        self.station_list.setUpdatesEnabled(False)
        for station in stations:
            name = station.get('name', 'Unknown').strip()
            if not name: continue
            
            tags = station.get('tags', '')
            if len(tags) > 30: tags = tags[:27] + "..."
            
            display_text = f"{name}"
            if tags:
                display_text += f"\n   {tags}"
            
            item = QListWidgetItem(display_text)
            item.setData(Qt.ItemDataRole.UserRole, station)
            self.station_list.addItem(item)
        self.station_list.setUpdatesEnabled(True)

    def _play_station(self, item):
        station_data = item.data(Qt.ItemDataRole.UserRole)
        self.current_station_data = station_data
        
        url = station_data.get('url_resolved', '')
        name = station_data.get('name', 'Station')
        
        self.player.play(url)
        self.info_label.setText(f"Connecting: {name[:15]}...") 
        self.meta_timer.start(1000)
        
        self.btn_fav.show()
        self._update_fav_button()

    def _toggle_favorite(self):
        if not self.current_station_data:
            return
            
        if self.fav_manager.is_favorite(self.current_station_data):
            self.fav_manager.remove_station(self.current_station_data)
        else:
            self.fav_manager.add_station(self.current_station_data)
            
        self._update_fav_button()
        
        if self.current_search_mode == 'favorites' and self.stack.currentIndex() == 1:
            self.station_list.clear()
            self._load_favorites_list()

    def _update_fav_button(self):
        if self.current_station_data and self.fav_manager.is_favorite(self.current_station_data):
            self.btn_fav.setStyleSheet(config.BTN_STYLE_FAV_ON)
        else:
            self.btn_fav.setStyleSheet(config.BTN_STYLE_FAV_OFF)

    def _handle_back_nav(self):
        if self.stack.currentIndex() == 1:
            self.stack.setCurrentIndex(0)
            self.search_input_btn.setText("Enter text here...")
        else:
            self.go_back.emit()

    def mute_radio_for_alarm(self):
        if self.player.player.is_playing():
            self.was_playing_before_alarm = True
            self.player.stop()
            self.meta_timer.stop()
            self.info_label.setText("ALARM!")
            self.btn_fav.hide()
        else:
            self.was_playing_before_alarm = False

    def unmute_radio_after_alarm(self):
        if self.was_playing_before_alarm:
            self.player.player.play()
            self.meta_timer.start(1000)
            self.btn_fav.show()

    def _stop_radio(self):
        self.player.stop()
        self.meta_timer.stop()
        self.info_label.setText("Stopped")
        self.btn_fav.hide()

    def _update_metadata(self):
        meta = self.player.get_now_playing()
        if meta:
            if len(meta) > 35: meta = meta[:32] + "..."
            self.info_label.setText(f"{meta}")

    def _update_clock(self):
        curr = QDateTime.currentDateTime()
        self.time_label.setText(curr.toString("HH:mm"))
        pl_locale = QLocale(QLocale.Language.Polish)
        self.date_label.setText(pl_locale.toString(curr, "dddd, d MMMM"))
