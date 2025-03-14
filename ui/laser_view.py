from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QPen, QColor
from PyQt6.QtCore import Qt

class LaserView(QWidget):
    def __init__(self):
        super().__init__()
        self.grid_size = 25  # Размер клетки
        self.margin = 4      # Отступ от границы
        self.laser_position = [self.margin, self.margin]  # Текущие координаты лазера
        self.trail = []      # История пройденных точек (для рисования линии)

    def update_position(self, x: int, y: int):
        """
        Обновляет координаты лазера и перерисовывает виджет.
        Вызывается MotorController при каждом шаге движения.
        """
        self.laser_position = [x, y]
        self.update()

    def add_trail(self, x: int, y: int):
        """
        Добавляет точку в список траектории (синяя линия),
        если лазер включён во время движения.
        """
        self.trail.append((x, y))
        self.update()

    def clear_trajectory(self):
        """
        Сбрасывает нарисованную траекторию.
        Обычно вызывается при сбросе настроек или при окончании проекта.
        """
        self.trail.clear()
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        field_width = self.width() - 2 * self.margin
        field_height = self.height() - 2 * self.margin

        # Чёрная рамка
        painter.setPen(QPen(Qt.GlobalColor.black, 4))
        painter.drawRect(self.margin, self.margin, field_width, field_height)

        # Сетка
        painter.setPen(QPen(Qt.GlobalColor.lightGray, 1))
        # Вертикальные линии
        for x in range(self.margin + self.grid_size, field_width + self.margin, self.grid_size):
            painter.drawLine(x, self.margin, x, field_height + self.margin)
        # Горизонтальные линии
        for y in range(self.margin + self.grid_size, field_height + self.margin, self.grid_size):
            painter.drawLine(self.margin, y, field_width + self.margin, y)

        # Траектория (синяя линия) с учётом "разрывов"
        if self.trail:
            painter.setPen(QPen(QColor(0, 0, 255), 2))  # Синяя линия
            for i in range(1, len(self.trail)):
                p1 = self.trail[i - 1]
                p2 = self.trail[i]

                # Проверяем, что точки не являются None и не содержат None
                if not p1 or not p2:
                    # Если p1 или p2 == None (или кортеж (None, None) не отлавливается напрямую),
                    # пропускаем отрисовку. Это разрыв.
                    continue

                # Проверка для случая (None, None):
                if p1[0] is None or p1[1] is None or p2[0] is None or p2[1] is None:
                    # Если элементы кортежа равны None — разрыв
                    continue

                # Иначе рисуем линию между p1 и p2
                painter.drawLine(*p1, *p2)

        # Лазерная точка (красная)
        painter.setPen(Qt.GlobalColor.red)
        painter.setBrush(Qt.GlobalColor.red)
        laser_x, laser_y = map(int, self.laser_position)
        painter.drawEllipse(laser_x - 3, laser_y - 3, 6, 6)
