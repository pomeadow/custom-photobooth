from email.mime import image
import os
from typing import List
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
)
from components.countdown_timer import CountdownTimer
from components.flash_overlay import FlashOverlay
from controllers.camera_controller import CameraController
from controllers.image_processor import ImageProcessor
from controllers.session_manager import SessionManager
from ui.base_screen import BaseScreen
from ui.styles import buttons_css


class CameraScreen(BaseScreen):
    # Signals
    session_complete = Signal()
    session_continued = Signal()

    def __init__(
        self,
        camera_controller: CameraController,
        image_processor: ImageProcessor,
        session_manager: SessionManager,
        frame_options: List[str],
        parent=None,
    ):
        super().__init__(parent)
        self.camera_controller = camera_controller
        self.image_processor = image_processor
        self.session_manager = session_manager
        self.photos_to_take = 1
        self.photos_taken = 0
        self.countdown = CountdownTimer()
        self._frame_options = frame_options
        self._overlay_path = None
        self._setup_ui()
        self._connect_signals()

    def on_enter(self):
        """Called when screen becomes active."""
        print(f"CameraScreen.on_enter() called. photos_to_take={self.photos_to_take}")
        self.photos_taken = 0
        self._update_counter()
        if self.camera_controller.start_camera():
            self.countdown.start(5)  # Start 20 second countdown
        else:
            self.timer_label.setText("Camera Error")

    def on_exit(self):
        """Called when leaving this screen."""
        self.camera_controller.stop_camera()
        self.countdown.stop()

    def cleanup(self):
        """Called when screen is being destroyed."""
        pass

    def _setup_ui(self):
        # Main layout
        main_layout = QHBoxLayout(self)

        # Left panel for controls
        left_panel = QVBoxLayout()
        # Frame selector (placeholder for now)
        frame_label = QLabel("Frame:")
        self.frame_combo = QComboBox()
        self.frame_combo.addItems(
            ["Default Frame", "Heart Frame", "Star Frame", "Frame 3", "Frame 4"]
        )
        self.frame_combo.setStyleSheet("color: red;")
        self.frame_combo.currentIndexChanged.connect(self._on_frame_combo_changed)

        # Control buttons
        self.back_button = QPushButton("← Back to Title")
        self.back_button.clicked.connect(lambda: self.navigate_to.emit("title"))
        self.back_button.setStyleSheet(buttons_css)

        # self.capture_button = QPushButton("Capture Photo")
        # self.capture_button.clicked.connect(self._capture_photo)
        # self.capture_button.setStyleSheet(buttons_css)

        self.next_button = QPushButton("Next")
        self.next_button.setFont(QFont("Arial", 18))
        self.next_button.setStyleSheet(buttons_css)
        self.next_button.clicked.connect(lambda: self.navigate_to.emit("selection"))
        self.next_button.setEnabled(False)

        # Photo counter
        self.counter_label = QLabel()
        self.counter_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.counter_label.setStyleSheet("font-size: 48px; color: blue;")
        self._update_counter()

        self.timer_label = QLabel()
        self.timer_label.setMinimumSize(100, 50)
        self.timer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.timer_label.setStyleSheet("font-size: 48px; color: blue;")

        # Add to left panel
        left_panel.addWidget(self.back_button)
        left_panel.addWidget(self.counter_label)
        if os.getenv("VERSION") == "0.0":
            left_panel.addWidget(frame_label)
            left_panel.addWidget(self.frame_combo)

        # left_panel.addWidget(self.capture_button)

        left_panel.addWidget(self.next_button)
        left_panel.addWidget(self.timer_label)
        # TODO set fixed size for left panel
        # left_panel_widget.setFixedWidth(200)

        # Right panel for camera preview
        self.camera_label = QLabel()
        self.camera_label.setMinimumSize(640, 480)
        self.camera_label.setStyleSheet("border: 1px solid black")
        self.camera_label.setText("Camera preview will appear here")
        self.camera_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.flash = FlashOverlay(self.camera_label)

        # Add to main layout
        main_layout.addLayout(left_panel, 0)  # 0 = no stretch
        main_layout.addWidget(self.camera_label, 1)  # 1 = takes remaining space

    def _connect_signals(self):
        """Connect all signals."""
        # Camera signals
        self.camera_controller.frame_ready.connect(self._on_camera_frame)

        # Countdown signals
        self.countdown.tick.connect(self._on_countdown_tick)
        self.countdown.finished.connect(self._on_countdown_finished)

        # Button signals
        self.next_button.clicked.connect(lambda: self.navigate_to.emit("selection"))

    def _on_camera_frame(self, frame):
        """Update preview with camera frame."""
        # Apply overlay and convert to pixmap
        processed = self.image_processor.apply_overlay(
            frame, None, flip_horizontal=False
        )
        pixmap = self.image_processor.frame_to_qpixmap(
            processed,
            target_size=(self.camera_label.width(), self.camera_label.height()),
        )
        self.camera_label.setPixmap(pixmap)

    def _capture_photo(self):
        frame = self.camera_controller.capture_photo()
        if frame is None:
            return

        processed = self.image_processor.apply_overlay(
            frame, None, flip_horizontal=False
        )

        self.session_manager.save_photo(processed)

        # Add flash effect
        self.flash.flash()
        self.photos_taken += 1
        self._update_counter()

        if self.photos_taken >= self.photos_to_take:
            if os.getenv("VERSION") == "0.0":
                self.session_complete.emit()
            else:
                self.session_continued.emit()
            self.navigate_to.emit("selection")
        else:
            # Only restart 20 seconds countdown if we still have photos to take
            self.countdown.start(5)

    def _on_frame_combo_changed(self, index):
        print(f"Selected item index: {index}")
        self._overlay_path = self._frame_options[index]
        self.image_processor.load_overlay(self._frame_options[index])

    def _update_counter(self):
        """Update photo counter display."""
        self.counter_label.setText(
            f"Photos: {self.photos_taken} / {self.photos_to_take}"
        )

    def set_photos_to_take(self, count: int):
        """Set how many photos to capture in this session."""
        print(f"Setting photos_to_take to: {count}")
        self.photos_to_take = count
        self._update_counter()
        print(f"Counter updated. photos_to_take is now: {self.photos_to_take}")

    def _on_countdown_tick(self, seconds: int):
        self.timer_label.setText(str(seconds))

    def _on_countdown_finished(self):
        self.timer_label.setText("0")
        self.countdown.stop()
        # Auto-capture photo when timer reaches 0
        self._capture_photo()
