from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QPushButton, 
                             QLabel, QSizePolicy, QStackedWidget, QDialog, QSpinBox, QLineEdit)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QDateTime, QRect, QLocale
from PyQt6.QtGui import QPainter, QColor, QPen
import vlc
import config
import os
from core.timer_presets_manager import TimerPresetsManager
from ui.components.virtual_keyboard import VirtualKeyboard

class LongPressButton(QPushButton):
    long_pressed = pyqtSignal()   
    clicked_short = pyqtSignal()  

    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self._on_long_press)
        self._is_long = False

    def mousePressEvent(self, event):
        self._is_long = False
        self._timer.start(800) 
        self.setDown(True) 
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        self._timer.stop()
        self.setDown(False)
        if not self._is_long:
            if self.rect().contains(event.pos()):
                self.clicked_short.emit()

    def _on_long_press(self):
        self._is_long = True
        self.setDown(False) 
        self.long_pressed.emit()

class PresetEditDialog(QDialog):
    def __init__(self, current_name, current_seconds, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Preset")
        self.setFixedSize(400, 300)
        self.setStyleSheet(config.MAIN_STYLE)
        
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Button name:"))
        
        self.name_btn = QPushButton(current_name)
        self.name_btn.setStyleSheet("""
            text-align: left; padding: 10px; font-size: 24px; 
            background-color: #444; border: 1px solid #555; color: #fff; border-radius: 5px;
        """)
        self.name_btn.clicked.connect(self._open_keyboard)
        layout.addWidget(self.name_btn)
        
        layout.addWidget(QLabel("Time (minutes : seconds):"))
        time_layout = QHBoxLayout()
        
        self.min_spin = QSpinBox()
        self.min_spin.setRange(0, 180) 
        self.min_spin.setSuffix(" min")
        self.min_spin.setValue(current_seconds // 60)
        
        self.sec_spin = QSpinBox()
        self.sec_spin.setRange(0, 59)
        self.sec_spin.setSuffix(" sec")
        self.sec_spin.setValue(current_seconds % 60)
        
        time_layout.addWidget(self.min_spin)
        time_layout.addWidget(self.sec_spin)
        layout.addLayout(time_layout)
        
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("SAVE")
        save_btn.setStyleSheet(config.BTN_STYLE_BLUE)
        save_btn.clicked.connect(self.accept)
        
        cancel_btn = QPushButton("CANCEL")
        cancel_btn.setStyleSheet(config.BTN_STYLE_GRAY)
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(save_btn)
        layout.addLayout(btn_layout)

    def _open_keyboard(self):
        kb = VirtualKeyboard(initial_text=self.name_btn.text(), parent=self)
        if kb.exec():
            new_text = kb.get_text()
            if new_text:
                self.name_btn.setText(new_text)

    def get_data(self):
        new_seconds = (self.min_spin.value() * 60) + self.sec_spin.value()
        return self.name_btn.text(), new_seconds

class CircularProgress(QWidget):
    clicked = pyqtSignal() 

    def __init__(self, parent=None):
        super().__init__(parent)
        self.value = 0
        self.max_value = 100
        self.progress_color = QColor("#28a745") 
        self.text_color = QColor("#ffffff")
        self.is_input_mode = False 
        
        self.layout = QVBoxLayout(self)
        self.label = QLabel("00:00")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setStyleSheet("background: transparent; color: white; font-weight: bold;")
        self.layout.addWidget(self.label)
        
    def mousePressEvent(self, event):
        self.clicked.emit()
        super().mousePressEvent(event)

    def set_values(self, current, maximum):
        self.value = current
        self.max_value = maximum
        self._update_color()
        self.update()

    def set_text(self, text, is_input=False):
        self.label.setText(text)
        self.is_input_mode = is_input
        font_size = min(self.width(), self.height()) // 4
        color = "#0078d7" if is_input else self.text_color.name() 
        self.label.setStyleSheet(f"background: transparent; color: {color}; font-weight: bold; font-size: {font_size}px;")

    def _update_color(self):
        if self.is_input_mode:
            self.progress_color = QColor("#0078d7") 
            self.text_color = QColor("#0078d7")
            return

        if self.max_value > 0:
            percent = self.value / self.max_value
            if percent < 0.2: 
                self.progress_color = QColor("#ff4444") 
                self.text_color = QColor("#ff4444")
            elif percent < 0.5: 
                self.progress_color = QColor("#ffc107") 
                self.text_color = QColor("#ffc107")
            else:
                self.progress_color = QColor("#28a745") 
                self.text_color = QColor("#ffffff")
        else:
            self.progress_color = QColor("#444")
            self.text_color = QColor("#ffffff")

    def paintEvent(self, event):
        width = self.width()
        height = self.height()
        margin = 15 
        rect = QRect(margin, margin, width - 2*margin, height - 2*margin)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        pen_bg = QPen(QColor("#333"), 15)
        pen_bg.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen_bg)
        painter.drawEllipse(rect)
        
        should_draw = (self.max_value > 0 and self.value > 0) or self.is_input_mode
        if should_draw:
            pen_progress = QPen(self.progress_color, 15)
            pen_progress.setCapStyle(Qt.PenCapStyle.RoundCap)
            painter.setPen(pen_progress)
            start_angle = 90 * 16
            if self.is_input_mode:
                span_angle = -360 * 16
            else:
                span_angle = int(-(self.value / self.max_value) * 360 * 16)
            painter.drawArc(rect, start_angle, span_angle)
        painter.end()

class TimerScreen(QWidget):
    go_back = pyqtSignal()
    alarm_triggered = pyqtSignal()
    alarm_stopped = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.seconds_left = 0
        self.total_seconds = 1
        self.is_alarm_ringing = False
        self.is_running = False
        self.input_buffer = ""
        
        self.presets_manager = TimerPresetsManager()

        self.timer = QTimer()
        self.timer.timeout.connect(self._tick)

        self.clock_timer = QTimer()
        self.clock_timer.timeout.connect(self._update_clock)
        
        self.vlc_instance = vlc.Instance('--no-video')
        self.alarm_player = self.vlc_instance.media_player_new()
        
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
        self.clock_time_label = QLabel("--:--")
        self.clock_time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.clock_time_label.setStyleSheet("font-size: 40px; font-weight: bold; color: white;")
        self.clock_date_label = QLabel("...")
        self.clock_date_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.clock_date_label.setStyleSheet("font-size: 14px; color: #bbb;")
        clock_layout.addWidget(self.clock_time_label)
        clock_layout.addWidget(self.clock_date_label)
        header_layout.addWidget(clock_container, 0, 0, Qt.AlignmentFlag.AlignCenter)

        btn_back = QPushButton("⬅")
        btn_back.setFixedSize(80, 80)
        btn_back.setStyleSheet(config.SIDE_CARD_STYLE + "font-size: 40px;")
        btn_back.clicked.connect(self._handle_back)
        header_layout.addWidget(btn_back, 0, 0, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        main_layout.addWidget(header_widget)

        content_widget = QWidget()
        content_layout = QHBoxLayout(content_widget)
        
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.circular_progress = CircularProgress()
        self.circular_progress.setFixedSize(240, 240)
        self.circular_progress.clicked.connect(self._handle_circle_click)
        left_layout.addWidget(self.circular_progress)
        
        control_row = QHBoxLayout()
        control_row.setSpacing(15) 
        
        self.btn_start = QPushButton("START")
        self.btn_start.setFixedSize(140, 60)
        self.btn_start.setStyleSheet("background-color: #28a745; color: white; font-size: 20px; border-radius: 30px; font-weight: bold;")
        self.btn_start.clicked.connect(self._toggle_timer_action)
        
        self.btn_reset = QPushButton("RESET")
        self.btn_reset.setFixedSize(140, 60)
        self.btn_reset.setStyleSheet(config.BTN_STYLE_GRAY + "border-radius: 30px;")
        self.btn_reset.clicked.connect(self._reset_timer)
        
        control_row.addWidget(self.btn_start)
        control_row.addWidget(self.btn_reset)
        left_layout.addLayout(control_row)
        
        hint_label = QLabel("Click time to enter manually")
        hint_label.setStyleSheet("color: #777; font-size: 12px; margin-top: 5px;")
        hint_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left_layout.addWidget(hint_label)
        
        content_layout.addWidget(left_panel, stretch=3)

        self.right_stack = QStackedWidget()
        self.page_presets = QWidget()
        self.presets_layout_container = QVBoxLayout(self.page_presets)
        self.presets_layout_container.setSpacing(10)
        self.presets_layout_container.setContentsMargins(10, 10, 20, 10)
        self._rebuild_presets_grid() 
        self.right_stack.addWidget(self.page_presets)
        
        self.page_keypad = QWidget()
        self._setup_keypad_view()
        self.right_stack.addWidget(self.page_keypad)
        
        content_layout.addWidget(self.right_stack, stretch=2)
        main_layout.addWidget(content_widget)
        self._update_display()

    def _handle_circle_click(self):
        if self.is_alarm_ringing:
            self._stop_alarm()
        else:
            self._show_keypad()

    def _rebuild_presets_grid(self):
        while self.presets_layout_container.count():
            item = self.presets_layout_container.takeAt(0)
            widget = item.widget()
            if widget: widget.deleteLater()
            
        label = QLabel("Quick select (Hold to edit):")
        label.setStyleSheet("color: #aaa; font-size: 16px;")
        label.setWordWrap(True)
        self.presets_layout_container.addWidget(label)

        grid = QGridLayout()
        grid.setSpacing(10)
        saved_presets = self.presets_manager.get_presets()
        
        row, col = 0, 0
        for i, p_data in enumerate(saved_presets):
            name = p_data['name']
            seconds = p_data['seconds']
            btn = LongPressButton(name)
            btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            btn.setStyleSheet(config.PRESET_BTN_STYLE)
            btn.clicked_short.connect(lambda s=seconds: self._set_time(s))
            btn.long_pressed.connect(lambda idx=i, n=name, s=seconds: self._edit_preset_dialog(idx, n, s))
            grid.addWidget(btn, row, col)
            col += 1
            if col > 1:
                col = 0
                row += 1
                
        fixed_btns = [("+ 1 min", 60), ("+ 10 min", 600)]
        for name, seconds in fixed_btns:
            btn = QPushButton(name)
            btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            btn.setStyleSheet(config.PRESET_BTN_STYLE)
            btn.clicked.connect(lambda _, s=seconds: self._add_time(s))
            grid.addWidget(btn, row, col)
            col += 1
            if col > 1:
                col = 0
                row += 1
        
        self.presets_layout_container.addLayout(grid)
        btn_clear = QPushButton("Clear Time")
        btn_clear.setFixedHeight(50)
        btn_clear.setStyleSheet(config.BTN_STYLE_GRAY)
        btn_clear.clicked.connect(lambda: self._set_time(0))
        self.presets_layout_container.addWidget(btn_clear)

    def _edit_preset_dialog(self, index, name, seconds):
        if self.is_running: return 
        dlg = PresetEditDialog(name, seconds, self)
        if dlg.exec(): 
            new_name, new_seconds = dlg.get_data()
            if new_seconds > 0:
                self.presets_manager.update_preset(index, new_name, new_seconds)
                self._rebuild_presets_grid() 

    def _setup_keypad_view(self):
        layout = QVBoxLayout(self.page_keypad)
        layout.setContentsMargins(10, 10, 20, 10)
        label = QLabel("Enter time:")
        label.setStyleSheet("color: #0078d7; font-size: 18px; font-weight: bold;")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)
        
        grid = QGridLayout()
        grid.setSpacing(8)
        keys = [('1', 0, 0), ('2', 0, 1), ('3', 0, 2), ('4', 1, 0), ('5', 1, 1), ('6', 1, 2), ('7', 2, 0), ('8', 2, 1), ('9', 2, 2), ('⌫', 3, 0), ('0', 3, 1), ('OK', 3, 2)]
        for text, r, c in keys:
            btn = QPushButton(text)
            btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            if text == 'OK':
                btn.setStyleSheet(config.BTN_STYLE_BLUE)
                btn.clicked.connect(self._keypad_ok)
            elif text == '⌫':
                btn.setStyleSheet(config.BTN_STYLE_RED)
                btn.clicked.connect(self._keypad_backspace)
            else:
                btn.setStyleSheet(config.MENU_CARD_STYLE + "font-size: 28px; border-radius: 10px; border: 2px solid #555;")
                btn.clicked.connect(lambda _, t=text: self._keypad_add(t))
            grid.addWidget(btn, r, c)
        layout.addLayout(grid)

    def _show_keypad(self):
        if self.is_running: return
        self.input_buffer = ""
        self.right_stack.setCurrentIndex(1)
        self.circular_progress.set_text("00:00", is_input=True)

    def _keypad_add(self, digit):
        if len(self.input_buffer) < 4:
            self.input_buffer += digit
            self._update_input_preview()

    def _keypad_backspace(self):
        self.input_buffer = self.input_buffer[:-1]
        self._update_input_preview()

    def _keypad_ok(self):
        padded = self.input_buffer.zfill(4)
        minutes = int(padded[0:2])
        seconds = int(padded[2:4])
        total = minutes * 60 + seconds
        self._set_time(total)
        self.right_stack.setCurrentIndex(0)

    def _update_input_preview(self):
        padded = self.input_buffer.zfill(4)
        formatted = f"{padded[0:2]}:{padded[2:4]}"
        self.circular_progress.set_text(formatted, is_input=True)

    def _update_clock(self):
        curr = QDateTime.currentDateTime()
        self.clock_time_label.setText(curr.toString("HH:mm"))
        pl_locale = QLocale(QLocale.Language.Polish)
        self.clock_date_label.setText(pl_locale.toString(curr, "dddd, d MMMM"))

    def _handle_back(self):
        if self.is_alarm_ringing:
            self._stop_alarm()
        self.go_back.emit()

    def _add_time(self, seconds):
        if not self.is_alarm_ringing:
            if self.seconds_left == 0:
                self.seconds_left = seconds
                self.total_seconds = seconds
            else:
                self.seconds_left += seconds
                if self.seconds_left > self.total_seconds:
                    self.total_seconds = self.seconds_left
            self._update_display()

    def _set_time(self, seconds):
        if self.is_running:
            self.timer.stop()
            self.is_running = False
            self.btn_start.setText("START")
            self.btn_start.setStyleSheet("background-color: #28a745; color: white; font-size: 20px; border-radius: 30px; font-weight: bold;")
        self.seconds_left = seconds
        self.total_seconds = seconds if seconds > 0 else 1
        self._update_display()

    def _toggle_timer_action(self):
        if self.is_alarm_ringing:
            self._stop_alarm()
            return
        if self.is_running:
            self.timer.stop()
            self.is_running = False
            self.btn_start.setText("RESUME")
            self.btn_start.setStyleSheet("background-color: #ffc107; color: black; font-size: 20px; border-radius: 30px; font-weight: bold;")
        else:
            if self.seconds_left > 0:
                self.timer.start(1000)
                self.is_running = True
                self.btn_start.setText("PAUSE")
                self.btn_start.setStyleSheet("background-color: #ffc107; color: black; font-size: 20px; border-radius: 30px; font-weight: bold;")

    def _tick(self):
        self.seconds_left -= 1
        if self.seconds_left <= 0:
            self._trigger_alarm()
        else:
            self._update_display()

    def _trigger_alarm(self):
        self.timer.stop()
        self.is_running = False
        self.seconds_left = 0
        self._update_display()
        self.is_alarm_ringing = True
        self.alarm_triggered.emit()
        self.circular_progress.set_text("TIME'S UP!", is_input=False)
        self.circular_progress.label.setStyleSheet("background: transparent; color: #ff4444; font-weight: bold; font-size: 40px;")
        
        self.btn_start.setText("STOP")
        self.btn_start.setStyleSheet(config.BTN_STYLE_RED)
        
        if os.path.exists(config.ALARM_SOUND_PATH):
            media = self.vlc_instance.media_new(config.ALARM_SOUND_PATH)
            media.add_option('input-repeat=999') 
            self.alarm_player.set_media(media)
            self.alarm_player.audio_set_volume(100)
            self.alarm_player.play()

    def _stop_alarm(self):
        if self.is_alarm_ringing:
            self.alarm_stopped.emit()
        self.is_alarm_ringing = False
        self.alarm_player.stop()
        self.btn_start.setText("START")
        self.btn_start.setStyleSheet("background-color: #28a745; color: white; font-size: 20px; border-radius: 30px; font-weight: bold;")
        self._update_display()

    def _reset_timer(self):
        self._stop_alarm()
        self._set_time(0)

    def _update_display(self):
        if self.right_stack.currentIndex() == 1: return
        minutes = self.seconds_left // 60
        seconds = self.seconds_left % 60
        time_str = f"{minutes:02}:{seconds:02}"
        self.circular_progress.set_text(time_str, is_input=False)
        self.circular_progress.set_values(self.seconds_left, self.total_seconds)
