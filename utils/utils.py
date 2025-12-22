import os
from pathlib import Path

from PySide6.QtCore import QUrl
from PySide6.QtMultimedia import QSoundEffect


def get_png_file_paths(directory_path):
    """
    Recursively finds and returns the absolute paths of all PNG files
    within a given directory and its subdirectories.

    Args:
        directory_path (str): The path to the directory to search.

    Returns:
        list: A list of absolute paths to PNG files.
    """
    base_path = Path(directory_path)
    png_files = []
    for file_path in base_path.rglob("*.png"):
        png_files.append(str(file_path.absolute()))
    return png_files


def clear_layout(layout):
    if layout is None:
        return
    while layout.count():
        item = layout.takeAt(0)
        widget = item.widget()
        if widget is not None:
            widget.deleteLater()  # Delete the widget
        elif item.layout() is not None:
            clear_layout(item.layout())  # Recurse into nested layouts

def load_sound_effect(file_path):
    effect = QSoundEffect()
    abs_path = os.path.abspath(file_path)
    effect.setSource(QUrl.fromLocalFile(abs_path))
    effect.setVolume(1.0)
    return effect
