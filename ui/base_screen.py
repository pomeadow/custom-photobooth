import os
from PySide6.QtCore import Signal
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QLabel, QWidget


class BaseScreen(QWidget):
    navigate_to = Signal(str)  # Emit screen name to navigate to

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background-color: #ffffff;")
        self._setup_background()

    def _setup_background(self):
        """Setup background image for all screens."""
        abs_path = os.path.abspath("./resources/UI Asset/UI Background (Solid Colour)-01.png")
        pixmap = QPixmap(abs_path)

        self.background_label = QLabel(self)
        if not pixmap.isNull():
            self.background_label.setPixmap(pixmap)
            self.background_label.setScaledContents(True)

        # Position background to fill entire widget
        self.background_label.setGeometry(self.rect())
        self.background_label.lower()  # Send to back

    def resizeEvent(self, event):
        """Update background size when window is resized."""
        super().resizeEvent(event)
        if hasattr(self, 'background_label'):
            self.background_label.setGeometry(self.rect())

    def on_enter(self):
        """Called when screen becomes active."""
        pass

    def on_exit(self):
        """Called when leaving this screen."""
        pass

    def cleanup(self):
        """Called when screen is being destroyed."""
        pass
