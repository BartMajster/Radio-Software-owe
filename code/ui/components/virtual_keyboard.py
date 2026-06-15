from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, 
                             QPushButton, QLabel, QSizePolicy)
from PyQt6.QtCore import Qt
import config
class VirtualKeyboard(QDialog):
    def __init__(self, initial_text="", parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.showFullScreen()
        self.setStyleSheet(config.MAIN_STYLE)
        self.kb_buffer = initial_text
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        display_text = self.kb_buffer + "_" if self.kb_buffer else "_"
        self.kb_preview = QLabel(display_text)
        self.kb_preview.setStyleSheet("background-color: #111; color: #0078d7; font-size: 32px; font-weight: bold; padding: 5px; border-radius: 5px; border: 2px solid #555;")
        self.kb_preview.setFixedHeight(50) 
        layout.addWidget(self.kb_preview)
        kb_grid = QGridLayout()
        kb_grid.setSpacing(4) 
        for i in range(10): kb_grid.setColumnStretch(i, 1)
        for i in range(5): kb_grid.setRowStretch(i, 1) 
        keys = [
            ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0'],
            ['Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P'],
            ['A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L', '⌫'],
            ['Z', 'X', 'C', 'V', 'B', 'N', 'M', '-', '_', '.']
        ]
        for r, row in enumerate(keys):
            for c, char in enumerate(row):
                btn = QPushButton(char)
                btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Ignored)
                if char == '⌫':
                    btn.setStyleSheet(config.BTN_STYLE_RED + " min-height: 0px; font-size: 26px;")
                    btn.clicked.connect(self._kb_backspace)
                else:
                    btn.setStyleSheet(config.KB_BTN_STYLE + " min-height: 0px;")
                    btn.clicked.connect(lambda _, ch=char: self._kb_type(ch))
                kb_grid.addWidget(btn, r, c)
        btn_cancel = QPushButton("CANCEL")
        btn_cancel.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Ignored)
        btn_cancel.setStyleSheet(config.BTN_STYLE_GRAY + " min-height: 0px;")
        btn_cancel.clicked.connect(self.reject) 
        btn_space = QPushButton("SPACE")
        btn_space.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Ignored)
        btn_space.setStyleSheet(config.KB_BTN_STYLE + " min-height: 0px;")
        btn_space.clicked.connect(lambda: self._kb_type(" "))
        btn_ok = QPushButton("DONE")
        btn_ok.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Ignored)
        btn_ok.setStyleSheet(config.BTN_STYLE_BLUE + " min-height: 0px;")
        btn_ok.clicked.connect(self.accept) 
        kb_grid.addWidget(btn_cancel, 4, 0, 1, 2) 
        kb_grid.addWidget(btn_space, 4, 2, 1, 5) 
        kb_grid.addWidget(btn_ok, 4, 7, 1, 3) 
        layout.addLayout(kb_grid, stretch=1)
    def _kb_type(self, char):
        self.kb_buffer += char
        self.kb_preview.setText(self.kb_buffer + "_")
    def _kb_backspace(self):
        self.kb_buffer = self.kb_buffer[:-1]
        self.kb_preview.setText(self.kb_buffer + "_")
    def get_text(self):
        return self.kb_buffer.strip()