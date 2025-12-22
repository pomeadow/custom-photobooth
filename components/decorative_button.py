import re
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPainter, QPainterPath, QPen, QBrush, QColor, QFont
from PySide6.QtWidgets import QPushButton


class DecorativeButton(QPushButton):
    """Custom button with decorative corner quadrants."""

    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.setMinimumSize(800, 120)
        self.border_color = QColor("#C9A961")  # Gold
        self.text_color = QColor("#C9A961")  # Gold
        self.bg_color = QColor(129, 21, 27, 76)  # Semi-transparent red
        self.hover_bg_color = QColor(129, 21, 27, 127)
        self.is_hovered = False
        self.is_pressed_state = False

    def enterEvent(self, event):
        self.is_hovered = True
        self.update()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.is_hovered = False
        self.update()
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        self.is_pressed_state = True
        self.update()
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        self.is_pressed_state = False
        self.update()
        super().mouseReleaseEvent(event)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = self.rect()
        
       
        pen = QPen(QColor("#C9A961"),  4)
        # painter.setPen(pen)

        # Draw background (solid, not transparent)
        bg_color = QColor(129, 21, 27) if not self.is_hovered else QColor(160, 30, 30)
        if self.is_pressed_state:
            bg_color = QColor(100, 15, 20)

        # pen = QPen(bg_color, 4)
        painter.setPen(pen)
       
        # painter.fillRect(rect, bg_color)

        # Draw concave circular quadrants at corners (curving inward toward center)
        quadrant_radius = 10
        corner_inset = 18

        path = QPainterPath()

        path.moveTo(rect.left() + quadrant_radius, rect.top())
        path.lineTo(rect.right() - quadrant_radius, rect.top())
        path.arcTo(
            rect.right() - quadrant_radius,
            rect.top(),
            quadrant_radius * 2,
            quadrant_radius * 2,
            180, 90
        )
        path.lineTo(rect.right(), rect.bottom() - quadrant_radius)
        path.arcTo(
            rect.right(),
            rect.bottom(),
            quadrant_radius * 2,
            quadrant_radius * 2,
            270, 180)
        path.lineTo(rect.left() + quadrant_radius, rect.bottom())
        path.arcTo(
            rect.left(),
            rect.bottom() - quadrant_radius,
            quadrant_radius * 2,
            quadrant_radius * 2,
            90, 90)
        path.lineTo(rect.left(), rect.top() + quadrant_radius)
        path.arcTo(
            rect.left(),
            rect.top(),
            quadrant_radius * 2,
            quadrant_radius * 2,
            180,90)
        painter.drawPath(path)

        # painter.drawLine(rect.left() + quadrant_radius, rect.top(), rect.right() - quadrant_radius, rect.top())
        # painter.drawLine(rect.left() + quadrant_radius, rect.bottom(), rect.right() - quadrant_radius, rect.bottom())
        # painter.drawLine(rect.left(), rect.top() + quadrant_radius, rect.left(), rect.bottom() + quadrant_radius)
        # painter.drawLine(rect.right(), rect.top() - quadrant_radius, rect.right(), rect.bottom() - quadrant_radius)
        # painter.fillPath(path, bg_color)

        # # Top-left corner - arc curving inward (shows right and bottom edges)
        # painter.drawArc(
        #     rect.left() + corner_inset - quadrant_radius,
        #     rect.top() + corner_inset - quadrant_radius,
        #     quadrant_radius * 2,
        #     quadrant_radius * 2,
        #     180 * 16,
        #     90 * 16       # Span angle (90 degrees)
        # )

        # # Top-right corner - arc curving inward (shows bottom and left edges)
        # painter.drawArc(
        #     rect.right() - corner_inset - quadrant_radius,
        #     rect.top() + corner_inset - quadrant_radius,
        #     quadrant_radius * 2,
        #     quadrant_radius * 2,
        #     270 * 16,  # Start angle (270 degrees)
        #     90 * 16    # Span angle (90 degrees)
        # )

        # # Bottom-left corner - arc curving inward (shows top and right edges)
        # painter.drawArc(
        #     rect.left() + corner_inset - quadrant_radius,
        #     rect.bottom() - corner_inset - quadrant_radius,
        #     quadrant_radius * 2,
        #     quadrant_radius * 2,
        #     90 * 16,   # Start angle (90 degrees)
        #     90 * 16    # Span angle (90 degrees)
        # )

        # # Bottom-right corner - arc curving inward (shows top and left edges)
        # painter.drawArc(
        #     rect.right() - corner_inset - quadrant_radius,
        #     rect.bottom() - corner_inset - quadrant_radius,
        #     quadrant_radius * 2,
        #     quadrant_radius * 2,
        #     0 * 16,    # Start angle (0 degrees)
        #     90 * 16    # Span angle (90 degrees)
        # )

        # Draw text
        painter.setPen(self.text_color)
        font = QFont("Impact", 72, QFont.Weight.Bold)
        painter.setFont(font)
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, self.text())
