from PySide6.QtWidgets import QLabel
from PySide6.QtCore import Signal, Qt


class ClickableLabel(QLabel):
    clicked = Signal(str)

    def __init__(self, image_path="", parent=None):
        super().__init__(parent)
        self.image_path = image_path
        self.is_selected = False
        self.is_clickable = True

    def mousePressEvent(self, event):
        # Emit the custom 'clicked' signal when the mouse is pressed on the label
        if event.button() == Qt.MouseButton.LeftButton and self.is_clickable:
            self.clicked.emit(self.image_path)
        super().mousePressEvent(event)  # Call the base class method

    def set_clickable(self, clickable: bool):
        """Enable or disable clicking on this label."""
        self.is_clickable = clickable
        # Change cursor to indicate clickable state
        if clickable:
            self.setCursor(Qt.CursorShape.PointingHandCursor)
        else:
            self.setCursor(Qt.CursorShape.ForbiddenCursor)
