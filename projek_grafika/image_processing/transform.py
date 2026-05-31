import cv2
import numpy as np


def apply_transform(frame, method, color_choice=None, param=None):

    img = frame.copy()

    beta = int(param) if param is not None else 40
    alpha = (param / 100.0) if param is not None else 1.5
    k = int(param) if param is not None else 7
    prob = (param / 1000.0) if param is not None else 0.02
    angle = int(param) if param is not None else 45
    shift = int(param) if param is not None else 30

    # =====================================
    # NEGATIVE
    # =====================================

    if method == "Negative":

        img = cv2.bitwise_not(frame)

    # =====================================
    # BRIGHTNESS
    # =====================================

    elif method == "Brightness":

        img = cv2.convertScaleAbs(
            frame,
            alpha=1,
            beta=beta
        )

    # =====================================
    # CONTRAST
    # =====================================

    elif method == "Contrast":

        img = cv2.convertScaleAbs(
            frame,
            alpha=alpha,
            beta=0
        )

    # =====================================
    # LOG TRANSFORM
    # =====================================

    elif method == "Log Transform":

        c = 255 / np.log(1 + np.max(frame))

        img = np.uint8(
            c * np.log(
                1 + frame.astype(np.float32)
            )
        )

    # =====================================
    # COLOR FILTERING
    # =====================================

    elif method == "Color Filtering":

        img = np.zeros_like(frame)

        if color_choice == "Red":

            img[:, :, 2] = frame[:, :, 2]

        elif color_choice == "Green":

            img[:, :, 1] = frame[:, :, 1]

        elif color_choice == "Blue":

            img[:, :, 0] = frame[:, :, 0]

    # =====================================
    # GAUSSIAN BLUR
    # =====================================

    elif method == "Gaussian Blur":

        if k % 2 == 0:
            k += 1

        img = cv2.GaussianBlur(
            frame,
            (k, k),
            0
        )

    # =====================================
    # SALT & PEPPER
    # =====================================

    elif method == "Salt & Pepper":

        h, w = frame.shape[:2]

        num = int(prob * h * w)

        coords_salt = (
            np.random.randint(0, h, num),
            np.random.randint(0, w, num)
        )

        img[coords_salt] = [255, 255, 255]

        coords_pepper = (
            np.random.randint(0, h, num),
            np.random.randint(0, w, num)
        )

        img[coords_pepper] = [0, 0, 0]

    # =====================================
    # GRAYSCALE
    # =====================================

    elif method == "Grayscale":

        img = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2GRAY
        )

        img = cv2.cvtColor(
            img,
            cv2.COLOR_GRAY2BGR
        )

    # =====================================
    # HISTOGRAM EQUALIZATION
    # =====================================

    elif method == "Equalization":

        ycrcb = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2YCrCb
        )

        y, cr, cb = cv2.split(ycrcb)

        y_eq = cv2.equalizeHist(y)

        ycrcb_eq = cv2.merge(
            (y_eq, cr, cb)
        )

        img = cv2.cvtColor(
            ycrcb_eq,
            cv2.COLOR_YCrCb2BGR
        )

    # =====================================
    # EDGE DETECTION
    # =====================================

    elif method == "Edge Detection":

        gray = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2GRAY
        )

        edges = cv2.Canny(
            gray,
            50,
            150
        )

        img = cv2.cvtColor(
            edges,
            cv2.COLOR_GRAY2BGR
        )

    # =====================================
    # MIRRORING
    # =====================================

    elif method == "Mirroring":

        img = cv2.flip(
            frame,
            1
        )

    # =====================================
    # ROTATE
    # =====================================

    elif method == "Rotate":

        h, w = frame.shape[:2]

        center = (
            w // 2,
            h // 2
        )

        M = cv2.getRotationMatrix2D(
            center,
            angle,
            1.0
        )

        img = cv2.warpAffine(
            frame,
            M,
            (w, h)
        )

    # =====================================
    # TRANSLATE
    # =====================================

    elif method == "Translate":

        M = np.float32([
            [1, 0, shift],
            [0, 1, shift]
        ])

        img = cv2.warpAffine(
            frame,
            M,
            (
                frame.shape[1],
                frame.shape[0]
            )
        )

    return img