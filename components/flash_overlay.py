from PySide6.QtCore import QEventLoop, QObject, QTimer, Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QLabel


class FlashOverlay(QObject):
    def __init__(self, camera_label: QLabel) -> None:
        super().__init__()
        # Store original image
        self.camera_label = camera_label
        self.original_pixmap = camera_label.pixmap()
        self.white_pixmap = QPixmap(camera_label.size())
        self.camera_label.setPixmap(self.white_pixmap)

    def flash(
        self,
    ):
        # Flash white
        self.white_pixmap.fill(Qt.white)

        # Use QTimer to restore after 200ms
        QTimer.singleShot(
            400,
            lambda: self.camera_label.setPixmap(self.original_pixmap)
            if self.original_pixmap
            else None,
        )
        loop = QEventLoop()
        QTimer.singleShot(400, loop.quit)
        loop.exec()
