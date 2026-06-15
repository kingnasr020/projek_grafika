from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt
from collections import deque
import struct


class FloodFill:
    """
    Flood Fill dengan Scanline algorithm + akses buffer langsung.

    Kenapa jauh lebih cepat dari BFS pixel-per-pixel:
    - Buffer raw bytes dibaca sekali (bits()), bukan pixelColor() per pixel
    - Scanline memproses satu baris penuh sekaligus → queue entry jauh lebih sedikit
    - Setiap baris hanya di-enqueue sekali (cek atas/bawah langsung di loop)
    """

    def __init__(self, canvas_ref):
        self.ref = canvas_ref

    # ------------------------------------------------------------------
    # PUBLIC
    # ------------------------------------------------------------------

    def flood_fill(self, x, y):
        image = self.ref.canvas.toImage().convertToFormat(QImage.Format_ARGB32)

        w = image.width()
        h = image.height()

        # Baca seluruh buffer sekaligus sebagai array integer 32-bit
        ptr    = image.bits()
        ptr.setsize(w * h * 4)
        buf    = bytearray(ptr)

        target_color = self._pixel_at(buf, w, x, y)
        fill_color   = self._qcolor_to_int(self.ref.pen_color)

        if target_color == fill_color:
            return

        # --- Scanline flood fill ---
        queue = deque()
        queue.append((x, y))

        while queue:
            cx, cy = queue.popleft()

            # Cari batas kiri segmen ini
            lx = cx
            while lx > 0 and self._pixel_at(buf, w, lx - 1, cy) == target_color:
                lx -= 1

            # Scan ke kanan, isi baris, periksa baris atas/bawah
            span_above = False
            span_below = False

            rx = lx
            while rx < w and self._pixel_at(buf, w, rx, cy) == target_color:
                self._set_pixel(buf, w, rx, cy, fill_color)

                # Cek baris atas
                if cy > 0:
                    above = self._pixel_at(buf, w, rx, cy - 1)
                    if above == target_color and not span_above:
                        queue.append((rx, cy - 1))
                        span_above = True
                    elif above != target_color:
                        span_above = False

                # Cek baris bawah
                if cy < h - 1:
                    below = self._pixel_at(buf, w, rx, cy + 1)
                    if below == target_color and not span_below:
                        queue.append((rx, cy + 1))
                        span_below = True
                    elif below != target_color:
                        span_below = False

                rx += 1

        # Tulis buffer kembali ke image lalu ke canvas
        new_image = QImage(bytes(buf), w, h, QImage.Format_ARGB32)
        self.ref.canvas = QPixmap.fromImage(new_image)

    # ------------------------------------------------------------------
    # HELPERS
    # ------------------------------------------------------------------

    @staticmethod
    def _pixel_at(buf, w, x, y):
        idx = (y * w + x) * 4
        return struct.unpack_from('<I', buf, idx)[0]

    @staticmethod
    def _set_pixel(buf, w, x, y, color):
        idx = (y * w + x) * 4
        struct.pack_into('<I', buf, idx, color)

    @staticmethod
    def _qcolor_to_int(qcolor):
        # ARGB32 little-endian: byte order = B G R A
        return struct.unpack('<I', bytes([
            qcolor.blue(),
            qcolor.green(),
            qcolor.red(),
            qcolor.alpha(),
        ]))[0]