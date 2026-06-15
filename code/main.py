import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QStackedWidget
from PyQt6.QtCore import Qt
import config
from ui.screens.menu_screen import MenuScreen
from ui.screens.radio_screen import RadioScreen
from ui.screens.timer_screen import TimerScreen
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(config.APP_TITLE)
        self.resize(*config.WINDOW_SIZE)
        self.setStyleSheet(config.MAIN_STYLE)
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)
        self.menu_screen = MenuScreen()
        self.radio_screen = RadioScreen()
        self.timer_screen = TimerScreen()
        self.stack.addWidget(self.menu_screen)
        self.stack.addWidget(self.radio_screen)
        self.stack.addWidget(self.timer_screen)
        self.menu_screen.go_to_radio.connect(lambda: self.stack.setCurrentWidget(self.radio_screen))
        self.menu_screen.go_to_timer.connect(lambda: self.stack.setCurrentWidget(self.timer_screen))
        self.menu_screen.exit_app.connect(self.close)
        self.radio_screen.go_back.connect(lambda: self.stack.setCurrentWidget(self.menu_screen))
        self.timer_screen.go_back.connect(lambda: self.stack.setCurrentWidget(self.menu_screen))
        self.timer_screen.alarm_triggered.connect(self.radio_screen.mute_radio_for_alarm)
        self.timer_screen.alarm_stopped.connect(self.radio_screen.unmute_radio_after_alarm)
        self.stack.setCurrentWidget(self.menu_screen)
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.showFullScreen()
    window.setCursor(Qt.CursorShape.BlankCursor)
    sys.exit(app.exec())