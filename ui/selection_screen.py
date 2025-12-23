import os
from turtle import st
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QIcon, QPixmap
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
from utils.utils import clear_layout, get_png_file_paths
from ui.styles import buttons_css, widget_0_css, widget_50_css
from utils.generate_preview_strips import generate_preview_strip
from config.load_metadata import templates_config_dict

from PySide6.QtWidgets import QSizePolicy


class SelectionScreen(BaseScreen):
    """
    Previews photos and allows user to select up to 4 photos

    Emits signal
        layout_path: str,
        num_photos: int,
        preview_path: str
    """

    layout_selected = Signal(str, int, str)

    def __init__(self, session_manager: SessionManager, parent=None):
        super().__init__(parent)
        self.session_manager = session_manager
        self.current_session_folder = None
        self._setup_ui()

    def on_enter(self):
        print(f"Widget size on enter: {self.size()}")
        self.current_session_folder = self.session_manager.get_current_session_folder
        # Load images from current session folder
        if self.current_session_folder and os.path.exists(self.current_session_folder):
            all_pngs = get_png_file_paths(self.current_session_folder)
            # Filter out preview strips and composite files, keep only photos
            self.all_image_paths = [
                p
                for p in all_pngs
                if p and "preview_strip" not in p and "composite" not in p
            ]
            print(
                f"Loaded {len(self.all_image_paths)} images from {self.current_session_folder}"
            )
        else:
            self.all_image_paths = []
            print("No session folder found")
        self.current_page = 0
        self._cleanup_old_previews()
        self._update_preview_strip()
        self.update_image_grid()

    def reset(self):
        self.selected_photos = []
        self.selected_labels = {}
        self.selected_template_path = None

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)

        # Debug: Print widget size (might not be final yet)
        print(f"Widget size at setup: {self.size()}")

        # Get actual screen size
        from PySide6.QtGui import QGuiApplication

        screen = QGuiApplication.primaryScreen()
        screen_geometry = screen.geometry()
        print(f"Screen size: {screen_geometry.width()}x{screen_geometry.height()}")

        self.current_page = 0
        self.images_per_page = 4
        self.selected_photos = []  # Track selected image paths
        self.selected_labels = {}  # Track labels by path for styling
        self.all_image_paths = []  # Will be populated when showing selection screen
        self.preview_strip_paths = {}  # Store preview strip paths {2: path, 3: path}
        self.selected_template_path = None  # Track currently selected template

        # Navigation buttons
        top_nav_layout = QHBoxLayout()
        top_widget = QWidget()
        top_widget.setLayout(top_nav_layout)
        top_widget.setVisible(False)

        self.page_label = QLabel()
        self.page_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        top_nav_layout.addWidget(self.page_label)

        middle_layout = QHBoxLayout()

        # Preview area for strips
        self.preview_widget = QWidget()
        self.preview_layout = QVBoxLayout(self.preview_widget)
        self.preview_widget.setStyleSheet(widget_50_css)
        self.preview_label = QLabel("Preview")
        self.preview_label.setStyleSheet(
            "font-size: 24px; font-weight: bold; color: #C9A961; font-family: Impact"
        )
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        self.preview_strip_label = QLabel()
        self.preview_strip_label.setFixedSize(480, 640)
        self.preview_strip_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.preview_strip_label.setVisible(False)

        self.preview_layout.addWidget(self.preview_label)
        self.preview_layout.addWidget(self.preview_strip_label)
        self.preview_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        # Grid for images
        self.grid_widget = QWidget()
        self.grid_layout = QGridLayout(self.grid_widget)

        middle_layout.addWidget(self.preview_widget)
        middle_layout.addWidget(self.grid_widget)

        self.template_selection_labels = QHBoxLayout()
        self.template_selection_widget = QWidget()
        self.template_selection_widget.setMinimumHeight(60)  # reserves vertical space
        self.template_selection_widget.setLayout(self.template_selection_labels)
        self.template_selection_widget.setVisible(False)
        self.template_selection_widget.setStyleSheet(widget_50_css)

        bottom_nav_layout = QHBoxLayout()
        bottom_widget = QWidget()
        bottom_widget.setLayout(bottom_nav_layout)
        bottom_widget.setMaximumHeight(150)
        bottom_left_layout = QVBoxLayout()
        bottom_left_layout.addWidget(self.template_selection_widget)

        label_instructions = QLabel("Select 2 or all 4 photos")
        label_instructions.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label_instructions.setSizePolicy(
            QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Fixed
        )
        label_instructions.setStyleSheet(
            """
            font-size: 32px;
            font-weight: bold;
            color: #C9A961;
            font-family: 'Impact', sans-serif;
            border-radius: 75px;       
        """
            + widget_50_css
        )
        bottom_left_layout.addWidget(label_instructions)
        bottom_nav_layout.addLayout(bottom_left_layout, 2)

        bottom_right_layout = QVBoxLayout()
        bottom_right_widget = QWidget()
        bottom_right_widget.setLayout(bottom_right_layout)
        bottom_nav_layout.addStretch()
        bottom_nav_layout.addWidget(bottom_right_widget, 1)

        start_over_button = QPushButton("Start Over")
        start_over_button.setFont(QFont("Impact"))
        start_over_button.setStyleSheet(
            buttons_css
            + """QPushButton {
                padding: 10px 20px;
                margin: 5px;
            }"""
        )
        start_over_button.clicked.connect(lambda: self.navigate_to.emit("title"))

        self.print_button = QPushButton("Next")
        self.print_button.setFont(QFont("Impact"))
        self.print_button.clicked.connect(lambda: self.navigate_to.emit("print"))
        self.print_button.setStyleSheet(
            buttons_css
            + """QPushButton {
                padding: 10px 20px;
                margin: 5px;
            }"""
        )
        self.print_button.setEnabled(False)
        bottom_right_layout.addWidget(start_over_button)
        bottom_right_layout.addWidget(self.print_button)

        main_layout.addWidget(top_widget)
        main_layout.addLayout(middle_layout)
        main_layout.addWidget(bottom_widget)

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
            # Skip empty or invalid paths
            if not path or not os.path.exists(path):
                continue

            row = i // cols
            col = i % cols

            label = ClickableLabel(path)
            label.setFixedSize(300, 225)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setStyleSheet(widget_0_css)

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
                label.setStyleSheet(widget_0_css + "border: 5px solid #C9A961;")
                label.is_selected = True
            else:
                label.setStyleSheet(widget_0_css + "border: none;")

            self.selected_labels[path] = label
            self.grid_layout.addWidget(label, row, col)

    def _on_label_clicked(self, image_path):
        """Handle image selection/deselection"""
        if image_path in self.selected_photos:
            # Deselect
            self.selected_photos.remove(image_path)
            if image_path in self.selected_labels:
                self.selected_labels[image_path].setStyleSheet(
                    widget_0_css + "border: none;"
                )
                self.selected_labels[image_path].is_selected = False
        else:
            # Select
            self.selected_photos.append(image_path)
            if image_path in self.selected_labels:
                self.selected_labels[image_path].setStyleSheet(
                    "border: 5px solid #C9A961;" + widget_0_css
                )
                self.selected_labels[image_path].is_selected = True

        print(f"Selected photos: {len(self.selected_photos)} - {self.selected_photos}")

        # Show color selection buttons
        self._update_color_selection_buttons(len(self.selected_photos))
        self.template_selection_widget.setVisible(True)
        # Update preview strip when 2 or 4 photos are selected
        self._update_preview_strip()

    def _update_preview_strip(self):
        """Generate and display preview strip based on number of selected photos and template."""
        num_selected = len(self.selected_photos)

        filtered_templates = self._get_suitable_templates(num_selected)

        if self.current_session_folder:
            if len(filtered_templates) == 0:
                print(f"No suitable templates found for {num_selected} photos")
                self._hide_preview_strip()
                self.selected_template_path = None
                self.template_selection_widget.setVisible(False)
                return

            # Default to first template if multiple available and selected_template_path not set
            if self.selected_template_path is None:
                self._on_color_selection_label_clicked(
                    list(filtered_templates.keys())[0]
                )

            # Generate preview strip
            strip_path = generate_preview_strip(
                photo_paths=self.selected_photos,
                num_photos=num_selected,
                template_path=self.selected_template_path,
                output_dir=self.current_session_folder,
                output_prefix="preview_strip",
            )

            if strip_path and os.path.exists(strip_path):
                # Store generated preview strip
                self.preview_strip_paths[num_selected] = strip_path
                # Load and display the preview strip
                pixmap = QPixmap(strip_path)
                # Scale to reasonable size (e.g., 600px wide)
                scaled_pixmap = pixmap.scaled(
                    self.preview_strip_label.size(),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
                self.preview_strip_label.setPixmap(scaled_pixmap)
                self.preview_strip_label.setVisible(True)
                self.preview_label.setVisible(True)
                print(f"Updated preview strip with {num_selected} photos: {strip_path}")
                print(f"Selected template: path={self.selected_template_path}")
                self.layout_selected.emit(
                    self.selected_template_path,
                    num_selected,
                    strip_path,
                )
                self.print_button.setEnabled(True)

            else:
                print(f"Failed to generate preview strip for {num_selected} photos")
                self._hide_preview_strip()
        else:
            # Hide preview if not 2 or 4 photos selected
            self._hide_preview_strip()
            self.selected_template_path = None
            self.template_selection_widget.setVisible(False)

    def _update_color_selection_buttons(self, num_photos: int):
        """Update the color selection buttons based on number of photos."""
        if num_photos not in [2, 4]:
            return

        try:
            # Clear existing buttons
            clear_layout(self.template_selection_labels)
        except:
            pass  # in case there are no widgets yet

        filtered_templates = self._get_suitable_templates(num_photos)

        for i in filtered_templates:
            template_selection_label = ClickableLabel(i)
            template_selection_label.setFixedSize(40, 40)
            template_selection_label.setObjectName(i)
            rgb = templates_config_dict[i]["color"]
            template_selection_label.setStyleSheet(f"""background-color: rgb({rgb[0]}, {rgb[1]}, {rgb[2]});
                                                    border-radius: {40 // 2}px;""")
            template_selection_label.clicked.connect(
                self._on_color_selection_label_clicked
            )
            self.template_selection_labels.addWidget(template_selection_label)
            if i != len(templates_config_dict) - 1:
                self.template_selection_labels.addSpacing(20)

    def _get_suitable_templates(self, num_photos) -> dict[str, dict]:
        """
        Get templates suitable for the given number of photos.
        """
        filtered_templates = {
            k: v
            for k, v in templates_config_dict.items()
            if v["num_photos"] == num_photos * 2
        }
        return filtered_templates

    def _on_color_selection_label_clicked(self, color_label):
        """Handle template selection/deselection"""
        if color_label == self.selected_template_path:
            # No change when clicking the same template
            return
        else:
            # Clear previously selected if available and Select new
            if self.selected_template_path:
                previous_widget = self.template_selection_widget.findChild(
                    ClickableLabel, self.selected_template_path
                )
                rgb = templates_config_dict[self.selected_template_path]["color"]
                # TODO ensure that previous_widget is not None
                previous_widget.setStyleSheet(f"""background-color: rgb({rgb[0]}, 
                                                                        {rgb[1]}, 
                                                                        {rgb[2]});
                                                border-radius: {40 // 2}px;""")
                previous_widget.is_selected = False

            self.selected_template_path = color_label
            selected_widget = self.template_selection_widget.findChild(
                ClickableLabel, color_label
            )
            rgb = templates_config_dict[self.selected_template_path]["color"]
            # TODO ensure that selected_widget is not None
            selected_widget.setStyleSheet(f"""background-color: rgb({rgb[0]}, 
                                                                        {rgb[1]}, 
                                                                        {rgb[2]});
                                                border-radius: {40 // 2}px;
                                                border: 5px solid #C9A961;""")
            selected_widget.is_selected = True
            # Update preview strip when new template selected
            self._update_preview_strip()

    def _hide_preview_strip(self):
        """Hide the preview strip."""
        self.preview_strip_label.setVisible(False)

    def _cleanup_old_previews(self):
        try:
            for p in self.preview_strip_paths.values():
                os.remove(p)
        except:
            pass  # expect that the path might not always exists
