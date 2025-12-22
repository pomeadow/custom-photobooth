#!/usr/bin/env python3
"""Generate preview strips (half vertical cut) for template composites."""

import os
import cv2 as cv
from controllers.image_processor import ImageProcessor
from config.load_metadata import templates_config


def generate_preview_strip(
    photo_paths, num_photos, template_path, output_dir, output_prefix="preview_strip"
):
    """
    Generate a preview strip with selected photos.

    Args:
        photo_paths: List of paths to photos
        num_photos: Number of photos
        template_path: Path to the selected template
        output_dir: Directory to save the preview strip
        output_prefix: Prefix for output filename

    Returns:
        str: Path to generated preview strip, or None if generation failed
    """
    if len(photo_paths) != num_photos:
        print(f"Error: Expected {num_photos} photos, got {len(photo_paths)}")
        return None

    os.makedirs(output_dir, exist_ok=True)

    if not os.path.exists(template_path):
        print(f"Template not found at {template_path}")
        return None

    try:
        # Load the template
        template = cv.imread(template_path)
        if template is None:
            print(f"Failed to load template from {template_path}")
            return None

        # Create composite using ImageProcessor
        processor = ImageProcessor()

        # Prepare photos for composite
        # We'll duplicate the photos to fill all slots, then crop later
        if num_photos == 2:
            # Duplicate photos: [photo1, photo2, photo1, photo2]
            photos_for_composite = photo_paths + photo_paths
        elif num_photos == 4:
            # Duplicate photos: [photo1, photo2, photo3, photo1, photo2, photo3]
            photos_for_composite = photo_paths + photo_paths
        else:
            photos_for_composite = photo_paths

        # Create a full composite first, then crop it
        composite = processor.create_photo_composite(
            photo_paths=photos_for_composite,
            template_path=template_path,
        )

        # Crop the composite based on template type
        # 2x2 and 4x2: take left column (left half)
        height, width = composite.shape[:2]
        half_width = width // 2
        composite_half = composite[:, :half_width].copy()

        # Save the preview strip
        output_filename = f"{output_prefix}_{num_photos}photos.png"
        output_path = os.path.join(output_dir, output_filename)
        cv.imwrite(output_path, composite_half)

        print(f"Generated preview strip: {output_path}")
        return output_path

    except Exception as e:
        print(f"Error generating preview strip: {e}")
        import traceback

        traceback.print_exc()
        return None
