#!/usr/bin/env python3
"""Utility script to generate photo composites for all available templates."""

import os
import sys
import glob
import cv2 as cv
from pathlib import Path
from controllers.image_processor import ImageProcessor
from config.load_metadata import templates_config


def get_session_photos(session_path):
    """Get all photo paths from a session directory."""
    if not os.path.exists(session_path):
        return []

    # Get all PNG images except final_composite.png
    photos = []
    for file in sorted(glob.glob(os.path.join(session_path, "*.png"))):
        if "final_composite" not in file and "composite_template" not in file:
            photos.append(file)

    return photos


def generate_all_composites(photo_paths, output_dir=None, output_prefix="composite"):
    """
    Generate composites for all available templates.

    Args:
        photo_paths: List of paths to photos to use in composites
        output_dir: Directory to save composites (defaults to current directory)
        output_prefix: Prefix for output filenames (default: "composite")

    Returns:
        dict: Dictionary mapping template_index to output path
    """
    if output_dir is None:
        output_dir = os.getcwd()

    os.makedirs(output_dir, exist_ok=True)

    processor = ImageProcessor()
    results = {}

    print(f"\nGenerating composites for all {len(templates_config)} templates...")
    print(f"Using {len(photo_paths)} photos")
    print(f"Output directory: {output_dir}\n")

    for template_index, template_info in templates_config.items():
        num_photos_needed = template_info["num_photos"]
        template_name = f"template{template_index}"

        # Get the template file path
        template_files = {
            0: "./resources/templates/v0.1/templateup4.png",  # 2x3, 6 photos
            1: "./resources/templates/templateup1.png",  # 2x4, 4 photos
            2: "./resources/templates/templateup2.png",  # 1x3, 3 photos
            3: "./resources/templates/v0.1/templateup3.png",  # 2x2, 4 photos
        }

        template_path = template_files.get(template_index)
        if not template_path or not os.path.exists(template_path):
            print(
                f"Template {template_index}: Template file not found at {template_path}"
            )
            continue

        # Check if we have enough photos
        if len(photo_paths) < num_photos_needed:
            print(
                f"Template {template_index}: Needs {num_photos_needed} photos, but only {len(photo_paths)} provided. Skipping."
            )
            continue

        # Use the required number of photos (cycle if we have more)
        photos_to_use = photo_paths[:num_photos_needed]

        print(
            f"Template {template_index} ({template_info['num_photos']} photos, rotate={template_info['toRotate']})..."
        )

        try:
            composite = processor.create_photo_composite(
                photo_paths=photos_to_use,
                template_path=template_path,
                template_index=template_index,
            )

            # Save the composite
            output_filename = f"{output_prefix}_template{template_index}.png"
            output_path = os.path.join(output_dir, output_filename)
            cv.imwrite(output_path, composite)

            results[template_index] = output_path
            print(f"Saved: {output_path}")

        except Exception as e:
            print(f"Error generating composite for template {template_index}: {e}")
            import traceback

            traceback.print_exc()

    print(f"\n✨ Generated {len(results)} composites successfully!")
    return results


def main():
    """Main entry point for the script."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate photo composites for all available templates"
    )
    parser.add_argument(
        "--session", type=str, help="Path to session directory containing photos"
    )
    parser.add_argument(
        "--photos", type=str, nargs="+", help="List of photo paths to use"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="./composite_output",
        help="Directory to save composites (default: ./composite_output)",
    )
    parser.add_argument(
        "--output-prefix",
        type=str,
        default="composite",
        help="Prefix for output filenames (default: composite)",
    )

    args = parser.parse_args()

    # Determine which photos to use
    photo_paths = []

    if args.session:
        print(f"Loading photos from session: {args.session}")
        photo_paths = get_session_photos(args.session)
        if not photo_paths:
            print(f"Error: No photos found in session directory: {args.session}")
            sys.exit(1)
    elif args.photos:
        photo_paths = args.photos
    else:
        # Try to find the most recent session
        sessions = sorted(glob.glob("./session_*"), reverse=True)
        if sessions:
            latest_session = sessions[0]
            print(f"No photos specified, using latest session: {latest_session}")
            photo_paths = get_session_photos(latest_session)

        if not photo_paths:
            print("Error: No photos specified and no sessions found.")
            print("\nUsage examples:")
            print(
                "  python generate_all_composites.py --session ./session_20251111_003314"
            )
            print(
                "  python generate_all_composites.py --photos photo1.png photo2.png photo3.png photo4.png photo5.png photo6.png"
            )
            sys.exit(1)

    print(f"Found {len(photo_paths)} photos:")
    for i, path in enumerate(photo_paths, 1):
        print(f"  {i}. {path}")

    # Generate composites
    results = generate_all_composites(
        photo_paths=photo_paths,
        output_dir=args.output_dir,
        output_prefix=args.output_prefix,
    )

    print("\n📂 Output files:")
    for template_index, output_path in sorted(results.items()):
        print(f"  Template {template_index}: {output_path}")


if __name__ == "__main__":
    main()
