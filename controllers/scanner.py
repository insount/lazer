from PyQt6.QtGui import QImage
import numpy as np

class Scanner:
    def __init__(self, image_path):
        self.image = QImage(image_path)

    def analyze_image(self):
        width = self.image.width()
        height = self.image.height()
        points = []

        for y in range(height):
            for x in range(width):
                pixel = self.image.pixelColor(x, y).lightness()  # Яркость пикселя
                if pixel < 128:  # Если пиксель тёмный, записываем его координаты
                    points.append((x, y))

        return points  # Список точек для обработки
