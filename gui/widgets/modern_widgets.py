import os
from PyQt6.QtWidgets import QPushButton, QLineEdit, QLabel, QFrame, QDialog, QWidget
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QPixmap


class ModernButton(QPushButton):
    def __init__(self, text, primary=True):
        super().__init__(text)
        self.primary = primary
        self.setMinimumHeight(45)
        self.setFont(QFont("Segoe UI", 11, QFont.Weight.Medium))
        self.setCursor(Qt.CursorShape.PointingHandCursor)


class ModernLineEdit(QLineEdit):
    def __init__(self, placeholder=""):
        super().__init__()
        self.setPlaceholderText(placeholder)
        # Basic text input styling
        self.setFixedHeight(40)
        self.setFont(QFont("Segoe UI", 11))
        self.setAlignment(Qt.AlignmentFlag.AlignVCenter)


class LogoWidget(QLabel):
    def __init__(self):
        super().__init__()
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.load_logo()

    def load_logo(self):
        # Build path to logo file
        current_dir = os.path.dirname(os.path.abspath(__file__))
        gui_dir = os.path.dirname(current_dir)
        project_root = os.path.dirname(gui_dir)
        logo_path = os.path.join(project_root, "assets", "logo.png")

        # Load and scale logo
        pixmap = QPixmap(logo_path)
        scaled_pixmap = pixmap.scaledToHeight(80, Qt.TransformationMode.SmoothTransformation)
        self.setPixmap(scaled_pixmap)

class ModernSmallButton(QPushButton):
    def __init__(self, text, delete_style=False):
        super().__init__(text)
        self.delete_style = delete_style
        # Set button properties
        self.setProperty("smallButton", True)
        if delete_style:
            self.setProperty("delete", True)
        self.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        self.setCursor(Qt.CursorShape.PointingHandCursor)

class ModernEntryHeader(QPushButton):
    def __init__(self, text):
        super().__init__(text)
        # Configure header properties
        self.setProperty("entryHeader", True)
        self.setProperty("expanded", False)
        self.setFixedHeight(45)
        self.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.is_expanded = False

    def set_expanded(self, expanded):
        self.is_expanded = expanded
        self.setProperty("expanded", expanded)
        # Force style refresh
        self.style().unpolish(self)
        self.style().polish(self)

        # Update arrow direction
        text = self.text()
        if text.startswith("▶") or text.startswith("▼"):
            arrow = "▼" if expanded else "▶"
            self.setText(arrow + text[1:])


class ModernEntryFrame(QFrame):
    def __init__(self):
        super().__init__()
        self.setProperty("entryWidget", True)
        self.setProperty("expanded", False)

    def set_expanded(self, expanded):
        self.setProperty("expanded", expanded)
        # Force style refresh
        self.style().unpolish(self)
        self.style().polish(self)


class ModernDialog(QDialog):
    def __init__(self, parent=None, title="Dialog"):
        super().__init__(parent)
        self.setProperty("modern", True)
        self.setWindowTitle(title)
        # Remove window decorations
        self.setWindowFlags(Qt.WindowType.Dialog |
                            Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)

    def setup_basic_layout(self, title_text):
        from PyQt6.QtWidgets import QVBoxLayout, QLabel, QFrame

        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Header and separator
        header_label = QLabel(title_text)
        header_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #4CAF50;")
        layout.addWidget(header_label)

        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet("background: rgba(255, 255, 255, 0.2);")
        layout.addWidget(separator)

        return layout


class ModernFormField(QWidget):
    def __init__(self, label_text, input_widget, label_width=100):
        super().__init__()

        from PyQt6.QtWidgets import QHBoxLayout, QLabel
        from PyQt6.QtGui import QFont

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 5, 0, 5)
        layout.setSpacing(10)

        # Create and style label
        label = QLabel(label_text)
        label.setFixedWidth(label_width)
        label.setFont(QFont("Segoe UI", 12))
        label.setStyleSheet("color: #ffffff;")

        # Set modern property on input
        if hasattr(input_widget, 'setProperty'):
            input_widget.setProperty("modern", True)

        layout.addWidget(label)
        layout.addWidget(input_widget)

        self.input = input_widget
        self.label = label