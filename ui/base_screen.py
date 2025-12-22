from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget


class BaseScreen(QWidget):
    navigate_to = Signal(str)  # Emit screen name to navigate to

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background-color: #ffffff;")

    def on_enter(self):
        """Called when screen becomes active."""
        pass

    def on_exit(self):
        """Called when leaving this screen."""
        pass

    def cleanup(self):
        """Called when screen is being destroyed."""
        pass
