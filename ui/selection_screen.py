import os
from PySide6.QtCore import Qt
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
from utils import get_png_file_paths
from ui.styles import buttons_css


class SelectionScreen(BaseScreen):
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

        # Navigation buttons
        top_nav_layout = QHBoxLayout()

        self.prev_button = QPushButton("← Previous")
        self.prev_button.clicked.connect(self.show_previous_images)
        self.prev_button.setStyleSheet(buttons_css)
        self.next_button_nav = QPushButton("Next →")
        self.next_button_nav.clicked.connect(self.show_next_images)
        self.next_button_nav.setStyleSheet(buttons_css)

        self.page_label = QLabel()
        self.page_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        top_nav_layout.addWidget(self.prev_button)
        top_nav_layout.addWidget(self.page_label)
        top_nav_layout.addWidget(self.next_button_nav)

        bottom_nav_layout = QHBoxLayout()
        print_button = QPushButton("Print!")
        print_button.clicked.connect(lambda: self.navigate_to.emit("print"))
        print_button.setStyleSheet(buttons_css)
        bottom_nav_layout.addWidget(print_button)

        # Grid for images
        self.grid_widget = QWidget()
        self.grid_layout = QGridLayout(self.grid_widget)

        main_layout.addLayout(top_nav_layout)
        main_layout.addWidget(self.grid_widget)
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

        self.prev_button.setEnabled(self.current_page > 0)
        self.next_button_nav.setEnabled(self.current_page < total_pages - 1)

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
