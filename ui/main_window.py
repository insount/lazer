from PyQt6.QtWidgets import (
    QMainWindow, QPushButton, QVBoxLayout, QWidget, QLabel, QHBoxLayout, QSpinBox, QFileDialog, QDialog
)
from PyQt6.QtCore import Qt, QTimer
from controllers.laser_controller import LaserController
from controllers.motor_controller import MotorController
from ui.laser_view import LaserView
from ui.image_loader import ImageLoader
import cv2

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Лазерный станок")
        self.setGeometry(100, 100, 600, 700)

        # Создаём контроллеры и виджеты
        self.laser = LaserController()
        self.laser_view = LaserView()             # Виджет отрисовки
        self.motor = MotorController(self.laser_view)
        self.image_loader = ImageLoader()

        # Поля для анимации лазера (прожиг) в диалоговом окне
        self.current_index = 0
        self.laser_timer = None
        self.dialog_window = None
        self.original_label = None
        self.binary_label = None
        self.laser_label = None

        self.init_ui()

        # Подключаем сигнал клика по полю из LaserView
        self.laser_view.coordinate_clicked.connect(self.handle_field_click)

    def init_ui(self):
        container = QWidget()
        layout = QVBoxLayout(container)
        self.setCentralWidget(container)

        # Панель координат
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
        self.speed_input.setValue(5)
        speed_layout.addWidget(QLabel("Скорость:"))
        speed_layout.addWidget(self.speed_input)
        layout.addLayout(speed_layout)

        # Виджет для «поля» лазера
        self.laser_view.setFixedSize(500, 500)
        self.laser_view.setStyleSheet("border: 4px solid black;")
        layout.addWidget(self.laser_view)

        # Кнопка загрузки изображения
        self.load_image_button = QPushButton("Загрузить и анализировать изображение")
        self.load_image_button.clicked.connect(self.load_and_process_image)
        layout.addWidget(self.load_image_button)

        # Кнопка включения/выключения лазера
        self.laser_button = QPushButton("Включить лазер")
        self.laser_button.clicked.connect(self.toggle_laser)
        layout.addWidget(self.laser_button)

        # Кнопка начала движения
        self.move_button = QPushButton("Начать движение")
        self.move_button.clicked.connect(self.start_movement)
        layout.addWidget(self.move_button)

        # Кнопка остановки движения
        self.stop_button = QPushButton("Остановить движение")
        self.stop_button.clicked.connect(self.stop_movement)
        layout.addWidget(self.stop_button)

        # Кнопка сброса
        self.reset_button = QPushButton("Сброс")
        self.reset_button.clicked.connect(self.reset)
        layout.addWidget(self.reset_button)

        # При каждом обновлении координат обновляем label
        self.motor.position_changed.connect(self.update_coordinates)

    def handle_field_click(self, x, y):
        """
        Обрабатывает клик по полю (LaserView) и запускает движение лазера к этой точке.
        """
        print(f"[DEBUG] Клик по полю: ({x}, {y})")
        # Обновляем поля ввода координат, если это нужно
        self.x_input.setValue(x)
        self.y_input.setValue(y)
        # Запускаем движение лазера к этим координатам
        speed = self.speed_input.value()
        self.motor.set_speed(speed)
        self.motor.drawing = self.laser.laser_on
        self.motor.move_to(x, y)

    def load_and_process_image(self):
        """
        Загружает изображение через ImageLoader, анализирует его, создаёт laser_simulation,
        и открывает диалог с анимацией прожига (не затрагивая главное поле LaserView).
        """
        file_path = self.image_loader.load_image()
        if not file_path:
            return

        points = self.image_loader.process_image()
        if not points:
            print("⚠️ Нет активных точек в изображении.")
            return

        print(f"✅ Обнаружено {len(points)} точек для обработки.")

        # Создаём белое изображение для симуляции
        self.image_loader.create_laser_simulation()

        # НЕ вызываем self.laser_view.set_laser_path(points),
        # чтобы не отображать это изображение в главном поле.
        # self.laser_view.set_laser_path(points)  # <-- закомментировано!

        # Открываем диалог с тремя изображениями (оригинал, бинарка, laser_simulation)
        self.show_images_dialog()

    def show_images_dialog(self):
        """
        Создаёт диалоговое окно с тремя QLabel:
        1) Оригинал
        2) Бинарка
        3) Лазерная симуляция (будем анимировать)
        """
        self.dialog_window = QDialog(self)
        self.dialog_window.setWindowTitle("Просмотр изображений")
        self.dialog_window.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)

        main_layout = QVBoxLayout(self.dialog_window)

        # Три QLabel
        self.original_label = QLabel()
        self.binary_label = QLabel()
        self.laser_label = QLabel()

        images_layout = QHBoxLayout()
        images_layout.addWidget(self.original_label)
        images_layout.addWidget(self.binary_label)
        images_layout.addWidget(self.laser_label)

        main_layout.addLayout(images_layout)
        self.dialog_window.setLayout(main_layout)

        # Обновляем содержимое каждого QLabel
        self.update_image_label(self.original_label, self.image_loader.original_image)
        self.update_image_label(self.binary_label, self.image_loader.binary_image)
        self.update_image_label(self.laser_label, self.image_loader.laser_simulation)

        self.dialog_window.adjustSize()
        self.dialog_window.setFixedSize(min(self.dialog_window.width(), 900),
                                        min(self.dialog_window.height(), 500))

        # Запускаем анимацию лазера (прожига) прямо сейчас
        self.start_laser_animation()

        self.dialog_window.exec()

    def start_laser_animation(self):
        """
        Создаём таймер, который будет «прожигать» пиксели в self.image_loader.laser_simulation,
        показывая результат в self.laser_label.
        """
        if not self.image_loader.points or self.image_loader.laser_simulation is None:
            print("⚠️ Нечего анимировать.")
            return

        self.current_index = 0
        self.laser_timer = QTimer(self)
        self.laser_timer.timeout.connect(self.animate_laser)

        # Установим общее время анимации, например, 5 секунд
        total_points = len(self.image_loader.points)
        duration_ms = 5000
        step_time = max(duration_ms // total_points, 10)
        print(f"⏳ Интервал таймера: {step_time} мс")

        self.laser_timer.start(step_time)

    def animate_laser(self):
        """
        За один «тик» закрашиваем часть точек в laser_simulation чёрным цветом
        и обновляем laser_label.
        """
        points = self.image_loader.points
        laser_sim = self.image_loader.laser_simulation

        if self.current_index >= len(points):
            self.laser_timer.stop()
            print("✅ Анимация завершена")
            return

        step_size = 50  # кол-во пикселей, которые «прожигаем» за один тик
        end_index = min(self.current_index + step_size, len(points))

        for i in range(self.current_index, end_index):
            x, y = points[i]
            laser_sim[y, x] = [0, 0, 0]  # чёрный пиксель

        self.current_index = end_index

        # Обновляем laser_label
        self.update_image_label(self.laser_label, laser_sim)
        self.dialog_window.repaint()

        if self.current_index >= len(points):
            self.laser_timer.stop()

    def update_image_label(self, label: QLabel, img):
        """
        Обновляет QLabel с изображением (numpy-массив).
        """
        if img is None or img.size == 0:
            label.setText("Нет данных")
            return

        height, width = img.shape[:2]
        max_height = 300
        if height > max_height:
            scale_factor = max_height / height
            new_width = int(width * scale_factor)
            new_height = max_height
            img = cv2.resize(img, (new_width, new_height), interpolation=cv2.INTER_AREA)
        else:
            new_height, new_width = height, width

        # Определяем, цветное или нет
        if len(img.shape) == 2:
            # Grayscale
            from PyQt6.QtGui import QImage, QPixmap
            format_type = QImage.Format.Format_Grayscale8
            bytes_per_line = new_width
        else:
            # BGR -> RGB
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            from PyQt6.QtGui import QImage, QPixmap
            format_type = QImage.Format.Format_RGB888
            bytes_per_line = new_width * 3

        qimage = QImage(img.data, new_width, new_height, bytes_per_line, format_type)
        pixmap = QPixmap.fromImage(qimage)
        label.setPixmap(pixmap)
        label.setFixedSize(new_width, new_height)

    # ======= Методы для лазера/движения ======= #

    def update_coordinates(self, x, y):
        self.coord_label.setText(f"Координаты: ({x}, {y})")

    def start_movement(self):
        x_target = self.x_input.value()
        y_target = self.y_input.value()
        speed = self.speed_input.value()
        self.motor.set_speed(speed)
        self.motor.drawing = self.laser.laser_on
        self.motor.move_to(x_target, y_target)

    def toggle_laser(self):
        if self.laser.laser_on:
            self.laser.turn_off()
            self.laser_button.setText("Включить лазер")
            self.motor.drawing = False
            self.laser_view.add_trail(None, None)  # разрыв
        else:
            self.laser.turn_on()
            self.laser_button.setText("Выключить лазер")
            self.motor.drawing = True
            self.laser_view.add_trail(None, None)  # разрыв

    def stop_movement(self):
        self.motor.stop()

    def reset(self):
        self.motor.reset_position()
        self.laser_view.clear_trajectory()
        self.coord_label.setText("Координаты: (0, 0)")
