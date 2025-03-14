from PyQt6.QtCore import QObject, pyqtSignal, QTimer

class MotorController(QObject):
    position_changed = pyqtSignal(int, int)

    def __init__(self, laser_view, field_size=(500, 500)):
        super().__init__()
        self.x = 0
        self.y = 0
        self.target_x = 0
        self.target_y = 0
        self.speed = 5
        self.drawing = False  # Если True, добавляем точки в trail (лазер «включён»)
        self.field_width, self.field_height = field_size
        self.moving = False

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_position)

        self.laser_view = laser_view

    def set_speed(self, speed: int):
        self.speed = max(1, min(10, speed))

    def move_to(self, x: int, y: int):
        self.target_x = max(0, min(self.field_width, x))
        self.target_y = max(0, min(self.field_height, y))
        self.moving = True
        self.timer.start(30)  # Запускаем таймер на 30 мс

    def update_position(self):
        if not self.moving:
            self.timer.stop()
            return

        dx = self.target_x - self.x
        dy = self.target_y - self.y
        dist = (dx**2 + dy**2) ** 0.5

        if dist < self.speed:
            self.x = self.target_x
            self.y = self.target_y
            self.moving = False
            self.timer.stop()
        else:
            step_x = self.speed * (dx / dist)
            step_y = self.speed * (dy / dist)
            self.x += step_x
            self.y += step_y

        # Сообщаем GUI о новых координатах
        self.position_changed.emit(int(self.x), int(self.y))
        # Обновляем положение красной точки в LaserView
        self.laser_view.update_position(int(self.x), int(self.y))

        # Если лазер включён, рисуем «след»
        if self.drawing:
            self.laser_view.add_trail(int(self.x), int(self.y))



    def stop(self):
        self.moving = False
        self.timer.stop()

    def reset_position(self):
        self.x, self.y = 0, 0
        self.target_x, self.target_y = 0, 0
        self.moving = False
        self.timer.stop()

        # Обновить виджет сразу на (0,0)
        self.laser_view.update_position(0, 0)

        # Также послать сигнал, чтобы обновить текст метки
        self.position_changed.emit(0, 0)
