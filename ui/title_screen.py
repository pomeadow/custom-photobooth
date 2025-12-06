import os
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QPixmap
from PySide6.QtWidgets import QLabel, QPushButton, QVBoxLayout, QWidget
from ui.base_screen import BaseScreen


class TitleScreen(BaseScreen):
    create_session_signal = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        title_layout = QVBoxLayout(self)
        title_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        pixmap = QPixmap("./resources/title.jpg")
        image_label = QLabel()
        image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        image_label.setFixedSize(800, 600)

        scaledPixmap = pixmap.scaled(
            image_label.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        image_label.setPixmap(scaledPixmap)

        # Title label
        # title_label = QLabel("🎄 Merry Christmas!! 🎄")
        # title_font = QFont()
        # title_font.setPointSize(36)
        # title_font.setBold(True)
        # title_label.setFont(title_font)
        # title_label.setAlignment(Qt.AlignCenter)
        # title_label.setStyleSheet("color: #d42c2c; margin: 50px;")

        # # Subtitle
        # subtitle_label = QLabel("Welcome to our Christmas Photobooth!")
        # subtitle_font = QFont()
        # subtitle_font.setPointSize(16)
        # subtitle_label.setFont(subtitle_font)
        # subtitle_label.setAlignment(Qt.AlignCenter)
        # subtitle_label.setStyleSheet("color: #2d5a2d; margin: 20px;")

        # Start button
        start_photobooth_button = QPushButton("Start")
        start_photobooth_button.setFont(QFont("Impact", 48, QFont.Weight.Bold))
        start_photobooth_button.setStyleSheet("""
            QPushButton {
                background-color: #d42c2c;
                color: white;
                border: none;
                padding: 20px 40px;
                border-radius: 10px;
                margin: 30px;
            }
            QPushButton:hover {
                background-color: #b82424;
            }
            QPushButton:pressed {
                background-color: #a01e1e;
            }
        """)
        start_photobooth_button.clicked.connect(self._emit_signals)

        # title_layout.addWidget(title_label)
        # title_layout.addWidget(subtitle_label)
        title_layout.addWidget(image_label)
        title_layout.addWidget(start_photobooth_button)

    def on_enter(self):
        return super().on_enter()

    def on_exit(self):
        return super().on_exit()

    def _emit_signals(self):
        self.create_session_signal.emit()
        self.navigate_to.emit("camera")
