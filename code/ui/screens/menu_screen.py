from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QLabel, 
                             QGraphicsOpacityEffect)
from PyQt6.QtCore import (Qt, pyqtSignal, QTimer, QDateTime, QEvent, 
                          QPropertyAnimation, QParallelAnimationGroup, 
                          QEasingCurve, QRect, QPoint, QLocale)
import config
class MenuScreen(QWidget):
    go_to_radio = pyqtSignal()
    go_to_timer = pyqtSignal()
    exit_app = pyqtSignal()
    def __init__(self):
        super().__init__()
        self.menu_items = [
            {"label": "📻\nRADIO", "action": self.go_to_radio, "style": ""},
            {"label": "⏲️\nTIMER", "action": self.go_to_timer, "style": ""},
            {"label": "❌\nEXIT", "action": self.exit_app, "style": "border-color: #cc0000; color: #ffcccc;"}
        ]
        self.current_index = 0
        self.is_animating = False
        self.drag_start_x = 0
        self.is_dragging = False
        self.clock_timer = QTimer()
        self.clock_timer.timeout.connect(self._update_clock)
        self._init_ui()
        self.clock_timer.start(1000)
        self._update_clock()
    def _init_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.header_widget = QWidget()
        self.header_widget.setStyleSheet("background-color: #222; border-bottom: 2px solid #444;")
        self.header_widget.setFixedHeight(100)
        header_layout = QVBoxLayout(self.header_widget)
        self.time_label = QLabel("--:--")
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.time_label.setStyleSheet("font-size: 40px; font-weight: bold; color: white;")
        header_layout.addWidget(self.time_label)
        self.date_label = QLabel("...")
        self.date_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.date_label.setStyleSheet("font-size: 16px; color: #bbb;")
        header_layout.addWidget(self.date_label)
        self.main_layout.addWidget(self.header_widget)
        self.carousel_container = QWidget()
        self.carousel_container.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.main_layout.addWidget(self.carousel_container)
        self.cards = []
        for i in range(5):
            btn = QPushButton(self.carousel_container)
            btn.show()
            btn.clicked.connect(self._handle_click)
            if i == 2:
                btn.installEventFilter(self)
            self.cards.append(btn)
        self._refresh_card_content()
    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._layout_cards_instantly()
    def _calculate_geometries(self):
        w = self.carousel_container.width()
        h = self.carousel_container.height()
        main_size = min(h - 20, int(w * 0.45))
        if main_size < 120: main_size = 120
        side_size = int(main_size * 0.7)
        center_y = (h - main_size) // 2
        side_y = (h - side_size) // 2
        center_x = (w - main_size) // 2
        spacing = 20
        rect_center = QRect(center_x, center_y, main_size, main_size)
        rect_left = QRect(center_x - side_size - spacing, side_y, side_size, side_size)
        rect_right = QRect(center_x + main_size + spacing, side_y, side_size, side_size)
        rect_far_left = QRect(-side_size - 50, side_y, side_size, side_size)
        rect_far_right = QRect(w + 50, side_y, side_size, side_size)
        return [rect_far_left, rect_left, rect_center, rect_right, rect_far_right]
    def _layout_cards_instantly(self):
        rects = self._calculate_geometries()
        for i, card in enumerate(self.cards):
            card.setGeometry(rects[i])
            self._apply_style_to_card(card, i)
    def _apply_style_to_card(self, card, pos_index):
        if pos_index == 2:
            base = config.MENU_CARD_STYLE
            card.setStyleSheet(base)
            card.raise_()
        else:
            card.setStyleSheet(config.SIDE_CARD_STYLE)
            card.lower()
    def _refresh_card_content(self):
        total = len(self.menu_items)
        offsets = [-2, -1, 0, 1, 2]
        for i, card in enumerate(self.cards):
            data_idx = (self.current_index + offsets[i]) % total
            item = self.menu_items[data_idx]
            card.setText(item["label"])
            if i == 2 and item["style"]:
                 card.setStyleSheet(config.MENU_CARD_STYLE + "QPushButton { " + item["style"] + " }")
            elif i == 2:
                 card.setStyleSheet(config.MENU_CARD_STYLE)
            else:
                 card.setStyleSheet(config.SIDE_CARD_STYLE)
    def _animate_move(self, direction):
        if self.is_animating: return
        self.is_animating = True
        rects = self._calculate_geometries()
        self.anim_group = QParallelAnimationGroup()
        if direction == "left":
            indices_to_animate = [(1,0), (2,1), (3,2), (4,3)]
            card_to_teleport = 0
            teleport_target = 4
            self.current_index = (self.current_index + 1) % len(self.menu_items)
        else:
            indices_to_animate = [(3,4), (2,3), (1,2), (0,1)]
            card_to_teleport = 4
            teleport_target = 0
            self.current_index = (self.current_index - 1) % len(self.menu_items)
        for curr_pos, target_pos in indices_to_animate:
            card = self.cards[curr_pos]
            anim = QPropertyAnimation(card, b"geometry")
            anim.setDuration(300)
            anim.setStartValue(rects[curr_pos])
            anim.setEndValue(rects[target_pos])
            anim.setEasingCurve(QEasingCurve.Type.OutQuad)
            self.anim_group.addAnimation(anim)
            if target_pos == 2:
                card.raise_()
        teleport_card = self.cards[card_to_teleport]
        teleport_card.setGeometry(rects[teleport_target])
        if direction == "left":
            first = self.cards.pop(0)
            self.cards.append(first)
        else:
            last = self.cards.pop()
            self.cards.insert(0, last)
        self.anim_group.finished.connect(self._on_animation_finished)
        self.anim_group.start()
    def _on_animation_finished(self):
        self.is_animating = False
        self._refresh_card_content()
        for i, card in enumerate(self.cards):
            if i == 2:
                card.installEventFilter(self)
            else:
                card.removeEventFilter(self)
    def eventFilter(self, source, event):
        if source == self.cards[2] and not self.is_animating:
            if event.type() == QEvent.Type.MouseButtonPress:
                self.drag_start_x = event.pos().x()
                self.is_dragging = True
            elif event.type() == QEvent.Type.MouseButtonRelease:
                if self.is_dragging:
                    delta = event.pos().x() - self.drag_start_x
                    self.is_dragging = False
                    if delta > 50:
                        self._animate_move("right")
                        return True
                    elif delta < -50:
                        self._animate_move("left")
                        return True
        return super().eventFilter(source, event)
    def _handle_click(self):
        if self.sender() == self.cards[2]:
            if not self.is_animating and not self.is_dragging:
                self.menu_items[self.current_index]["action"].emit()
    def _update_clock(self):
        curr = QDateTime.currentDateTime()
        self.time_label.setText(curr.toString("HH:mm"))
        pl_locale = QLocale(QLocale.Language.Polish)
        self.date_label.setText(pl_locale.toString(curr, "dddd, d MMMM"))