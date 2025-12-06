import os
from pathlib import Path
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)
from components.clickable_label import ClickableLabel
from controllers.session_manager import SessionManager
from ui.base_screen import BaseScreen
from utils.utils import get_png_file_paths
from ui.styles import buttons_css
from utils.generate_preview_strips import generate_preview_strip


class SelectionScreen(BaseScreen):
    """
    Previews photos and allows user to select up to 3 photo

    Emits signal
        layout_path: str,
        num_photos: int,
        template_index: int
    """

    layout_selected = Signal(str, int, int)

    def __init__(self, session_manager: SessionManager, parent=None):
        super().__init__(parent)
        self.session_manager = session_manager
        self.current_session_folder = None
        self._setup_ui()

    def on_enter(self):
        self.current_session_folder = self.session_manager.get_current_session_folder
        # Load images from current session folder
        if self.current_session_folder and os.path.exists(self.current_session_folder):
            self.all_image_paths = get_png_file_paths(self.current_session_folder)
            print(
                f"Loaded {len(self.all_image_paths)} images from {self.current_session_folder}"
            )
        else:
            self.all_image_paths = []
            print("No session folder found")
        self.current_page = 0
        self.update_image_grid()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)

        self.current_page = 0
        self.images_per_page = 4
        self.selected_photos = []  # Track selected image paths
        self.selected_labels = {}  # Track labels by path for styling
        self.all_image_paths = []  # Will be populated when showing selection screen
        self.preview_strip_paths = {}  # Store preview strip paths {2: path, 3: path}

        # Navigation buttons
        top_nav_layout = QHBoxLayout()

        self.page_label = QLabel()
        self.page_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # top_nav_layout.addWidget(self.prev_button)
        top_nav_layout.addWidget(self.page_label)
        # top_nav_layout.addWidget(self.next_button_nav)

        bottom_nav_layout = QHBoxLayout()
        label_instructions = QLabel("Select min 2, max 3 photos")
        label_instructions.setStyleSheet("font-size: 48px; color: blue;")
        print_button = QPushButton("Next")
        print_button.clicked.connect(self._cleanup_and_move_to_print)
        print_button.setStyleSheet(buttons_css)
        bottom_nav_layout.addWidget(label_instructions)
        bottom_nav_layout.addWidget(print_button)

        # Grid for images
        self.grid_widget = QWidget()
        self.grid_layout = QGridLayout(self.grid_widget)

        # Preview area for strips
        self.preview_widget = QWidget()
        self.preview_layout = QVBoxLayout(self.preview_widget)
        self.preview_label = QLabel("Preview")
        self.preview_label.setStyleSheet(
            "font-size: 24px; font-weight: bold; color: #2d5a2d;"
        )
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setVisible(False)

        self.preview_strip_label = QLabel()
        self.preview_strip_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_strip_label.setVisible(False)

        self.preview_layout.addWidget(self.preview_label)
        self.preview_layout.addWidget(self.preview_strip_label)

        main_layout.addLayout(top_nav_layout)
        main_layout.addWidget(self.grid_widget)
        main_layout.addWidget(self.preview_widget)
        main_layout.addLayout(bottom_nav_layout)

        # Load first page
        self.update_image_grid()

    def show_previous_images(self):
        if self.current_page > 0:
            self.current_page -= 1
            self.update_image_grid()

    def show_next_images(self):
        total_pages = (
            len(self.all_image_paths) + self.images_per_page - 1
        ) // self.images_per_page
        if self.current_page < total_pages - 1:
            self.current_page += 1
            self.update_image_grid()

    def update_image_grid(self):
        # Clear existing widgets
        for i in reversed(range(self.grid_layout.count())):
            self.grid_layout.itemAt(i).widget().setParent(None)

        # Calculate page bounds
        start_idx = self.current_page * self.images_per_page
        end_idx = min(start_idx + self.images_per_page, len(self.all_image_paths))
        current_paths = self.all_image_paths[start_idx:end_idx]

        # Display images in 2x2 grid
        rows = 2
        cols = 2
        for i, path in enumerate(current_paths):
            row = i // cols
            col = i % cols

            label = ClickableLabel(path)
            label.setFixedSize(300, 225)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)

            pixmap = QPixmap(path)
            scaled_pixmap = pixmap.scaled(
                label.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            label.setPixmap(scaled_pixmap)
            label.clicked.connect(self._on_label_clicked)

            # Apply selection styling if already selected
            if path in self.selected_photos:
                label.setStyleSheet("border: 5px solid #2d5a2d;")
                label.is_selected = True
            else:
                label.setStyleSheet("border: 2px solid #ccc;")

            self.selected_labels[path] = label
            self.grid_layout.addWidget(label, row, col)

        # Update navigation
        total_pages = (
            len(self.all_image_paths) + self.images_per_page - 1
        ) // self.images_per_page
        self.page_label.setText(f"Page {self.current_page + 1} of {total_pages}")

        # # Update button states
        # self.prev_button.setEnabled(self.current_page > 0)
        # self.next_button_nav.setEnabled(self.current_page < total_pages - 1)

        # # Apply disabled styling
        # if self.current_page > 0:
        #     self.prev_button.setStyleSheet(buttons_css)
        # else:
        #     self.prev_button.setStyleSheet(
        #         buttons_css + "background-color: #666; color: #999;"
        #     )

        # if self.current_page < total_pages - 1:
        #     self.next_button_nav.setStyleSheet(buttons_css)
        # else:
        #     self.next_button_nav.setStyleSheet(
        #         buttons_css + "background-color: #666; color: #999;"
        #     )

    def _on_label_clicked(self, image_path):
        """Handle image selection/deselection"""
        if image_path in self.selected_photos:
            # Deselect
            self.selected_photos.remove(image_path)
            if image_path in self.selected_labels:
                self.selected_labels[image_path].setStyleSheet(
                    "border: 2px solid #ccc;"
                )
                self.selected_labels[image_path].is_selected = False
        else:
            # Select
            self.selected_photos.append(image_path)
            if image_path in self.selected_labels:
                self.selected_labels[image_path].setStyleSheet(
                    "border: 5px solid #2d5a2d;"
                )
                self.selected_labels[image_path].is_selected = True

        print(f"Selected photos: {len(self.selected_photos)} - {self.selected_photos}")

        # Update preview strip when 2 or 3 photos are selected
        self._update_preview_strip()

    def _update_preview_strip(self):
        """Generate and display preview strip based on number of selected photos."""
        num_selected = len(self.selected_photos)

        # Only show preview for 2 or 3 selected photos
        if num_selected in [2, 3] and self.current_session_folder:
            # Map number of photos to template configuration
            if num_selected == 3:
                selected_template_index = 0  # templateup4 (2x3 grid)
                selected_template_path = "./resources/templates/v0.1/templateup4.png"
            elif num_selected == 2:
                selected_template_index = 3  # templateup3 (2x2 grid)
                selected_template_path = "./resources/templates/v0.1/templateup3.png"

            # Generate preview strip
            strip_path = generate_preview_strip(
                photo_paths=self.selected_photos,
                num_photos=num_selected,
                output_dir=self.current_session_folder,
                output_prefix="preview_strip",
            )

            if strip_path and os.path.exists(strip_path):
                # Store generated preview strip
                self.preview_strip_paths[num_selected] = strip_path
                # Load and display the preview strip
                pixmap = QPixmap(strip_path)
                # Scale to reasonable size (e.g., 600px wide)
                scaled_pixmap = pixmap.scaledToWidth(
                    600, Qt.TransformationMode.SmoothTransformation
                )
                self.preview_strip_label.setPixmap(scaled_pixmap)
                self.preview_strip_label.setVisible(True)
                self.preview_label.setVisible(True)
                print(f"Updated preview strip with {num_selected} photos: {strip_path}")
                print(
                    f"Selected template: index={selected_template_index}, path={selected_template_path}"
                )
                self.layout_selected.emit(
                    selected_template_path, num_selected, selected_template_index
                )

            else:
                print(f"Failed to generate preview strip for {num_selected} photos")
                self._hide_preview_strip()
        else:
            # Hide preview if not 2 or 3 photos selected
            self._hide_preview_strip()
            self.selected_template_index = None
            self.selected_template_path = None

    def _hide_preview_strip(self):
        """Hide the preview strip."""
        self.preview_strip_label.setVisible(False)
        self.preview_label.setVisible(False)

    def _cleanup_and_move_to_print(self):
        try: 
            for p in self.preview_strip_paths.values():
                os.remove(p)
        except:
            pass # expect that the path might not always exists
            
        self.navigate_to.emit("print")
