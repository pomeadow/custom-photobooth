from PySide6.QtWidgets import QLabel
from PySide6.QtCore import Signal, Qt


class ClickableLabel(QLabel):
    clicked = Signal(str)

    def __init__(self, image_path="", parent=None):
        super().__init__(parent)
        self.image_path = image_path
        self.is_selected = False

    def mousePressEvent(self, event):
        # Emit the custom 'clicked' signal when the mouse is pressed on the label
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.image_path)
        super().mousePressEvent(event)  # Call the base class method
