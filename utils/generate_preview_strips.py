#!/usr/bin/env python3
"""Generate preview strips (half vertical cut) for template composites."""

import os
import cv2 as cv
from controllers.image_processor import ImageProcessor
from config.load_metadata import templates_config


def generate_preview_strip(
    photo_paths, num_photos, output_dir, output_prefix="preview_strip"
):
    """
    Generate a preview strip with selected photos.

    Args:
        photo_paths: List of paths to photos (2 or 3 photos)
        num_photos: Number of photos (2 or 3)
        output_dir: Directory to save the preview strip
        output_prefix: Prefix for output filename

    Returns:
        str: Path to generated preview strip, or None if generation failed
    """
    if len(photo_paths) != num_photos:
        print(f"Error: Expected {num_photos} photos, got {len(photo_paths)}")
        return None

    os.makedirs(output_dir, exist_ok=True)

    # Map number of photos to template configuration
    # For 3 photos: use template 2 (1x3 horizontal layout)
    # For 2 photos: we need to create a 2x1 variant or use existing template

    if num_photos == 3:
        template_index = 0  # templateup4 - 2x3 grid, we'll take top row
        template_path = "./resources/templates/v0.1/templateup4.png"
    elif num_photos == 2:
        template_index = 3  # templateup3 - 2x2 grid, we'll take left column
        template_path = "./resources/templates/v0.1/templateup3.png"
    else:
        print(f"Preview strips only supported for 2 or 3 photos, got {num_photos}")
        return None

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
        # For 2 photos with template 3 (2x2 grid), we need to provide 4 photos
        # For 3 photos with template 0 (2x3 grid), we need to provide 6 photos
        # We'll duplicate the photos to fill all slots, then crop later
        if num_photos == 2 and template_index == 3:
            # Duplicate photos: [photo1, photo2, photo1, photo2]
            photos_for_composite = photo_paths + photo_paths
        elif num_photos == 3 and template_index == 0:
            # Duplicate photos: [photo1, photo2, photo3, photo1, photo2, photo3]
            photos_for_composite = photo_paths + photo_paths
        else:
            photos_for_composite = photo_paths

        # Create a full composite first, then crop it
        composite = processor.create_photo_composite(
            photo_paths=photos_for_composite,
            template_path=template_path,
            template_index=template_index,
        )

        # Crop the composite based on template type
        if template_index == 3:
            # templateup3 (2x2): take left column (left half)
            height, width = composite.shape[:2]
            half_width = width // 2
            composite_half = composite[:, :half_width].copy()
        elif template_index == 0:
            # templateup4 (2x3): take top row (top half)
            height, width = composite.shape[:2]
            half_height = height // 2
            composite_half = composite[:half_height, :].copy()
        else:
            composite_half = composite

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


# def generate_all_preview_strips(photo_paths, output_dir):
#     """
#     Generate preview strips for 2 and 3 photo configurations.

#     Args:
#         photo_paths: List of paths to photos (must have at least 3 photos)
#         output_dir: Directory to save preview strips

#     Returns:
#         dict: Dictionary mapping num_photos to output path {2: path, 3: path}
#     """
#     results = {}

#     if len(photo_paths) >= 2:
#         strip_2 = generate_preview_strip(
#             photo_paths[:2],
#             num_photos=2,
#             output_dir=output_dir,
#             output_prefix="preview_strip"
#         )
#         if strip_2:
#             results[2] = strip_2

#     if len(photo_paths) >= 3:
#         strip_3 = generate_preview_strip(
#             photo_paths[:3],
#             num_photos=3,
#             output_dir=output_dir,
#             output_prefix="preview_strip"
#         )
#         if strip_3:
#             results[3] = strip_3

#     return results
