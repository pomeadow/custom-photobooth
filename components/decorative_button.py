from calendar import c
import re
from PySide6.QtCore import QRect, QRectF, Qt, Signal
from PySide6.QtGui import QPainter, QPainterPath, QPen, QBrush, QColor, QFont
from PySide6.QtWidgets import QPushButton
from numpy import rec


class DecorativeButton(QPushButton):
    """Custom button with decorative corner quadrants."""

    def __init__(self, text="", parent=None, min_width=None, min_height=None):
        super().__init__(text, parent)
        if min_width and min_height:
            self.setMinimumSize(min_width, min_height)
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

        # Draw background (solid, not transparent)
        bg_color = QColor(129, 21, 27) if not self.is_hovered else QColor(160, 30, 30)
        if self.is_pressed_state:
            bg_color = QColor(100, 15, 20)

        pen = QPen(bg_color, 1)
        painter.setPen(pen)

        # Draw concave circular quadrants at corners (curving inward toward center)
        quadrant_radius = 10
        corner_inset = quadrant_radius

        path = QPainterPath()
        path.moveTo(
            rect.left() + corner_inset + quadrant_radius, rect.top() + corner_inset
        )
        path.lineTo(
            rect.right() - quadrant_radius - corner_inset, rect.top() + corner_inset
        )
        path.arcTo(
            rect.right() - (quadrant_radius + corner_inset),
            rect.top(),
            quadrant_radius * 2,
            quadrant_radius * 2,
            180,
            90,
        )
        path.lineTo(
            rect.right() - corner_inset, rect.bottom() - quadrant_radius - corner_inset
        )
        path.arcTo(
            rect.right() - (quadrant_radius + corner_inset),
            rect.bottom() - (quadrant_radius + corner_inset),
            quadrant_radius * 2,
            quadrant_radius * 2,
            90,
            90,
        )
        path.lineTo(
            rect.left() + quadrant_radius + corner_inset, rect.bottom() - corner_inset
        )
        path.arcTo(
            rect.left(),
            rect.bottom() - (quadrant_radius + corner_inset),
            quadrant_radius * 2,
            quadrant_radius * 2,
            0,
            90,
        )
        path.lineTo(
            rect.left() + corner_inset, rect.top() + quadrant_radius + corner_inset
        )
        path.arcTo(
            rect.left(), rect.top(), quadrant_radius * 2, quadrant_radius * 2, 270, 90
        )
        painter.drawPath(path)
        painter.fillPath(path, bg_color)

        painter.setPen(QPen(QColor("#C9A961"), 3))
        inner = QPainterPath()
        margin = 5
        inner.moveTo(
            rect.left() + corner_inset + quadrant_radius + margin,
            rect.top() + corner_inset + margin,
        )
        inner.lineTo(
            rect.right() - quadrant_radius - corner_inset - margin,
            rect.top() + corner_inset + margin,
        )
        inner.arcTo(
            rect.right() - (quadrant_radius + corner_inset) - margin,
            rect.top() + margin,
            quadrant_radius * 2,
            quadrant_radius * 2,
            180,
            90,
        )
        inner.lineTo(
            rect.right() - corner_inset - margin,
            rect.bottom() - quadrant_radius - corner_inset - margin,
        )
        inner.arcTo(
            rect.right() - (quadrant_radius + corner_inset) - margin,
            rect.bottom() - (quadrant_radius + corner_inset) - margin,
            quadrant_radius * 2,
            quadrant_radius * 2,
            90,
            90,
        )
        inner.lineTo(
            rect.left() + quadrant_radius + corner_inset + margin,
            rect.bottom() - corner_inset - margin,
        )
        inner.arcTo(
            rect.left() + margin,
            rect.bottom() - (quadrant_radius + corner_inset) - margin,
            quadrant_radius * 2,
            quadrant_radius * 2,
            0,
            90,
        )
        inner.lineTo(
            rect.left() + corner_inset + margin,
            rect.top() + quadrant_radius + corner_inset + margin,
        )
        inner.arcTo(
            rect.left() + margin,
            rect.top() + margin,
            quadrant_radius * 2,
            quadrant_radius * 2,
            270,
            90,
        )

        # Draw inner shape
        painter.drawPath(inner)
        # Draw text
        painter.setPen(self.text_color)
        font = QFont("Impact", 60, QFont.Weight.Bold)
        painter.setFont(font)
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, self.text())
