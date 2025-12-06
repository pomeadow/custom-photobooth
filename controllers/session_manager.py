import datetime
import os
from pathlib import Path
from typing import Optional, Union
import cv2 as cv


class SessionManager:
    def __init__(self, base_dir) -> None:
        self._base_dir = Path(base_dir) if base_dir else Path.cwd()
        self._current_session_folder: Optional[Path] = None
        self._template_path = None
        self._template_index = None

    def create_session(self, template_path: str, template_index: int, num_photos):
        """Create new session folder and properties"""
        self._template_path = template_path
        self._template_index = template_index
        self._num_photos = num_photos
        now = datetime.datetime.now()
        folder_name = now.strftime("session_%Y%m%d_%H%M%S")
        self._current_session_folder = Path(os.path.join(self._base_dir, folder_name))
        os.makedirs(self._current_session_folder, exist_ok=True)
        print(f"Created session folder: {self._current_session_folder}")
        return self._current_session_folder

    def create_default_session(self):
        return self.create_session("", 0, None)

    def set_template_path(self, template_path: str):
        self._template_path = template_path

    def set_template_index(self, template_index: int):
        self._template_index = template_index

    def set_num_photos(self, num_photos: int):
        self._num_photos = num_photos

    @property
    def get_current_session_folder(self):
        return self._current_session_folder

    @property
    def photo_count(self) -> int:
        """Get number of photos saved in current session."""
        return self._photo_count

    @property
    def template_info(self):
        """Get path of templates and index selected"""
        return self._template_path, self._template_index, self._num_photos

    def close_session(self):
        """Close the current session."""
        self._current_session_folder = None
        self._photo_count = 0

    def save_photo(self, frame):
        # Save the captured image to current session folder
        now = datetime.datetime.now()
        formatted_date_time = now.strftime("%Y-%m-%d %H%M%S.%f")
        filename = f"{formatted_date_time}_image.png"

        # Save to session folder if it exists, otherwise save to current directory
        if self._current_session_folder:
            filepath = os.path.join(self._current_session_folder, filename)
        else:
            filepath = filename

        cv.imwrite(filepath, frame)
        print(f"Photo captured and saved as {filepath}")
