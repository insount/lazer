import cv2
import numpy as np
from PyQt6.QtWidgets import QFileDialog, QMessageBox, QDialog, QLabel, QHBoxLayout, QVBoxLayout
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtCore import Qt, QTimer


class ImageLoader:
    def __init__(self):
        self.original_image = None
        self.binary_image = None
        self.laser_simulation = None
        self.points = []
        self.dialog = None
        self.laser_timer = None
        self.current_index = 0  # Индекс для анимации

    def load_image(self):
        """Открывает диалог выбора файла и загружает изображение"""
        file_path, _ = QFileDialog.getOpenFileName(None, "Выберите изображение", "", "Images (*.bmp *.png *.jpg)")
        if not file_path:
            return None

        self.original_image = cv2.imread(file_path)
        self.binary_image = cv2.imread(file_path, cv2.IMREAD_GRAYSCALE)

        if self.binary_image is None:
            QMessageBox.warning(None, "Ошибка", "Не удалось загрузить изображение")
            return None

        return file_path

    def process_image(self):
        """Обрабатывает изображение, выделяет активные пиксели"""
        if self.binary_image is None:
            return None

        _, self.binary_image = cv2.threshold(self.binary_image, 127, 255, cv2.THRESH_BINARY)

        self.points = []
        height, width = self.binary_image.shape

        for y in range(height):
            for x in range(width):
                if self.binary_image[y, x] == 0:
                    self.points.append((x, y))

        print(f"🔹 Найдено {len(self.points)} точек для лазера")  # ✅ Отладка

        return self.points

    def create_laser_simulation(self):
        """Создаёт пустое белое изображение"""
        if self.binary_image is None:
            return None

        height, width = self.binary_image.shape
        self.laser_simulation = np.full((height, width, 3), 255, dtype=np.uint8)  # ✅ Белый фон (RGB)

    def show_images(self):
        """Открывает окно с изображениями и запускает анимацию лазера"""
        self.dialog = QDialog()
        self.dialog.setWindowTitle("Просмотр изображений")
        self.dialog.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)

        layout = QVBoxLayout(self.dialog)

        self.original_label = QLabel()
        self.binary_label = QLabel()
        self.laser_label = QLabel()

        layout_images = QHBoxLayout()
        layout_images.addWidget(self.original_label)
        layout_images.addWidget(self.binary_label)
        layout_images.addWidget(self.laser_label)

        layout.addLayout(layout_images)
        self.dialog.setLayout(layout)

        # ✅ Создаём симуляцию перед обновлением изображений
        if self.laser_simulation is None:
            self.create_laser_simulation()

        self.update_image(self.original_label, self.original_image, max_height=300)
        self.update_image(self.binary_label, self.binary_image, max_height=300)
        self.update_image(self.laser_label, self.laser_simulation, max_height=300)

        self.dialog.adjustSize()
        self.dialog.setFixedSize(min(self.dialog.width(), 900), min(self.dialog.height(), 500))

        self.start_laser_animation()  # ✅ Запускаем анимацию
        self.dialog.exec()

    def start_laser_animation(self):
        """Запускает анимацию движения лазера"""
        if not self.points:
            print("⚠️ Ошибка: список точек пуст. Лазер не будет анимирован!")
            return

        self.current_index = 0
        self.laser_timer = QTimer()
        self.laser_timer.timeout.connect(self.animate_laser)

        # ✅ Длительность анимации 5 секунд
        duration_ms = 5000
        step_time = max(duration_ms // len(self.points), 10)  # Минимальный шаг 10 мс
        print(f"⏳ Интервал таймера: {step_time} мс")  # ✅ Отладка

        self.laser_timer.setInterval(step_time)
        self.laser_timer.start()

    def animate_laser(self):
        """Анимирует движение лазера, оставляя только чёрный 🔲 след без красной точки"""
        if self.current_index >= len(self.points):
            self.laser_timer.stop()
            print("✅ Анимация завершена")
            return

        step_size = 100  # ✅ Лазер проходит сразу 50 точек за шаг (ускоряем)

        end_index = min(self.current_index + step_size, len(self.points))

        # ✅ Оставляем только чёрный след
        for i in range(self.current_index, end_index):
            x, y = self.points[i]
            self.laser_simulation[y, x] = [0, 0, 0]  # ⚫ Чёрный след

        # ✅ Обновляем QLabel
        self.update_image(self.laser_label, self.laser_simulation, max_height=300)
        self.dialog.repaint()

        self.current_index += step_size

        if self.current_index >= len(self.points):
            self.laser_timer.stop()


    def update_image(self, label, img, max_height=300):
        """Обновляет QLabel с изображением, уменьшая его, но сохраняя пропорции"""
        if img is None or img.size == 0:
            label.setText("Нет данных")  # ✅ Заглушка вместо пустого места
            return

        height, width = img.shape[:2]

        # ✅ Уменьшаем размер изображения, сохраняя пропорции
        if height > max_height:
            scale_factor = max_height / height
            new_width = int(width * scale_factor)
            new_height = max_height
            img = cv2.resize(img, (new_width, new_height), interpolation=cv2.INTER_AREA)

        try:
            bytes_per_line = new_width * 3 if len(img.shape) == 3 else new_width
            format_type = QImage.Format.Format_RGB888 if len(img.shape) == 3 else QImage.Format.Format_Grayscale8
            qimage = QImage(img.data, new_width, new_height, bytes_per_line, format_type)
            pixmap = QPixmap.fromImage(qimage)

            label.setPixmap(pixmap)
            label.setFixedSize(new_width, new_height)
        except Exception as e:
            print(f"Ошибка при обработке изображения: {e}")

