import sys
from PySide6 import QtGui
from PySide6.QtWidgets import QApplication
from config.load_metadata import initialize_templates_config_dict
from ui.main_window import PhotoboothGUI

if __name__ == "__main__":
    initialize_templates_config_dict()
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = PhotoboothGUI("")
    window.showMaximized()
    sys.exit(app.exec())
