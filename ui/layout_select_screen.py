from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QPixmap
from PySide6.QtWidgets import QGridLayout, QLabel, QPushButton, QVBoxLayout, QWidget
from components.clickable_label import ClickableLabel
from components.range_selector import RangeSelectorWidget
from ui.base_screen import BaseScreen
from ui.styles import buttons_css
from config.load_metadata import layout_metadata_v0_1, templates_path
from generate_all_composites import get_session_photos, generate_all_composites


class LayoutSelectScreen(BaseScreen):
    # Signals
    layout_selected = Signal(
        str, int, int, int
    )  # (template_path, num_photos, template_index, template_num_of_photos)

    def __init__(self, session_manager=None, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background-color: #ffffff;")
        # Layout metadata: {path: {index, num_photos, display_text}}
        self.session_manager = session_manager
        self.templates_path = templates_path
        self.layout_labels = {}  # Dictionary to track all layout labels
        self.layout_metadata = layout_metadata_v0_1
        self.selected_layout_path = None
        self.composite_paths = {}  # Will store template_index -> composite_path mapping
        self._setup_ui()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)

        title_label = QLabel("Choose a layout for your photo")
        title_font = QFont()
        title_font.setPointSize(36)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("color: #d42c2c; margin: 20px;")

        main_layout.addWidget(title_label)

        # Grid for images
        grid_widget = QWidget()
        grid_widget.setAutoFillBackground(False)
        grid_layout = QGridLayout(grid_widget)

        for i, path in enumerate(self.templates_path):
            row = i // 2
            col = i % 2

            # Container for each layout option
            container = QWidget()
            container_layout = QVBoxLayout(container)
            container_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            container_layout.setSpacing(5)

            # Image label
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
            label.clicked.connect(self._on_select_layout)

            # Store label in dictionary for later updates
            self.layout_labels[path] = label

            # Text label for display info
            if path in self.layout_metadata:
                meta = self.layout_metadata[path]
                info_label = QLabel(f"{meta['display_text']}")
            else:
                info_label = QLabel(f"Layout {i + 1}")

            info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            info_label.setStyleSheet(
                "font-size: 14px; color: #2d5a2d; margin-top: 10px;"
            )

            if path == self.selected_layout_path:
                label.setStyleSheet("background-color: rgba(45, 90, 45, 0.3)")
                label.is_selected = True
            else:
                label.setStyleSheet("background-color: transparent")

            container_layout.addWidget(label)
            container_layout.addWidget(info_label)
            grid_layout.addWidget(container, row, col)

        self.number_of_photos_selector_widget = RangeSelectorWidget(
            initial_value=2, min_value=1, max_value=4, label_text="Number of photos"
        )

        # Create bottom grid layout for proper centering
        # Grid structure: [stretch column] [center widget] [stretch column] [button]
        bottom_layout = QGridLayout()
        bottom_layout.setContentsMargins(
            10, 10, 10, 10
        )  # Reduced margins to prevent cutting off
        bottom_layout.setVerticalSpacing(0)

        confirm_button = QPushButton("Confirm")
        confirm_button.setFont(QFont("Arial", 18))
        confirm_button.setStyleSheet(buttons_css)
        confirm_button.clicked.connect(self._on_confirm_button)
        confirm_button.setEnabled(True)

        # Add widgets to grid:
        # Row 0, Column 1: centered selector widget
        # Row 0, Column 2: right-aligned button
        bottom_layout.addWidget(
            self.number_of_photos_selector_widget,
            0,
            1,
            Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter,
        )
        bottom_layout.addWidget(
            confirm_button,
            0,
            2,
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
        )

        # Set column stretch factors:
        # Column 0 (left stretch): 1
        # Column 1 (selector): 0 (no stretch, natural size)
        # Column 2 (button): 1 (takes remaining space, button aligned right)
        bottom_layout.setColumnStretch(0, 1)
        bottom_layout.setColumnStretch(1, 0)
        bottom_layout.setColumnStretch(2, 1)

        main_layout.addWidget(grid_widget)
        main_layout.addStretch()
        main_layout.addLayout(bottom_layout)

    def on_exit(self):
        pass

    def on_enter(self):
        """Generate composites for all templates and update the display."""
        # Generate composites if we have a session manager
        if self.session_manager:
            session_folder = self.session_manager.get_current_session_folder
            if session_folder:
                # Get photos from the current session
                photo_paths = get_session_photos(session_folder)

                if photo_paths:
                    # Generate composites for all templates
                    print(f"Generating composites for all templates using {len(photo_paths)} photos...")
                    self.composite_paths = generate_all_composites(
                        photo_paths=photo_paths,
                        output_dir=session_folder,
                        output_prefix="preview_composite"
                    )

                    # Update the display with generated composites
                    self._update_composite_previews()

        self._on_select_layout(None)

    def _update_composite_previews(self):
        """Update the layout preview images with generated composites."""
        # Map template paths to template indices
        template_path_to_index = {
            path: meta["index"]
            for path, meta in self.layout_metadata.items()
        }

        # Update each label with its corresponding composite
        for template_path, label in self.layout_labels.items():
            template_index = template_path_to_index.get(template_path)
            if template_index is not None and template_index in self.composite_paths:
                composite_path = self.composite_paths[template_index]
                pixmap = QPixmap(composite_path)
                scaled_pixmap = pixmap.scaled(
                    label.size(),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
                label.setPixmap(scaled_pixmap)
                print(f"Updated template {template_index} preview with {composite_path}")

    def _on_select_layout(self, value):
        """
        Update all labels to reflect the new selection
        """
        print(f"Changed layout: {value}")
        self.selected_layout_path = value
        for path, lbl in self.layout_labels.items():
            if path == value:
                lbl.setStyleSheet("background-color: rgba(45, 90, 45, 0.3)")
            else:
                lbl.setStyleSheet("background-color: transparent")

    def _on_confirm_button(self):
        if self.selected_layout_path is None:
            raise ValueError("No layout selected")
        self.number_of_photos = self.number_of_photos_selector_widget.current_value

        # Get the template index from metadata
        template_index = self.layout_metadata[self.selected_layout_path]["index"]

        # Get the template number of photos from metadata
        template_number_of_photos = self.layout_metadata[self.selected_layout_path][
            "num_photos"
        ]

        self.layout_selected.emit(
            self.selected_layout_path,
            self.number_of_photos,
            template_index,
            template_number_of_photos,
        )
