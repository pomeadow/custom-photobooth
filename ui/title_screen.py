import os
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QLabel, QVBoxLayout
from ui.base_screen import BaseScreen
from components.decorative_button import DecorativeButton


class TitleScreen(BaseScreen):
    create_session_signal = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        abs_path = os.path.abspath("./resources/UI Asset/UI Background (Solid Colour)-01.png")
        pixmap = QPixmap(abs_path)

        self.background_label = QLabel(self)
        if not pixmap.isNull():
            self.background_label.setPixmap(pixmap)
            self.background_label.setScaledContents(True)

        # Position background to fill entire widget
        self.background_label.setGeometry(self.rect())
        self.background_label.lower()  # Send to back
        
        # Main layout with content
        title_layout = QVBoxLayout(self)
        title_layout.setAlignment(Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignCenter)
        title_layout.setContentsMargins(100, 0, 100, 80)  # Add bottom margin

        start_photobooth_button = DecorativeButton("START", min_width=800, min_height=120)
        start_photobooth_button.clicked.connect(self._emit_signals)

        title_layout.addWidget(start_photobooth_button, 0, Qt.AlignmentFlag.AlignCenter)

    # Override resizeEvent to adjust background
    def resizeEvent(self, event):
        """Update background size when window is resized."""
        super().resizeEvent(event)
        if hasattr(self, 'background_label'):
            self.background_label.setGeometry(self.rect())

    def on_enter(self):
        return super().on_enter()

    def on_exit(self):
        return super().on_exit()
    
    def _emit_signals(self):
        self.create_session_signal.emit()
        self.navigate_to.emit("camera")
