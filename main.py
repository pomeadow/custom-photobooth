# import datetime
# import dis
# import os
# import sys
# from components.range_selector import RangeSelectorWidget
# import cv2 as cv

# from PySide6.QtWidgets import (
#     QApplication,
#     QMainWindow,
#     QWidget,
#     QVBoxLayout,
#     QHBoxLayout,
#     QPushButton,
#     QLabel,
#     QSpinBox,
#     QComboBox,
#     QStackedWidget,
#     QGridLayout,
# )
# from PySide6.QtCore import QTimer, Qt, QRect, QEventLoop
# from PySide6.QtGui import QImage, QPixmap, QFont

# from components.clickable_label import ClickableLabel
# from utils import get_png_file_paths


# # 1) Pick the number of pax taking photos/ how many photos you want
# # set n number for the photos
# # 2) Select a frame
# # Show interactable preset frames
# # OR people can select while taking
# ### Main app ###


# class PhotoboothGUI(QMainWindow):
#     def __init__(self):
#         super().__init__()
#         self.setWindowTitle("Christmas Photobooth")
#         self.setGeometry(100, 100, 800, 600)
#         self.setMinimumSize(
#             800, 600
#         )  # Set minimum window size to prevent cutting off content

#         # Initialize camera
#         self.cam = None
#         self.overlay_image = None
#         self.timer = QTimer()
#         self.timer.timeout.connect(self.update_frame)

#         self.DEFAULT_OVERLAY_PATH = "/Users/chewyan/Documents/carrot-tp.png"
#         self.number_of_photos = 1
#         self.current_session_folder = None
#         self.selected_layout_path = None
#         self.setup_ui()
#         self.load_overlay(self.DEFAULT_OVERLAY_PATH)

#     def setup_ui(self):
#         self.stacked_widget.addWidget(camera_widget)

#     def create_selection_screen(self):
#         selection_widget = QWidget()
#         selection_widget.setStyleSheet("background-color: #ffffff;")
#         self.setup_selection_ui(selection_widget)
#         self.stacked_widget.addWidget(selection_widget)

#     def create_print_screen(self):
#         print_widget = QWidget()
#         print_widget.setStyleSheet("background-color: #f0f8f0;")
#         self.setup_print_ui(print_widget)
#         self.stacked_widget.addWidget(print_widget)

#     def show_print_screen(self):
#         self.stacked_widget.setCurrentIndex(4)

#     def show_selection_screen(self):
#         self.stop_camera()

#         self.stacked_widget.setCurrentIndex(3)

#     def show_camera_screen(self):
#         # Create new session folder
#         now = datetime.datetime.now()
#         folder_name = now.strftime("session_%Y%m%d_%H%M%S")
#         self.current_session_folder = os.path.join(os.getcwd(), folder_name)
#         os.makedirs(self.current_session_folder, exist_ok=True)
#         print(f"Created session folder: {self.current_session_folder}")

#         self.stacked_widget.setCurrentIndex(2)
#         # Automatically start the camera when entering camera screen
#         self.start_camera()

#     def show_select_layout_screen(self):
#         self.stacked_widget.setCurrentIndex(1)

#     def show_title_screen(self):
#         # Stop camera if running before going back
#         self.stop_camera()
#         self.stacked_widget.setCurrentIndex(0)

#     def setup_select_layout(self, parent_widget):
#         def on_number_of_photos_selector(value):
#             print(f"Changed value: {value}")
#             self.number_of_photos = value

#         def selected_layout(value):
#             print(f"Changed layout: {value}")
#             self.selected_layout_path = value
#             # Update all labels to reflect the new selection
#             for path, lbl in layout_labels.items():
#                 if path == value:
#                     lbl.setStyleSheet("background-color: rgba(45, 90, 45, 0.3)")
#                 else:
#                     lbl.setStyleSheet("background-color: transparent")

#         # Layout metadata: {path: {index, num_photos, display_text}}
#         templates_path = get_png_file_paths("./resources/templates/")
#         layout_labels = {}  # Dictionary to track all layout labels
#         layout_metadata = {
#             templates_path[0]: {"index": 0, "num_photos": 4, "display_text": "2 x 2"},
#             templates_path[1]: {"index": 1, "num_photos": 6, "display_text": "2 x 3"},
#             templates_path[2]: {"index": 2, "num_photos": 3, "display_text": "1 x 3"},
#             templates_path[3]: {"index": 3, "num_photos": 4, "display_text": "1 x 4"},
#             # Add more as needed
#         }

#         main_layout = QVBoxLayout(parent_widget)
#         title_label = QLabel("Choose a layout for your photo <3")
#         title_font = QFont()
#         title_font.setPointSize(36)
#         title_font.setBold(True)
#         title_label.setFont(title_font)
#         title_label.setAlignment(Qt.AlignCenter)
#         title_label.setStyleSheet("color: #d42c2c; margin: 20px;")

#         main_layout.addWidget(title_label)

#         # Grid for images
#         grid_widget = QWidget()
#         grid_layout = QGridLayout(grid_widget)

#         for i, path in enumerate(templates_path):
#             row = i // 2
#             col = i % 2

#             # Container for each layout option
#             container = QWidget()
#             container_layout = QVBoxLayout(container)
#             container_layout.setAlignment(Qt.AlignCenter)
#             container_layout.setSpacing(5)

#             # Image label
#             label = ClickableLabel(path)
#             label.setFixedSize(300, 225)
#             label.setAlignment(Qt.AlignCenter)

#             pixmap = QPixmap(path)
#             scaled_pixmap = pixmap.scaled(
#                 label.size(),
#                 Qt.KeepAspectRatio,
#                 Qt.SmoothTransformation,
#             )
#             label.setPixmap(scaled_pixmap)
#             label.clicked.connect(selected_layout)

