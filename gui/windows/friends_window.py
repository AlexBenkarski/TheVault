from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


class FriendsWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        """Initialize the friends window UI"""
        # Set background to match app theme
        self.setStyleSheet("""
            QWidget {
                background-color: #1a1a1d;
                color: #ffffff;
            }
        """)

        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # Title
        title = QLabel("Friends & Sharing")
        title.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        title.setStyleSheet("color: #4CAF50; margin-bottom: 10px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Coming soon message
        coming_soon = QLabel("Coming Soon!")
        coming_soon.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        coming_soon.setStyleSheet("color: #ffaa00; margin-bottom: 5px;")
        coming_soon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(coming_soon)

        # Description
        description = QLabel("Secure password sharing with friends and family")
        description.setFont(QFont("Segoe UI", 14))
        description.setStyleSheet("color: #888888;")
        description.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(description)

        # Stretch to center content
        layout.addStretch()