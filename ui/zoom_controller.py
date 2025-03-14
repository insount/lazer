class ZoomController:
    """
    Класс, управляющий "зумом" (масштабированием) поля.
    """
    def __init__(self, laser_view):
        self.laser_view = laser_view  # ссылка на LaserView
        self.zoom_enabled = False     # включён ли режим "лупы"
        self.zoom_factor = 1.0        # текущий коэффициент увеличения

    def set_enabled(self, enable: bool):
        """Включает/выключает режим увеличения."""
        self.zoom_enabled = enable
        # Если при каждом включении хотим сбрасывать на 1.0:
        # if enable:
        #     self.zoom_factor = 1.0
        self.laser_view.update()

    def is_enabled(self) -> bool:
        return self.zoom_enabled

    def zoom_in(self, step: float = 1.2):
        """Увеличивает zoom_factor и просит LaserView перерисоваться."""
        self.zoom_factor *= step
        self.laser_view.update()

    def zoom_out(self, step: float = 1.2):
        """Уменьшает zoom_factor, но не даём упасть ниже 0.1, чтобы не схлопнулось."""
        self.zoom_factor = max(self.zoom_factor / step, 0.1)
        self.laser_view.update()

    def get_zoom_factor(self) -> float:
        return self.zoom_factor
