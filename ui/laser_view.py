from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QPen, QColor, QImage
from PyQt6.QtCore import Qt, pyqtSignal


class LaserView(QWidget):
    coordinate_clicked = pyqtSignal(int, int)

    def __init__(self):
        super().__init__()
        self.grid_size = 25  # Размер клетки
        self.margin = 4  # Отступ от границы
        self.laser_position = [self.margin, self.margin]  # Текущие координаты лазера

        # Традиционный "след" (синяя линия) если нужно
        self.trail = []

        # Новый слой для точек, загруженных из ImageLoader
        # Если он None, значит пока ничего не загружено
        self.points_image = None

        self.field_width = 500
        self.field_height = 500

        # Параметры зума
        self.zoom_enabled = False
        self.zoom_factor = 1.0
        self.zoom_center = None  # Центр, относительно которого происходит масштабирование

    # Методы для управления зумом
    def set_zoom_enabled(self, enabled: bool):
        self.zoom_enabled = enabled
        if not enabled:
            self.zoom_factor = 1.0
            self.zoom_center = None
        self.update()

    def zoom_in(self, step: float = 1.2):
        self.zoom_factor *= step
        self.update()

    def zoom_out(self, step: float = 1.2):
        self.zoom_factor = max(0.1, self.zoom_factor / step)
        self.update()

    # Остальные методы остаются без изменений
    def update_position(self, x: int, y: int):
        self.laser_position = [x, y]
        self.update()

    def add_trail(self, x: int, y: int):
        self.trail.append((x, y))
        self.update()

    def clear_trajectory(self):
        self.trail.clear()
        self.update()

    def set_laser_path(self, points):
        self.points_image = QImage(self.field_width, self.field_height, QImage.Format.Format_RGB32)
        self.points_image.fill(Qt.GlobalColor.white)
        for (px, py) in points:
            if 0 <= px < self.field_width and 0 <= py < self.field_height:
                self.points_image.setPixel(px, py, QColor(0, 0, 0).rgb())
        self.update()

    def clear_laser_path(self):
        self.points_image = None
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.save()

        # Применяем зум: если включён, масштабируем относительно zoom_center
        if self.zoom_enabled:
            if self.zoom_center is not None:
                cx, cy = self.zoom_center
                painter.translate(cx + self.margin, cy + self.margin)
                painter.scale(self.zoom_factor, self.zoom_factor)
                painter.translate(- (cx + self.margin), - (cy + self.margin))
            else:
                painter.scale(self.zoom_factor, self.zoom_factor)

        draw_width = self.width() - 2 * self.margin
        draw_height = self.height() - 2 * self.margin

        # Рисуем рамку
        painter.setPen(QPen(Qt.GlobalColor.black, 4))
        painter.drawRect(self.margin, self.margin, draw_width, draw_height)

        # Рисуем сетку
        painter.setPen(QPen(Qt.GlobalColor.lightGray, 1))
        for x in range(self.margin + self.grid_size, draw_width + self.margin, self.grid_size):
            painter.drawLine(x, self.margin, x, draw_height + self.margin)
        for y in range(self.margin + self.grid_size, draw_height + self.margin, self.grid_size):
            painter.drawLine(self.margin, y, draw_width + self.margin, y)

        # Рисуем слой точек, если он есть
        if self.points_image is not None:
            painter.drawImage(self.margin, self.margin, self.points_image)

        # Рисуем синий trail
        if self.trail:
            painter.setPen(QPen(QColor(0, 0, 255), 2))
            for i in range(1, len(self.trail)):
                p1 = self.trail[i - 1]
                p2 = self.trail[i]
                if not p1 or not p2:
                    continue
                if p1[0] is None or p1[1] is None or p2[0] is None or p2[1] is None:
                    continue
                painter.drawLine(p1[0], p1[1], p2[0], p2[1])

        # Рисуем лазер (красная точка)
        painter.setPen(Qt.GlobalColor.red)
        painter.setBrush(Qt.GlobalColor.red)
        lx, ly = map(int, self.laser_position)
        painter.drawEllipse(lx - 3, ly - 3, 6, 6)

        painter.restore()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            x_click = event.position().x()
            y_click = event.position().y()
            x_field = int(x_click - self.margin)
            y_field = int(y_click - self.margin)
            if 0 <= x_field < self.field_width and 0 <= y_field < self.field_height:
                self.coordinate_clicked.emit(x_field, y_field)
        elif event.button() == Qt.MouseButton.RightButton:
            # Если режим зума включён, устанавливаем центр зума в точке клика
            if self.zoom_enabled:
                x_click = event.position().x()
                y_click = event.position().y()
                x_field = int(x_click - self.margin)
                y_field = int(y_click - self.margin)
                if 0 <= x_field < self.field_width and 0 <= y_field < self.field_height:
                    self.zoom_center = (x_field, y_field)
                    self.zoom_in(step=1.2)
        super().mousePressEvent(event)
