from re import I
from typing import List, Tuple
from PySide6.QtCore import QObject, Qt
from PySide6.QtGui import QImage, QPixmap
import cv2 as cv
import numpy as np
from PIL import Image
from config.load_metadata import templates_config_dict


class ImageProcessor(QObject):
    """Handles image processing operations for the photobooth."""

    def __init__(self) -> None:
        super().__init__()
        self._overlay_cache = {}
        self._current_overlay_image = None
        self._composite_dpi = None  # Store DPI for the composite

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
            aspect_mode = (
                Qt.AspectRatioMode.KeepAspectRatio
                if keep_aspect
                else Qt.AspectRatioMode.IgnoreAspectRatio
            )
            pixmap = pixmap.scaled(
                target_size[0],
                target_size[1],
                aspect_mode,
                Qt.TransformationMode.SmoothTransformation,
            )

        return pixmap

    def clear_cache(self):
        """Clear the overlay cache to free memory."""
        self._overlay_cache.clear()

    @staticmethod
    def _get_image_dpi(image_path: str) -> Tuple[int, int]:
        """
        Get DPI from an image file.

        Args:
            image_path: Path to the image file

        Returns:
            Tuple of (dpi_x, dpi_y). Defaults to (300, 300) if not found.
        """
        try:
            with Image.open(image_path) as img:
                dpi = img.info.get("dpi")
                if dpi:
                    return tuple(int(d) for d in dpi)
        except Exception as e:
            print(f"Could not read DPI from {image_path}: {e}")

        # Default to 300 DPI for printing
        return (300, 300)

    def get_composite_dpi(self) -> Tuple[int, int]:
        """Get the DPI of the last created composite."""
        return self._composite_dpi if self._composite_dpi else (300, 300)

    def create_photo_composite(
        self, photo_paths: List[str], template_path: str
    ) -> np.ndarray:
        """
        Create a composite image by placing photos into a template layout.

        Args:
            photo_paths: List of paths to photos to insert
            template_path: Path to the template image

        Returns:
            Composite image as numpy array (BGR format)
        """
        # Get DPI from the first photo (all should have same DPI from camera)
        if photo_paths:
            self._composite_dpi = self._get_image_dpi(photo_paths[0])
            print(f"Using DPI from photos: {self._composite_dpi}")

        # Load template
        template = cv.imread(template_path)
        if template is None:
            raise ValueError(f"Could not load template: {template_path}")

        # Get template dimensions
        template_height, template_width = template.shape[:2]

        # Create a copy of the template to work with
        result = template.copy()

        # Photo slot positions for each template (x, y, width, height)
        slots = templates_config_dict[template_path]["slots"]

        # Insert each photo into its slot
        for i in range(len(slots)):
            # 0 % 3 = 0, 1 % 3 = 1, 2 % 3 = 2
            photo_path = photo_paths[i % len(photo_paths)]
            slot_x, slot_y, slot_w, slot_h = slots[i]

            # Load photo
            photo = cv.imread(photo_path)
            if photo is None:
                print(f"Warning: Could not load photo {photo_path}")
                continue

            # Resize and crop photo to exactly fill the slot
            photo_resized = self._resize_photo_to_slot(photo, slot_w, slot_h)

            # Photo is now exactly slot_w × slot_h, place directly at slot position
            try:
                result[slot_y : slot_y + slot_h, slot_x : slot_x + slot_w] = (
                    photo_resized
                )
            except Exception as e:
                print(f"Error placing photo {i}: {e}")
                print(f"  Template size: {template_height}x{template_width}")
                print(f"  Photo size: {photo_resized.shape[:2]}")
                print(f"  Slot: ({slot_x}, {slot_y}, {slot_w}, {slot_h})")

        return result

    def _resize_photo_to_slot(
        self, photo: np.ndarray, slot_width: int, slot_height: int
    ) -> np.ndarray:
        """
        Resize photo to exactly fill slot dimensions (crop to fit).
        Photo is scaled to cover the entire slot, then center-cropped to exact size.

        Args:
            photo: Input photo (BGR format)
            slot_width: Target slot width
            slot_height: Target slot height

        Returns:
            Photo exactly matching slot dimensions (slot_height, slot_width, 3)
        """
        h, w = photo.shape[:2]

        # Calculate scale factors for both dimensions
        scale_w = slot_width / w
        scale_h = slot_height / h

        # Use the LARGER scale factor to ensure photo covers entire slot
        scale = max(scale_w, scale_h)

        # Calculate new dimensions (at least one will be larger than slot)
        new_w = int(w * scale)
        new_h = int(h * scale)

        # Resize photo
        resized = cv.resize(photo, (new_w, new_h), interpolation=cv.INTER_LANCZOS4)

        # Center crop to EXACT slot dimensions
        start_x = max(0, (new_w - slot_width) // 2)
        start_y = max(0, (new_h - slot_height) // 2)

        # Ensure we don't go out of bounds
        end_x = start_x + slot_width
        end_y = start_y + slot_height

        cropped = resized[start_y:end_y, start_x:end_x]

        # Final safety: if cropped isn't exactly right size, force resize
        if cropped.shape[0] != slot_height or cropped.shape[1] != slot_width:
            cropped = cv.resize(
                cropped, (slot_width, slot_height), interpolation=cv.INTER_LANCZOS4
            )

        return cropped
