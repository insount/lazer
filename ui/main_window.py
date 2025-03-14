from PyQt6.QtWidgets import (
    QMainWindow, QPushButton, QVBoxLayout, QWidget, QLabel, QHBoxLayout, QSpinBox
)
from controllers.laser_controller import LaserController
from controllers.motor_controller import MotorController
from ui.laser_view import LaserView

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Лазерный станок")
        self.setGeometry(100, 100, 600, 700)

        self.laser_view = LaserView()  # Создаём LaserView до MotorController
        self.laser = LaserController()
        self.motor = MotorController(self.laser_view)  # Передаём laser_view в MotorController

        self.init_ui()

    def init_ui(self):
        container = QWidget()
        layout = QVBoxLayout(container)
        self.setCentralWidget(container)

        # Панель текущих координат
        self.coord_label = QLabel("Координаты: (0, 0)")
        layout.addWidget(self.coord_label)

        # Поле ввода координат
        coord_layout = QHBoxLayout()
        self.x_input = QSpinBox()
        self.x_input.setRange(0, 500)
        self.y_input = QSpinBox()
        self.y_input.setRange(0, 500)
        coord_layout.addWidget(QLabel("X:"))
        coord_layout.addWidget(self.x_input)
        coord_layout.addWidget(QLabel("Y:"))
        coord_layout.addWidget(self.y_input)
        layout.addLayout(coord_layout)

        # Поле ввода скорости
        speed_layout = QHBoxLayout()
        self.speed_input = QSpinBox()
        self.speed_input.setRange(1, 10)
        self.speed_input.setValue(5)  # По умолчанию скорость 5
        speed_layout.addWidget(QLabel("Скорость:"))
        speed_layout.addWidget(self.speed_input)
        layout.addLayout(speed_layout)

        # Поле для отрисовки лазера с сеткой
        self.laser_view.setFixedSize(500, 500)
        self.laser_view.setStyleSheet("border: 4px solid black;")
        layout.addWidget(self.laser_view)

        # Кнопки управления
        self.laser_button = QPushButton("Включить лазер")
        self.laser_button.clicked.connect(self.toggle_laser)
        layout.addWidget(self.laser_button)

        self.move_button = QPushButton("Начать движение")
        self.move_button.clicked.connect(self.start_movement)
        layout.addWidget(self.move_button)

        self.stop_button = QPushButton("Остановить движение")
        self.stop_button.clicked.connect(self.stop_movement)
        layout.addWidget(self.stop_button)

        self.reset_button = QPushButton("Сброс")
        self.reset_button.clicked.connect(self.reset)
        layout.addWidget(self.reset_button)

        # Подключение сигнала об обновлении координат
        self.motor.position_changed.connect(self.update_coordinates)

    def update_coordinates(self, x, y):
        self.coord_label.setText(f"Координаты: ({x}, {y})")

    def start_movement(self):
        x_target = self.x_input.value()
        y_target = self.y_input.value()
        speed = self.speed_input.value()
        self.motor.set_speed(speed)

        # При начале движения устанавливаем флаг drawing в текущее состояние лазера
        self.motor.drawing = self.laser.laser_on
        self.motor.move_to(x_target, y_target)

    # В MainWindow.toggle_laser:
    def toggle_laser(self):
        if self.laser.laser_on:
            # ... лазер был ON, сейчас выключаем
            self.laser.turn_off()
            self.laser_button.setText("Включить лазер")
            self.motor.drawing = False
            # Добавляем маркер-разрыв, чтобы линии не соединялись
            self.laser_view.add_trail(None, None)
        else:
            # ... лазер был OFF, сейчас включаем
            self.laser.turn_on()
            self.laser_button.setText("Выключить лазер")
            self.motor.drawing = True
            # Аналогично можно добавить разрыв здесь, если хотим
            # чтобы новая линия не соединялась с точкой из предыдущего включения
            self.laser_view.add_trail(None, None)

    def stop_movement(self):
        self.motor.stop()

    def reset(self):
        self.motor.reset_position()  # вернёт мотор и LaserView к (0,0)
        self.laser_view.clear_trajectory()  # очистит линию
        self.coord_label.setText("Координаты: (0, 0)")