#             # Store label in dictionary for later updates
#             layout_labels[path] = label

#             # Text label for display info
#             if path in layout_metadata:
#                 meta = layout_metadata[path]
#                 info_label = QLabel(f"{meta['display_text']}")
#             else:
#                 info_label = QLabel(f"Layout {i + 1}")

#             info_label.setAlignment(Qt.AlignCenter)
#             info_label.setStyleSheet(
#                 "font-size: 14px; color: #2d5a2d; margin-top: 10px;"
#             )

#             if path == self.selected_layout_path:
#                 label.setStyleSheet("background-color: rgba(45, 90, 45, 0.3)")
#                 label.is_selected = True
#             else:
#                 label.setStyleSheet("background-color: transparent")

#             container_layout.addWidget(label)
#             container_layout.addWidget(info_label)
#             grid_layout.addWidget(container, row, col)

#         number_of_photos_selector_widget = RangeSelectorWidget(
#             initial_value=1, min_value=1, max_value=4, label_text="Number of photos"
#         )

#         # Create bottom grid layout for proper centering
#         # Grid structure: [stretch column] [center widget] [stretch column] [button]
#         bottom_layout = QGridLayout()
#         bottom_layout.setContentsMargins(
#             10, 10, 10, 10
#         )  # Reduced margins to prevent cutting off
#         bottom_layout.setVerticalSpacing(0)

#         next_button = QPushButton("Confirm")
#         next_button.setFont(QFont("Arial", 18))
#         next_button.setStyleSheet(buttons_css)
#         next_button.clicked.connect(self.show_camera_screen)
#         next_button.setEnabled(True)

#         # Add widgets to grid:
#         # Row 0, Column 1: centered selector widget
#         # Row 0, Column 2: right-aligned button
#         bottom_layout.addWidget(
#             number_of_photos_selector_widget, 0, 1, Qt.AlignCenter | Qt.AlignVCenter
#         )
#         bottom_layout.addWidget(next_button, 0, 2, Qt.AlignRight | Qt.AlignVCenter)

#         # Set column stretch factors:
#         # Column 0 (left stretch): 1
#         # Column 1 (selector): 0 (no stretch, natural size)
#         # Column 2 (button): 1 (takes remaining space, button aligned right)
#         bottom_layout.setColumnStretch(0, 1)
#         bottom_layout.setColumnStretch(1, 0)
#         bottom_layout.setColumnStretch(2, 1)

#         main_layout.addWidget(grid_widget)
#         main_layout.addStretch()
#         main_layout.addLayout(bottom_layout)

#     def setup_selection_ui(self, parent_widget):
#         main_layout = QVBoxLayout(parent_widget)

#         self.current_page = 0
#         self.images_per_page = 4
#         self.selected_photos = []  # Track selected image paths
#         self.selected_labels = {}  # Track labels by path for styling
#         self.all_image_paths = []  # Will be populated when showing selection screen

#         # Navigation buttons
#         top_nav_layout = QHBoxLayout()
#         self.prev_button = QPushButton("← Previous")
#         self.prev_button.clicked.connect(self.show_previous_images)
#         self.prev_button.setStyleSheet(buttons_css)
#         self.next_button_nav = QPushButton("Next →")
#         self.next_button_nav.clicked.connect(self.show_next_images)
#         self.next_button_nav.setStyleSheet(buttons_css)

#         self.page_label = QLabel()
#         self.page_label.setAlignment(Qt.AlignCenter)

#         top_nav_layout.addWidget(self.prev_button)
#         top_nav_layout.addWidget(self.page_label)
#         top_nav_layout.addWidget(self.next_button_nav)

#         bottom_nav_layout = QHBoxLayout()
#         print_button = QPushButton("Print!")
#         print_button.clicked.connect(self.show_print_screen)
#         print_button.setStyleSheet(buttons_css)
#         bottom_nav_layout.addWidget(print_button)

#         # Grid for images
#         self.grid_widget = QWidget()
#         self.grid_layout = QGridLayout(self.grid_widget)

#         main_layout.addLayout(top_nav_layout)
#         main_layout.addWidget(self.grid_widget)
#         main_layout.addLayout(bottom_nav_layout)

#         # Load first page
#         self.update_image_grid()

#     def setup_print_ui(self, parent_widget):
#         window = QWidget()
#         layout = QHBoxLayout(parent_widget)
#         label = QLabel()
#         font = QFont()
#         font.setPointSize(16)
#         label.setFont(font)
#         label.setAlignment(Qt.AlignCenter)
#         label.setStyleSheet("color: #2d5a2d; margin: 20px;")
#         label.setText("Printing photos")

#         # TODO generate qr??

#         layout.addWidget(label)
#         window.setLayout(layout)

#     def flash(self):
#         # Store original image
#         original_pixmap = self.camera_label.pixmap()
#         # Flash white
#         white_pixmap = QPixmap(self.camera_label.size())
#         white_pixmap.fill(Qt.white)
#         self.camera_label.setPixmap(white_pixmap)
#         # Use QTimer to restore after 200ms
#         QTimer.singleShot(
#             400,
#             lambda: self.camera_label.setPixmap(original_pixmap)
#             if original_pixmap
#             else None,
#         )
#         loop = QEventLoop()
#         QTimer.singleShot(400, loop.quit)
#         loop.exec()


import sys
from PySide6.QtWidgets import QApplication
from ui.main_window import PhotoboothGUI

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PhotoboothGUI()
    window.show()
    sys.exit(app.exec())
