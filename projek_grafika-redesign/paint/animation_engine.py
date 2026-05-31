from PyQt5.QtCore import QObject, QTimer
import math


class AnimationEngine(QObject):

    BOUNCE = "bounce"
    SPIN = "spin"
    PULSE = "pulse"

    def __init__(self, canvas):
        super().__init__()

        self.canvas = canvas

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_animation)

        self.running = False

        self.animation_type = None

        self.frame = 0

        # Transform values
        self.offset_x = 0
        self.offset_y = 0

        self.scale = 1.0

        self.rotation = 0

    # ==========================
    # START
    # ==========================

    def start(self, animation_type):

        self.animation_type = animation_type

        self.frame = 0

        self.running = True

        self.timer.start(16)  # ~60 FPS

    # ==========================
    # STOP
    # ==========================

    def stop(self):

        self.timer.stop()

        self.running = False

        self.offset_x = 0
        self.offset_y = 0

        self.scale = 1.0

        self.rotation = 0

        self.canvas.update()

    # ==========================
    # UPDATE
    # ==========================

    def update_animation(self):

        self.frame += 1

        t = self.frame * 0.1

        if self.animation_type == self.BOUNCE:

            self.offset_y = math.sin(t) * 25

            self.rotation = 0
            self.scale = 1.0

        elif self.animation_type == self.SPIN:

            self.rotation += 5

            if self.rotation >= 360:
                self.rotation = 0

            self.offset_y = 0
            self.scale = 1.0

        elif self.animation_type == self.PULSE:

            self.scale = 1.0 + 0.25 * math.sin(t)

            self.offset_y = 0
            self.rotation = 0

        self.canvas.update()

    # ==========================
    # GETTERS
    # ==========================

    def get_offset(self):

        return (
            self.offset_x,
            self.offset_y
        )

    def get_scale(self):

        return self.scale

    def get_rotation(self):

        return self.rotation