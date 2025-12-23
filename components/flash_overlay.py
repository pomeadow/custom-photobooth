from PySide6.QtCore import QObject, QTimer, Qt, Signal
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QLabel


class FlashOverlay(QObject):
    flash_started = Signal()
    flash_finished = Signal()

    def __init__(self, camera_label: QLabel) -> None:
        super().__init__()
        self.camera_label = camera_label

    def flash(self):
        # Signal that flash is starting (to pause camera updates)
        self.flash_started.emit()

        # Capture current pixmap before flashing
        original_pixmap = self.camera_label.pixmap()

        # Create white pixmap and flash
        white_pixmap = QPixmap(self.camera_label.size())
        white_pixmap.fill(Qt.GlobalColor.white)
        self.camera_label.setPixmap(white_pixmap)

        # Restore original pixmap and signal completion after 400ms
        def restore():
            if original_pixmap:
                self.camera_label.setPixmap(original_pixmap)
            self.flash_finished.emit()

        QTimer.singleShot(300, restore)
