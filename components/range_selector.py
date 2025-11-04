from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)
from PySide6.QtGui import QFont


class RangeSelectorWidget(QWidget):
    def __init__(
        self,
        initial_value=0,
        parent=None,
        disabled_display=True,
        min_value=1,
        max_value=10,
        label_text="",
    ):
        super().__init__(parent)
        self.current_value = initial_value
        self.disabled_display = disabled_display
        self.min_value = min_value
        self.max_value = max_value
        self.label_text = label_text
        self.setup_ui()
        self.connect_signals()

    def setup_ui(self):
        """Builds the UI for the custom widget."""
        # Create the widgets
        self.decrement_button = QPushButton("-")
        self.value_display = QLineEdit(str(self.current_value))
        self.increment_button = QPushButton("+")

        # Set larger fixed sizes for buttons
        self.decrement_button.setFixedSize(80, 80)
        self.increment_button.setFixedSize(80, 80)

        # Set larger fixed size for value display
        self.value_display.setFixedSize(120, 80)

        # Style the buttons with Christmas theme
        button_style = """
            QPushButton {
                background-color: #d42c2c;
                color: white;
                border: none;
                border-radius: 10px;
                font-size: 32px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #b82424;
            }
            QPushButton:pressed {
                background-color: #a01e1e;
            }
        """
        self.decrement_button.setStyleSheet(button_style)
        self.increment_button.setStyleSheet(button_style)

        # Style the value display
        self.value_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        if self.disabled_display:
            self.value_display.setDisabled(True)

        self.value_display.setStyleSheet("""
            QLineEdit {
                font-size: 36px;
                font-weight: bold;
                color: #2d5a2d;
                border: 2px solid #d42c2c;
                border-radius: 10px;
                background-color: white;
            }
            QLineEdit:disabled {
                font-size: 36px;
                font-weight: bold;
                color: #2d5a2d;
                border: 2px solid #d42c2c;
                border-radius: 10px;
                background-color: #f5f5f5;
            }
        """)

        # Create a horizontal layout for the controls
        h_layout = QHBoxLayout()
        h_layout.addWidget(self.decrement_button)
        h_layout.addWidget(self.value_display)
        h_layout.addWidget(self.increment_button)
        h_layout.setSpacing(20)
        h_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Use a main vertical layout for the custom widget
        main_layout = QVBoxLayout(self)

        # Add label if provided
        if self.label_text:
            label = QLabel(self.label_text)
            label_font = QFont()
            label_font.setPointSize(18)
            label_font.setBold(True)
            label.setFont(label_font)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setStyleSheet("color: #2d5a2d; margin: 10px;")
            main_layout.addWidget(label)

        main_layout.addLayout(h_layout)
        main_layout.setContentsMargins(20, 20, 20, 20)
        self.setLayout(main_layout)

    def connect_signals(self):
        """Connects button signals to increment/decrement slots."""
        self.increment_button.clicked.connect(self.increment_value)
        self.decrement_button.clicked.connect(self.decrement_value)

    def increment_value(self):
        """Increments the current value."""
        try:
            current_int = int(self.value_display.text())
            if current_int < self.max_value:
                self.current_value = current_int + 1
                self.value_display.setText(str(self.current_value))
        except ValueError:
            # Handle cases where non-integer text is in the line edit
            self.value_display.setText(str(self.current_value))

    def decrement_value(self):
        """Decrements the current value."""
        try:
            current_int = int(self.value_display.text())
            if current_int > self.min_value:
                self.current_value = current_int - 1
                self.value_display.setText(str(self.current_value))
        except ValueError:
            # Handle cases where non-integer text is in the line edit
            self.value_display.setText(str(self.current_value))
