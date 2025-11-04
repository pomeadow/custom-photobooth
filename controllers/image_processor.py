from typing import List
from PySide6.QtCore import QObject, Qt
from PySide6.QtGui import QImage, QPixmap
import cv2 as cv
import numpy as np


class ImageProcessor(QObject):
    """Handles image processing operations for the photobooth."""

    def __init__(self) -> None:
        super().__init__()
        self._overlay_cache = {}
        self._current_overlay_image = None

    def load_overlay(self, overlay_path: str):
        """Load an overlay image with caching."""
        try:
            path_str = str(overlay_path)
            # Check cache first
            if path_str in self._overlay_cache:
                self._current_overlay_image = self._overlay_cache[path_str]
                return True

            self._current_overlay_image = cv.imread(overlay_path, cv.IMREAD_UNCHANGED)
            self._overlay_cache[path_str] = self._current_overlay_image
            return True
        except Exception as e:
            print(f"Could not load overlay image: {e}")
            return False

    def apply_overlay(self, frame, foreground_overlay, flip_horizontal: bool):
        """
        Apply overlay to frame with alpha blending.

        Args:
            frame: Background image (BGR format)
            foreground_overlay: RGBA overlay image (uses current if None)
            flip_horizontal: Whether to flip the result for mirror effect

        Returns:
            Processed frame with overlay applied
        """
        background_img = frame
        if background_img is None:
            raise ValueError("Could not read the background image")
        if foreground_overlay is None:
            foreground_overlay = self._current_overlay_image

        if foreground_overlay is None:
            return cv.flip(frame, 1) if flip_horizontal else frame.copy()

        result = background_img.copy()
        # Get background dimensions first
        bh, bw = result.shape[:2]

        # Resize foreground overlay to match background dimensions
        resized_foreground_overlay = cv.resize(foreground_overlay, (bw, bh))

        # Get dimensions of resized overlay
        oh, ow, oc = resized_foreground_overlay.shape

        # Define ROI on background (example: top-left corner)
        x_offset = 0
        y_offset = 0

        # # using opencv alone
        # grayscaled_overlay = cv.cvtColor(foreground_overlay, cv.COLOR_BGR2GRAY)
        # ret, mask = cv.threshold(grayscaled_overlay, 10, 255, cv.THRESH_BINARY)
        # mask_inv = cv.bitwise_not(mask)
        # # Now black-out the area of logo in ROI
        # roi = foreground_overlay[:oh, :ow]
        # img1_bg = cv.bitwise_and(roi,roi,mask = mask_inv)

        # Extract alpha channel and color channels from overlay
        alpha_channel = (
            resized_foreground_overlay[:, :, 3] / 255.0
        )  # Single channel (1280, 1280)
        bgr_channels = resized_foreground_overlay[
            :, :, :3
        ]  # RGB channels (1280, 1280, 3)
        # print(alpha_channel.dtype)

        # Create inverse alpha mask for background
        inverse_alpha = 1.0 - alpha_channel

        # Blend the images/ combine the foreground and background within the ROI
        # formula: output_pixel = (foreground_pixel * alpha) + (background_pixel * (1 - alpha))
        # Apply alpha blending to the BGR channels
        for c in range(0, 3):
            result[y_offset : y_offset + oh, x_offset : x_offset + ow, c] = (
                bgr_channels[:, :, c] * alpha_channel
            ) + (
                result[y_offset : y_offset + oh, x_offset : x_offset + ow, c]
                * inverse_alpha
            )

        if flip_horizontal:
            return cv.flip(result, 1)

        return result

    @staticmethod
    def frame_to_qpixmap(
        frame: np.ndarray, target_size: tuple = None, keep_aspect: bool = True
    ) -> QPixmap:
        """
        Convert OpenCV frame to QPixmap for Qt display.

        Args:
            frame: OpenCV frame (BGR format)
            target_size: Optional (width, height) tuple for scaling
            keep_aspect: Whether to maintain aspect ratio when scaling
        """
        # Convert BGR to RGB
        rgb_frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
        h, w, ch = rgb_frame.shape
        bytes_per_line = ch * w

        # Create QImage
        qt_image = QImage(
            rgb_frame.data, w, h, bytes_per_line, QImage.Format.Format_RGB888
        )

        pixmap = QPixmap.fromImage(qt_image)

        # Scale if target size specified
        if target_size:
            aspect_mode = Qt.KeepAspectRatio if keep_aspect else Qt.IgnoreAspectRatio
            pixmap = pixmap.scaled(
                target_size[0], target_size[1], aspect_mode, Qt.SmoothTransformation
            )

        return pixmap

    def clear_cache(self):
        """Clear the overlay cache to free memory."""
        self._overlay_cache.clear()

    def create_photo_composite(
        self, photo_paths: List[str], template_path: str, template_index: int
    ) -> np.ndarray:
        """
        Create a composite image by placing photos into a template layout.

        Args:
            photo_paths: List of paths to photos to insert
            template_path: Path to the template image
            template_index: Index of the template (0-3)

        Returns:
            Composite image as numpy array (BGR format)
        """
        # Load template
        template = cv.imread(template_path)
        if template is None:
            raise ValueError(f"Could not load template: {template_path}")

        # Get template dimensions
        template_height, template_width = template.shape[:2]

        # Define photo slot positions for each template (x, y, width, height)
        # These are approximate positions based on the visual inspection of templates
        template_configs = {
            0: {  # template1.png - 1x3 horizontal layout
                "slots": [
                    (35, 30, 305, 305),  # Left slot
                    (355, 30, 305, 305),  # Middle slot
                    (985, 30, 305, 305),  # Right slot
                ],
                "num_photos": 3,
            },
            1: {  # template2.png - 1x3 horizontal layout (different sizing)
                "slots": [
                    (50, 35, 350, 310),  # Left slot
                    (460, 35, 420, 310),  # Middle slot
                    (900, 35, 360, 310),  # Right slot
                ],
                "num_photos": 3,
            },
            2: {  # template3.png - 2x3 grid layout
                "slots": [
                    (45, 50, 360, 280),  # Top-left
                    (470, 50, 360, 280),  # Top-middle
                    (870, 50, 360, 280),  # Top-right
                    (45, 385, 360, 280),  # Bottom-left
                    (470, 385, 360, 280),  # Bottom-middle
                    (870, 385, 360, 280),  # Bottom-right
                ],
                "num_photos": 6,
            },
            3: {  # template4.png - 2x2 grid layout
                "slots": [
                    (50, 50, 570, 300),  # Top-left
                    (675, 50, 570, 300),  # Top-right
                    (50, 385, 570, 300),  # Bottom-left
                    (675, 385, 570, 300),  # Bottom-right
                ],
                "num_photos": 4,
            },
        }

        if template_index not in template_configs:
            raise ValueError(f"Invalid template index: {template_index}")

        config = template_configs[template_index]
        slots = config["slots"]
        num_photos_needed = min(len(photo_paths), len(slots))

        # Create a copy of the template to work with
        result = template.copy()

        # Insert each photo into its slot
        for i in range(num_photos_needed):
            photo_path = photo_paths[i]
            slot_x, slot_y, slot_w, slot_h = slots[i]

            # Load photo
            photo = cv.imread(photo_path)
            if photo is None:
                print(f"Warning: Could not load photo {photo_path}")
                continue

            # Resize photo to fit slot while maintaining aspect ratio
            photo_resized = self._resize_photo_to_slot(photo, slot_w, slot_h)

            # Calculate centering offsets if photo is smaller than slot
            ph, pw = photo_resized.shape[:2]
            offset_x = (slot_w - pw) // 2
            offset_y = (slot_h - ph) // 2

            # Place photo in the slot
            final_x = slot_x + offset_x
            final_y = slot_y + offset_y

            try:
                result[final_y : final_y + ph, final_x : final_x + pw] = photo_resized
            except Exception as e:
                print(f"Error placing photo {i}: {e}")

        return result

    def _resize_photo_to_slot(
        self, photo: np.ndarray, slot_width: int, slot_height: int
    ) -> np.ndarray:
        """
        Resize photo to fit within slot dimensions while maintaining aspect ratio.

        Args:
            photo: Input photo (BGR format)
            slot_width: Target slot width
            slot_height: Target slot height

        Returns:
            Resized photo
        """
        h, w = photo.shape[:2]
        aspect_ratio = w / h
        slot_aspect_ratio = slot_width / slot_height

        # Determine scaling to fill the slot (crop if necessary)
        if aspect_ratio > slot_aspect_ratio:
            # Photo is wider than slot - fit to height
            new_h = slot_height
            new_w = int(new_h * aspect_ratio)
        else:
            # Photo is taller than slot - fit to width
            new_w = slot_width
            new_h = int(new_w / aspect_ratio)

        # Resize photo
        resized = cv.resize(photo, (new_w, new_h), interpolation=cv.INTER_LANCZOS4)

        # If resized photo is larger than slot, crop it
        if new_w > slot_width or new_h > slot_height:
            # Center crop
            start_x = (new_w - slot_width) // 2
            start_y = (new_h - slot_height) // 2
            resized = resized[start_y : start_y + slot_height, start_x : start_x + slot_width]

        return resized
