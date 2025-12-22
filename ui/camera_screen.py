from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
)
from components.countdown_timer import CountdownTimer
from components.flash_overlay import FlashOverlay
from controllers.camera_controller import CameraController
from controllers.image_processor import ImageProcessor
from controllers.session_manager import SessionManager
from ui.base_screen import BaseScreen
from ui.styles import buttons_css, counter_css, timer_css
from utils.utils import load_sound_effect


class CameraScreen(BaseScreen):
    # Signals
    session_continued = Signal()

    def __init__(
        self,
        camera_controller: CameraController,
        image_processor: ImageProcessor,
        session_manager: SessionManager,
        camera_index: int = 0,
        parent=None,
    ):
        super().__init__(parent)
        self.camera_controller = camera_controller
        self.image_processor = image_processor
        self.session_manager = session_manager
        self.camera_index = camera_index
        self.photos_to_take = 1
        self.photos_taken = 0
        self.countdown = CountdownTimer()
        self._overlay_path = None
        self.sound_effect = load_sound_effect("./resources/sounds/countdown_beep.wav")
        self.sound_effect.setLoopCount(1) # Play only once per trigger
        self._setup_ui()
        self._connect_signals()

    def on_enter(self):
        """Called when screen becomes active."""
        print(f"CameraScreen.on_enter() called. photos_to_take={self.photos_to_take}")
        self.countdown.start(10)  # Start 10 second countdown

    def on_exit(self):
        """Called when leaving this screen."""
        # self.camera_controller.stop_camera()
        self.countdown.stop()

    def reset(self):
        self.photos_taken = 0
        self._update_counter()

    def _setup_ui(self):
        # Main layout
        main_layout = QVBoxLayout(self)

        # Top panel for controls
        top_panel = QHBoxLayout()
        top_panel.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Control buttons
        self.back_button = QPushButton("← Back to Title")
        self.back_button.clicked.connect(lambda: self.navigate_to.emit("title"))
        self.back_button.setStyleSheet(buttons_css)

        self.capture_button = QPushButton("Capture")
        self.capture_button.clicked.connect(self._capture_photo)
        self.capture_button.setStyleSheet(buttons_css)

        # Photo counter
        self.counter_label = QLabel()
        self.counter_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.counter_label.setStyleSheet(counter_css)
        self._update_counter()

        self.timer_label = QLabel()
        self.timer_label.setMinimumSize(100, 50)
        self.timer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.timer_label.setStyleSheet(timer_css)

        # Add to top panel
        top_panel.addWidget(self.back_button, 1)
        top_panel.addWidget(self.counter_label, 2)

        # top_panel.addWidget(self.capture_button)
        top_panel.addWidget(self.timer_label, 2)
        top_panel.addWidget(self.capture_button, 1)

        # TODO set fixed size for top panel

        # Right panel for camera preview
        self.camera_label = QLabel()
        self.camera_label.setMinimumSize(640, 480)
        self.camera_label.setText("Camera preview will appear here")
        self.camera_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.flash = FlashOverlay(self.camera_label)

        # Add to main layout
        main_layout.addLayout(top_panel, 0)  # 0 = no stretch
        main_layout.addWidget(self.camera_label, 1)  # 1 = takes remaining space

    def _connect_signals(self):
        """Connect all signals."""
        # Camera signals
        self.camera_controller.frame_ready.connect(self._on_camera_frame)

        # Countdown signals
        self.countdown.tick.connect(self._on_countdown_tick)
        self.countdown.finished.connect(self._on_countdown_finished)

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
            self.session_continued.emit()
            self.navigate_to.emit("selection")
        else:
            # Only restart 5 seconds countdown if we still have photos to take
            self.countdown.start(1)

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
        if seconds == 4:
            # Start playing sound effect
            self.sound_effect.play()

    def _on_countdown_finished(self):
        self.timer_label.setText("Time's up!")
        self.countdown.stop()
        # Auto-capture photo when timer reaches 0
        self._capture_photo()
