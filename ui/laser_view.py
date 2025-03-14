from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QPen, QColor, QImage
from PyQt6.QtCore import Qt

class LaserView(QWidget):
    def __init__(self):
        super().__init__()
        self.grid_size = 25    # Размер клетки
        self.margin = 4        # Отступ от границы
        self.laser_position = [self.margin, self.margin]  # Текущие координаты лазера

        # Традиционный "след" (синяя линия) если нужно
        self.trail = []

        # Новый слой для точек, загруженных из ImageLoader
        # Если он None, значит пока ничего не загружено
        self.points_image = None

        # Предположим, поле 500x500 (как в MotorController)
        self.field_width = 500
        self.field_height = 500

        # Если у вас поле может меняться, можно сделать гибче,
        # или брать поле из config

    def update_position(self, x: int, y: int):
        """
        Обновляет координаты лазера и перерисовывает виджет.
        """
        self.laser_position = [x, y]
        self.update()

    def add_trail(self, x: int, y: int):
        """
        Добавляет точку в список "траектории" (синяя линия).
        По-прежнему можно использовать для движущегося лазера.
        """
        self.trail.append((x, y))
        self.update()

    def clear_trajectory(self):
        """
        Сбрасывает нарисованную траекторию.
        """
        self.trail.clear()
        self.update()

    def set_laser_path(self, points):
        """
        Вместо добавления 70k точек в trail (что может вызвать вылет),
        рисуем их сразу во "вторичное" QImage (self.points_image).

        points: список (x, y), где нужно поставить чёрный пиксель.
        """
        # Создаём QImage размером поля, заливаем белым
        self.points_image = QImage(self.field_width, self.field_height, QImage.Format.Format_RGB32)
        self.points_image.fill(Qt.GlobalColor.white)

        # Проставляем чёрные пиксели во всех нужных координатах
        for (px, py) in points:
            # Убедимся, что точки в пределах поля
            if 0 <= px < self.field_width and 0 <= py < self.field_height:
                self.points_image.setPixel(px, py, QColor(0, 0, 0).rgb())

        # Вызовем update(), чтобы виджет перерисовался
        self.update()

    def clear_laser_path(self):
        """
        Очищает "слой" с пикселями, загруженными из изображения
        (если нужно сбросить).
        """
        self.points_image = None
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Рассчитываем реальные размеры поля, учитывая margin
        draw_width = self.width() - 2 * self.margin
        draw_height = self.height() - 2 * self.margin

        # Чёрная рамка
        painter.setPen(QPen(Qt.GlobalColor.black, 4))
        painter.drawRect(self.margin, self.margin, draw_width, draw_height)

        # Сетка (рисуем поверх рамки, но подо всем остальным)
        painter.setPen(QPen(Qt.GlobalColor.lightGray, 1))
        # Вертикальные линии
        for x in range(self.margin + self.grid_size, draw_width + self.margin, self.grid_size):
            painter.drawLine(x, self.margin, x, draw_height + self.margin)
        # Горизонтальные линии
        for y in range(self.margin + self.grid_size, draw_height + self.margin, self.grid_size):
            painter.drawLine(self.margin, y, draw_width + self.margin, y)

        # Рисуем, если есть загруженный слой точек
        if self.points_image is not None:
            # Если размер points_image == (500x500), а draw_width, draw_height тоже (500x500),
            # мы просто рисуем image внутри поля.
            # Если у вас другое поле, нужно масштабировать:
            # scaled = self.points_image.scaled(draw_width, draw_height)
            # painter.drawImage(self.margin, self.margin, scaled)
            # Но если всё 500x500 совпадает, то не нужно
            painter.drawImage(self.margin, self.margin, self.points_image)

        # Рисуем синий trail (если используется для "живого" перемещения)
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

        # Красная точка (лазер)
        painter.setPen(Qt.GlobalColor.red)
        painter.setBrush(Qt.GlobalColor.red)
        lx, ly = map(int, self.laser_position)
        painter.drawEllipse(lx - 3, ly - 3, 6, 6)
