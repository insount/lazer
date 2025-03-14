from PyQt6.QtCore import QObject, pyqtSignal

class LaserController(QObject):
    state_changed = pyqtSignal(bool)  # Сигнал для GUI (True - включён, False - выключен)

    def __init__(self):
        super().__init__()
        self.laser_on = False

    def turn_on(self):
        self.laser_on = True
        self.state_changed.emit(True)

    def turn_off(self):
        self.laser_on = False
        self.state_changed.emit(False)
