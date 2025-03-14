import cv2
import numpy as np
from PyQt6.QtWidgets import QFileDialog, QMessageBox
from PyQt6.QtCore import Qt


class ImageLoader:
    def __init__(self):
        self.original_image = None
        self.binary_image = None
        self.laser_simulation = None
        self.points = []

    def load_image(self):
        """Открывает диалог выбора файла и загружает изображение"""
        file_path, _ = QFileDialog.getOpenFileName(
            None,
            "Выберите изображение",
            "",
            "Images (*.bmp *.png *.jpg)"
        )
        if not file_path:
            return None

        self.original_image = cv2.imread(file_path)
        self.binary_image = cv2.imread(file_path, cv2.IMREAD_GRAYSCALE)

        if self.binary_image is None:
            QMessageBox.warning(None, "Ошибка", "Не удалось загрузить изображение")
            return None

        return file_path

    def process_image(self):
        """Бинаризует изображение и собирает точки, где пиксель чёрный (0)."""
        if self.binary_image is None:
            return None

        _, self.binary_image = cv2.threshold(
            self.binary_image, 127, 255, cv2.THRESH_BINARY
        )

        self.points = []
        height, width = self.binary_image.shape

        for y in range(height):
            for x in range(width):
                # Если пиксель чёрный
                if self.binary_image[y, x] == 0:
                    self.points.append((x, y))

        print(f"🔹 Найдено {len(self.points)} точек для лазера")
        return self.points

    def create_laser_simulation(self):
        """
        Создаёт белое цветное изображение (h×w×3)
        для дальнейшего «прожига» пикселей.
        """
        if self.binary_image is None:
            return None

        height, width = self.binary_image.shape
        self.laser_simulation = np.full((height, width, 3), 255, dtype=np.uint8)
        return self.laser_simulation
