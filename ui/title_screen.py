from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QVBoxLayout
from ui.base_screen import BaseScreen
from components.decorative_button import DecorativeButton


class TitleScreen(BaseScreen):
    create_session_signal = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        # Main layout with content
        title_layout = QVBoxLayout(self)
        title_layout.setAlignment(Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignCenter)
        title_layout.setContentsMargins(100, 0, 100, 80)  # Add bottom margin

        start_photobooth_button = DecorativeButton("START")
        start_photobooth_button.clicked.connect(self._emit_signals)

        title_layout.addWidget(start_photobooth_button, 0, Qt.AlignmentFlag.AlignCenter)

    def on_enter(self):
        return super().on_enter()

    def on_exit(self):
        return super().on_exit()
    
    def _emit_signals(self):
        self.create_session_signal.emit()
        self.navigate_to.emit("camera")

        # pixmap = QPixmap("./resources/UI Asset/UI Background (Solid Colour)-01.png")
        # image_label = QLabel()
        # image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # scaledPixmap = pixmap.scaled(
        #     self.size(),
        #     Qt.AspectRatioMode.KeepAspectRatio,
        #     Qt.TransformationMode.SmoothTransformation,
        # )
        # image_label.setPixmap(scaledPixmap)

        # button_layout = QVBoxLayout(self)
        # # Start button
        # start_photobooth_button = QPushButton()
        # start_photobooth_button_img = QPixmap("./resources/UI Asset/Asset - Start Button.png")
        # start_photobooth_button_img_scaled = start_photobooth_button_img.scaled(
        #     start_photobooth_button.size(),
        #     Qt.AspectRatioMode.KeepAspectRatio,
        #     Qt.TransformationMode.SmoothTransformation,
        # )
        # start_photobooth_button.setIcon(
        #     start_photobooth_button_img_scaled
        # )
        # start_photobooth_button.clicked.connect(self._emit_signals)
        # button_layout.setSpacing(20)
        # button_layout.addWidget(start_photobooth_button)

        # title_layout.addWidget(image_label)
