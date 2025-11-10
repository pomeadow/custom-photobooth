import sys
from PySide6.QtWidgets import QApplication
from ui.main_window import PhotoboothGUI

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PhotoboothGUI("")
    window.show()
    sys.exit(app.exec())
