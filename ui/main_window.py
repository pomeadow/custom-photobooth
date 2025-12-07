import os
from dotenv import load_dotenv
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QMainWindow, QStackedWidget, QWidget
from controllers.camera_controller import CameraController
from controllers.image_processor import ImageProcessor
from controllers.session_manager import SessionManager
from ui.camera_screen import CameraScreen
from ui.print_screen import PrintScreen
from ui.selection_screen import SelectionScreen
from ui.title_screen import TitleScreen

# Load environment variables
load_dotenv()


class PhotoboothGUI(QMainWindow):
    def __init__(self, DEFAULT_OVERLAY_PATH) -> None:
        super().__init__()
        self.setWindowTitle("Christmas Photobooth")
        self.setGeometry(100, 100, 800, 600)
        self.setMinimumSize(
            800, 600
        )  # Set minimum window size to prevent cutting off content

        # Initialize camera
        base_dir = os.getcwd()
        self._camera_controller = CameraController()
        self._camera_index = int(os.getenv("CAMERA_INDEX", "0"))
        self._session_manager = SessionManager(base_dir=base_dir)
        self._image_processor = ImageProcessor()

        self.DEFAULT_OVERLAY_PATH = DEFAULT_OVERLAY_PATH
        self.number_of_photos = 1
        self.current_session_folder = None
        self.selected_layout_path = None
        self._setup_ui()

    def _setup_ui(self):
        # Create stacked widget to switch between screens
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.setStyleSheet("background-color: #ffffff;")
        self.setCentralWidget(self.stacked_widget)

        # Create title screen
        self.title_screen = TitleScreen()
        self.camera_screen = CameraScreen(
            camera_controller=self._camera_controller,
            image_processor=self._image_processor,
            session_manager=self._session_manager,
            frame_options=[
                self.DEFAULT_OVERLAY_PATH,
                "./resources/frames/christmas-frame1.png",
                "./resources/frames/3.png",
                "./resources/frames/christmas-frame3.png",
            ],
            camera_index=self._camera_index,
        )
        self.selection_screen = SelectionScreen(session_manager=self._session_manager)
        self.print_screen = PrintScreen(
            image_processor=self._image_processor, session_manager=self._session_manager
        )

        # Order that it is added matters
        self.stacked_widget.addWidget(self.title_screen)
        self.stacked_widget.addWidget(self.camera_screen)
        self.stacked_widget.addWidget(self.selection_screen)
        self.stacked_widget.addWidget(self.print_screen)

        self.title_screen.navigate_to.connect(self.navigate_to_screen)
        self.camera_screen.navigate_to.connect(self.navigate_to_screen)
        self.selection_screen.navigate_to.connect(self.navigate_to_screen)
        self.print_screen.navigate_to.connect(self.navigate_to_screen)

        self.camera_screen.session_complete.connect(self._on_session_complete)

        # Connect this method to the same method if layout screen if not active
        self.title_screen.create_session_signal.connect(
            self._on_skip_layout_create_session
        )
        self.camera_screen.session_continued.connect(self._on_session_continued)
        self.selection_screen.layout_selected.connect(self._on_layout_selected)

        # Start with title screen
        self.navigate_to_screen("title")
        self.stacked_widget.setCurrentIndex(0)

    def navigate_to_screen(self, screen_name: str):
        screen_map = {"title": 0, "camera": 1, "selection": 2, "print": 3}

        # Call on_exit for current screen
        current_widget = self.stacked_widget.currentWidget()
        if hasattr(current_widget, "on_exit"):
            current_widget.on_exit()  # type: ignore

        if screen_name == "title":
            self._session_manager.reset_session()
            self.camera_screen.reset()
            self.selection_screen.reset()

        # Special handling for print screen - generate composite
        if screen_name == "print":
            selected_photos = self.selection_screen.selected_photos
            if not selected_photos:
                print("No photos selected!")
                return
            # Generate the composite before switching
            self.print_screen.generate_composite(selected_photos)

        # Switch to new screen
        new_index = screen_map[screen_name]
        self.stacked_widget.setCurrentIndex(new_index)

        # Call on_enter for new screen
        new_widget = self.stacked_widget.currentWidget()
        if hasattr(new_widget, "on_enter"):
            new_widget.on_enter()  # type: ignore

    def _on_layout_selected(
        self,
        layout_path: str,
        num_photos: int,
        template_index: int,
    ):
        """Handle layout selection."""
        # Update the current session with selected template info
        self._session_manager.set_template_path(layout_path)
        self._session_manager.set_template_index(template_index)
        self._session_manager.set_num_photos(num_photos)

    def _on_skip_layout_create_session(self):
        # Configure camera screen
        self.camera_screen.set_photos_to_take(4)

        # Create new session with template info -- num of photos to set later
        self._session_manager.create_default_session()

        # Navigate to camera
        self.navigate_to_screen("camera")

    def _on_session_complete(self):
        """Handle photo session completion."""
        # Could show completion message, play sound, etc.
        if self._session_manager.template_info is None:
            raise ValueError("Should not happen")
        if self._session_manager.template_info[0] is None:
            raise ValueError("Should not happen")
        self._image_processor.load_overlay(self._session_manager.template_info[0])
        pass

    def _on_session_continued(self):
        # Could show completion message, play sound, etc.
        if self._session_manager.template_info is None:
            raise ValueError("Should not happen")
        pass

    def closeEvent(self, event):
        """Cleanup when window closes."""
        self._camera_controller.stop_camera()
        event.accept()
