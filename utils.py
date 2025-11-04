"""
Recursively finds and returns the absolute paths of all PNG files
within a given directory and its subdirectories.

Args:
    directory_path (str): The path to the directory to search.

Returns:
    list: A list of absolute paths to PNG files.
"""

from pathlib import Path


def get_png_file_paths(directory_path):
    base_path = Path(directory_path)
    png_files = []
    for file_path in base_path.rglob("*.png"):
        png_files.append(str(file_path.absolute()))
    return png_files
