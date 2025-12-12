from PySide6.QtCore import QObject, QTimer, Signal
import cv2 as cv
import numpy as np
import os
from dotenv import load_dotenv
from PIL import Image
import io

load_dotenv()

# Try to import gphoto2, but don't fail if not available
try:
    import gphoto2 as gp

    GPHOTO2_AVAILABLE = True
except ImportError:
    GPHOTO2_AVAILABLE = False
    print("Warning: gphoto2 not available. Install with: pip install gphoto2")


class CameraController(QObject):
    frame_ready = Signal(np.ndarray)
    camera_started = Signal()
    camera_stopped = Signal()
    camera_error = Signal(str)  # Emit error messages
    camera_ready = Signal()  # Emit when startup frames are skipped

    def __init__(self) -> None:
        super().__init__()
        self._camera = None
        self._gphoto_camera = None
        self._use_gphoto2 = False
        self._timer = QTimer()
        self._fps = 30
        self._is_running = False
        self._frames_to_skip = 90  # Skip first N frames to hide startup logo
        self._frame_count = 0
        self._ready_emitted = False

    def start_camera(self, camera_index: int = 0):
        self._camera = cv.VideoCapture(camera_index)
        if not self._camera.isOpened():
            self._camera = cv.VideoCapture(camera_index)

        if self._is_running:
            return True
        # Read from .env or use defaults
        camera_width = int(os.getenv("CAMERA_WIDTH", "1920"))
        camera_height = int(os.getenv("CAMERA_HEIGHT", "1080"))

        print(f"Requesting resolution: {camera_width}×{camera_height}")
        self._camera.set(cv.CAP_PROP_FRAME_WIDTH, camera_width)
        self._camera.set(cv.CAP_PROP_FRAME_HEIGHT, camera_height)

        # Also try setting FPS to a value the camera supports for 4K
        self._camera.set(cv.CAP_PROP_FPS, 30)

        # Verify what resolution was actually set
        actual_width = self._camera.get(cv.CAP_PROP_FRAME_WIDTH)
        actual_height = self._camera.get(cv.CAP_PROP_FRAME_HEIGHT)
        actual_fps = self._camera.get(cv.CAP_PROP_FPS)

        if actual_width != camera_width or actual_height != camera_height:
            print(f"⚠️  Camera doesn't support {camera_width}×{camera_height}")
            print(
                f"    Actual resolution: {int(actual_width)}×{int(actual_height)} @ {actual_fps:.1f}fps"
            )
            print(f"    This is a camera/driver limitation, not a software issue")
        else:
            print(
                f"✓ Preview resolution: {int(actual_width)}×{int(actual_height)} @ {actual_fps:.1f}fps"
            )

        # Reset frame counter for new camera session
        self._frame_count = 0
        self._ready_emitted = False

        self._timer.start(30)  # Update every 30ms
        self._timer.timeout.connect(self._update_frame)
        self._is_running = True
        if not self._camera.isOpened():
            self.camera_error.emit("Cannot open camera")
            return False

        self.camera_started.emit()
        return True

    def stop_camera(self):
        if not self._is_running:
            return
        self._timer.stop()
        if self._camera:
            self._camera.release()
            self._camera = None
        self._is_running = False
        self.camera_stopped.emit()

    def _update_frame(self):
        if not self._camera or not self._camera.isOpened():
            return
        ret, frame = self._camera.read()
        if ret:
            # Skip initial frames to hide camera startup logo
            if self._frame_count < self._frames_to_skip:
                self._frame_count += 1
                # Emit camera_ready signal once when ready
                if (
                    self._frame_count == self._frames_to_skip
                    and not self._ready_emitted
                ):
                    self._ready_emitted = True
                    self.camera_ready.emit()
                return

            self.frame_ready.emit(frame)
        else:
            self.camera_error.emit("Failed to read frame")

    def capture_photo(self):
        """
        Capture a photo.

        Returns:
            numpy.ndarray: Captured frame in BGR format, or None if capture failed
        """
        if not self._camera or not self._camera.isOpened():
            return None
        ret, frame = self._camera.read()
        if ret:
            print(f"Captured {frame.shape[1]}×{frame.shape[0]} image via OpenCV")
            return frame
        return None

    def __del__(self):
        """Cleanup when controller is destroyed."""
        self.stop_camera()
