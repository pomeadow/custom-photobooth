from PySide6.QtCore import QObject, QTimer, Signal
import cv2 as cv
import numpy as np


class CameraController(QObject):
    frame_ready = Signal(np.ndarray)
    camera_started = Signal()
    camera_stopped = Signal()
    camera_error = Signal(str)  # Emit error messages
    camera_ready = Signal()  # Emit when startup frames are skipped

    def __init__(self) -> None:
        super().__init__()
        self._camera = None
        self._timer = QTimer()
        self._fps = 30
        self._is_running = False
        self._frames_to_skip = 10  # Skip first N frames to hide startup logo
        self._frame_count = 0
        self._ready_emitted = False

    def start_camera(self, camera_index: int = 0):
        self._camera = cv.VideoCapture(camera_index)
        if self._is_running:
            return True

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
        # # Stop countdown timer if it exists
        # if hasattr(self, "countdown_timer"):
        #     self.countdown_timer.stop()
        # self.capture_button.setEnabled(False)

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
            # # Apply overlay if available
            # if self.overlay_image is not None:
            #     frame = apply_overlay(frame, self.overlay_image)

            # # Flip horizontally for mirror effect
            # frame = cv.flip(frame, 1)

            # # Convert to Qt format and display
            # rgb_image = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
            # h, w, ch = rgb_image.shape
            # bytes_per_line = ch * w
            # qt_image = QImage(
            #     rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888
            # )

            # # Scale to fit label while maintaining aspect ratio
            # pixmap = QPixmap.fromImage(qt_image)
            # scaled_pixmap = pixmap.scaled(
            #     self.camera_label.size(),
            #     Qt.KeepAspectRatio,
            #     Qt.SmoothTransformation,
            # )
            # self.camera_label.setPixmap(scaled_pixmap)

    def capture_photo(self):
        if not self._camera or not self._camera.isOpened():
            return None
        ret, frame = self._camera.read()
        if ret:
            return frame
        return None
        #     # Apply overlay if available
        #     if self.overlay_image is not None:
        #         frame = apply_overlay(frame, self.overlay_image)

        #     # Flip horizontally for mirror effect
        #     frame = cv.flip(frame, 1)

    def __del__(self):
        """Cleanup when controller is destroyed."""
        self.stop_camera()
