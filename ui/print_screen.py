import os
from PySide6.QtCore import QRect, Qt
from PySide6.QtGui import QFont, QPixmap
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)
from PIL import Image
from components.range_selector import RangeSelectorWidget
from controllers.image_processor import ImageProcessor
from controllers.session_manager import SessionManager
from ui.base_screen import BaseScreen
from ui.styles import buttons_css
import cv2 as cv
from python_parallel_print import mock_printer


class PrintScreen(BaseScreen):
    def __init__(
        self, image_processor: ImageProcessor, session_manager: SessionManager
    ):
        super().__init__()
        self._image_processor = image_processor
        self._session_manager = session_manager
        self._composite_image = None
        self.printer = mock_printer.MockPrinter()
        self._setup_ui()

    def _setup_ui(self):
        """Set up the UI for the print screen."""
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Title
        title_label = QLabel("Your Photo is Ready!")
        title_font = QFont()
        title_font.setPointSize(20)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("color: #C9A961; margin: 20px;")
        main_layout.addWidget(title_label)

        # Image preview label
        self.preview_widget = QWidget()
        self.preview_widget.setObjectName("previewWidget")

        self.preview_widget.setMinimumSize(900, 700)
        self.preview_widget.setStyleSheet(
            "QWidget#previewWidget {border-top: 3px solid #C9A961; background-color: white;}"
        )

        self.preview_layout = QHBoxLayout(self.preview_widget)
        self.preview_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.preview_label = QLabel()
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setMinimumSize(800, 640)
        self.preview_layout.addWidget(self.preview_label, 2)

        self.add_number_of_prints_label = RangeSelectorWidget(
            initial_value=2,
            min_value=2,
            max_value=None,
            label_text="Number of prints",
        )
        self.add_number_of_prints_label.setMaximumHeight(300)
        self.preview_layout.addWidget(self.add_number_of_prints_label, 1)

        main_layout.addWidget(self.preview_widget)

        # Buttons layout
        button_layout = QHBoxLayout()
        button_layout.setSpacing(20)

        # Back button
        back_button = QPushButton("Back to Selection")
        back_button.setFont(QFont("Impact"))
        back_button.setStyleSheet(buttons_css)
        back_button.clicked.connect(lambda: self.navigate_to.emit("selection"))

        # Print button
        print_button = QPushButton("Print Photo")
        print_button.setFont(QFont("Impact"))
        print_button.setStyleSheet(buttons_css)
        print_button.clicked.connect(self._on_print_clicked)

        # Popup dialog
        self.popup_dialog = QDialog(self)
        self.popup_dialog.setWindowTitle("Print Status")
        self.popup_dialog.setModal(True)  # Make it modal (blocks other interactions)
        # TODO make it center
        self.popup_dialog.setGeometry(QRect(100, 100, 400, 200))

        popup_layout = QVBoxLayout(self.popup_dialog)
        popup_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        popup_message = QLabel(text="Sent to print")
        popup_message.setFont(QFont("Impact"))
        popup_message.setAlignment(Qt.AlignmentFlag.AlignCenter)
        popup_message.setStyleSheet("color: black;")
        popup_layout.addWidget(popup_message)  # Add the label to the layout

        # Optional: Add a close button
        close_button = QPushButton("OK")
        close_button.setFont(QFont("Impact"))
        close_button.setStyleSheet(buttons_css)
        close_button.clicked.connect(self.popup_dialog.close)
        popup_layout.addWidget(close_button)

        # Start over button
        start_over_button = QPushButton("Start Over")
        start_over_button.setFont(QFont("Impact"))
        start_over_button.setStyleSheet(buttons_css)
        start_over_button.clicked.connect(lambda: self.navigate_to.emit("title"))

        button_layout.addWidget(back_button)
        button_layout.addWidget(print_button)
        button_layout.addWidget(start_over_button)

        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

    def on_enter(self):
        """Called when entering the print screen - generate the composite."""
        # This will be called with selected photos from SelectionScreen
        pass

    def generate_composite(self, photos_path):
        """Create and display the photo composite."""
        # Get template info from session manager
        template_path, num_photos, preview_path = self._session_manager.template_info

        if template_path is None or num_photos is None or preview_path is None:
            raise ValueError("No template info available in session")

        # Create the composite
        self._composite_image = self._image_processor.create_photo_composite(
            photo_paths=photos_path,
            template_path=template_path,
        )

        # Display the selected preview strip in the preview
        self._display_preview_strip(preview_path)

        return self._composite_image

    def _display_preview_strip(self, preview_path):
        """Display the preview image in the preview label."""
        if preview_path is None:
            raise ValueError("No preview path available in session")

        pixmap = QPixmap(preview_path)

        pixmap_scaled = pixmap.scaled(
            self.preview_label.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )

        # Convert for QPixmap for display
        self.preview_label.setPixmap(pixmap_scaled)

    def _on_print_clicked(self):
        """Handle print button click."""
        if self._composite_image is None:
            print("No composite image to print")
            return

        # Save the composite to session folder with DPI preserved
        session_folder = self._session_manager.get_current_session_folder
        if session_folder:
            output_path = os.path.join(session_folder, "final_composite.png")

            # Get DPI from image processor (preserves original or defaults to 300)
            dpi = self._image_processor.get_composite_dpi()

            # Convert BGR to RGB for PIL
            composite_rgb = cv.cvtColor(self._composite_image, cv.COLOR_BGR2RGB)

            # Save with PIL to preserve/set DPI
            img = Image.fromarray(composite_rgb)
            img.save(output_path, dpi=dpi)
            print(f"Composite saved to: {output_path} (DPI: {dpi})")

        print("Sending to printer...")
        self.popup_dialog.show()
        self.printer.print_images(
            output_path,
            num_copies=int(self.add_number_of_prints_label.current_value / 2),
        )
