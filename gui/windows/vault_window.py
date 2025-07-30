from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea,
                             QFrame, QPushButton, QGroupBox, QGridLayout, QDialog,
                             QLineEdit, QTextEdit, QMessageBox, QFileDialog, QSizePolicy)
from PyQt6.QtCore import Qt, pyqtSignal, QDateTime, QSize, QTimer
from PyQt6.QtGui import QFont

from gui.update_manager import get_current_version
from gui.widgets.modern_widgets import (ModernButton, ModernSmallButton, ModernEntryHeader,
                                        ModernEntryFrame, ModernDialog, ModernFormField, ModernLineEdit)
from gui.widgets.svg_icons import SvgIcon, Icons



class VaultWindow(QWidget):
    logout_requested = pyqtSignal()

    def __init__(self):
        super().__init__()
        # Global vault state
        self.selected_folder = None
        self.vault_data = {}
        self.vault_key = None
        self.folder_buttons = {}
        self.init_ui()

    def init_ui(self):
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Main content area with fixed layout (YOUR ORIGINAL CODE)
        content_layout = QHBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        # Left panel - fixed width
        left_panel = self.create_left_panel()
        left_panel.setFixedWidth(280)

        # Right panel - takes remaining space
        right_panel = self.create_right_panel()

        content_layout.addWidget(left_panel)
        content_layout.addWidget(right_panel)

        # Create content widget
        content_widget = QWidget()
        content_widget.setLayout(content_layout)

        main_layout.addWidget(content_widget)

        # Bottom status bar
        self.create_status_bar(main_layout)

        self.setLayout(main_layout)


    def create_left_panel(self):
        """Create the enhanced left sidebar panel without Quick Actions"""
        left_widget = QWidget()
        left_widget.setFixedWidth(280)
        left_widget.setStyleSheet("""
            QWidget {
                background: #1a1a1d;
                border-right: 1px solid rgba(255, 255, 255, 0.08);
            }
        """)

        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(16, 20, 16, 20)
        left_layout.setSpacing(20)

        # Security Health Section
        security_section = self.create_security_health_section()
        left_layout.addWidget(security_section)

        # Expanded Folders Section - now takes up more space
        folders_section = self.create_enhanced_folders_section()
        left_layout.addWidget(folders_section)

        # Recent Activity Section - moved up to fill space
        recent_activity = self.create_recent_activity_section()
        left_layout.addWidget(recent_activity)

        # Remove the addStretch() to let folders take more space naturally
        return left_widget

    def create_security_health_section(self):
        """Create enhanced security health status panel with better styling"""
        section = QWidget()
        section.setFixedHeight(140)  # Expanded height for more content

        # Enhanced styling with gradient background and stronger border
        section.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(76, 175, 80, 0.15), 
                    stop:1 rgba(76, 175, 80, 0.08));
                border: 2px solid rgba(76, 175, 80, 0.3);
                border-radius: 12px;
            }
        """)

        layout = QVBoxLayout(section)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(8)

        # Header row with enhanced status
        header_layout = QHBoxLayout()
        header_layout.setSpacing(0)

        title = QLabel("Quick Health")
        title.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        title.setStyleSheet("color: #ffffff; background: transparent; border: none;")

        # Dynamic status based on vault data
        vault_data = getattr(self, 'vault_data', {}).get('data', {})
        has_issues = self.check_security_issues(vault_data)

        status_text = "Needs Attention" if has_issues else "Good"
        status_color = "#ff9500" if has_issues else "#4CAF50"

        status_label = QLabel(status_text)
        status_label.setStyleSheet(f"""
            color: {status_color};
            font-size: 12px;
            font-weight: 700;
            background: rgba(0, 0, 0, 0.1);
            padding: 4px 8px;
            border-radius: 6px;
            border: none;
        """)

        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(status_label)
        layout.addLayout(header_layout)

        # Weak Passwords line
        weak_layout = QHBoxLayout()
        weak_label = QLabel("Weak Passwords:")
        weak_label.setFont(QFont("Segoe UI", 10))
        weak_label.setStyleSheet("color: #ff9500; background: transparent; border: none;")

        weak_count = QLabel("3 found")
        weak_count.setFont(QFont("Segoe UI", 10))
        weak_count.setStyleSheet("color: #ff9500; background: transparent; border: none;")

        weak_layout.addWidget(weak_label)
        weak_layout.addStretch()
        weak_layout.addWidget(weak_count)
        layout.addLayout(weak_layout)

        # Last Sync line
        sync_layout = QHBoxLayout()
        sync_label = QLabel("Last Sync:")
        sync_label.setFont(QFont("Segoe UI", 10))
        sync_label.setStyleSheet("color: #b0b0b0; background: transparent; border: none;")

        sync_time = QLabel("2 min ago")
        sync_time.setFont(QFont("Segoe UI", 10))
        sync_time.setStyleSheet("color: #4CAF50; background: transparent; border: none;")

        sync_layout.addWidget(sync_label)
        sync_layout.addStretch()
        sync_layout.addWidget(sync_time)
        layout.addLayout(sync_layout)

        # Backup Status line
        backup_layout = QHBoxLayout()
        backup_label = QLabel("Backup Status:")
        backup_label.setFont(QFont("Segoe UI", 10))
        backup_label.setStyleSheet("color: #b0b0b0; background: transparent; border: none;")

        backup_status = QLabel("OneDrive ✓")
        backup_status.setFont(QFont("Segoe UI", 10))
        backup_status.setStyleSheet("color: #4CAF50; background: transparent; border: none;")

        backup_layout.addWidget(backup_label)
        backup_layout.addStretch()
        backup_layout.addWidget(backup_status)
        layout.addLayout(backup_layout)

        return section

    def create_folder_list_item(self, folder_name, password_count, is_selected=False):
        """Create a folder list item with unified border styling (updated to match enhanced version)"""
        print(f"Creating old folder list item: {folder_name}, selected: {is_selected}")
        item_container = QWidget()
        item_container.setFixedHeight(50)
        item_container.setCursor(Qt.CursorShape.PointingHandCursor)

        # Use the same unified border approach as enhanced version
        if is_selected:
            item_container.setStyleSheet("""
                QWidget {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 rgba(76, 175, 80, 0.15), 
                        stop:1 rgba(76, 175, 80, 0.08));
                    border: 2px solid #4CAF50;
                    border-radius: 8px;
                }
                QWidget > QWidget {
                    border: none !important;
                    background: transparent !important;
                }
                QWidget QLabel {
                    background: transparent !important;
                    border: none !important;
                }
                QWidget QLabel:hover, QWidget QLabel:focus, QWidget QLabel:pressed {
                    background: transparent !important;
                    border: none !important;
                }
            """)
        else:
            item_container.setStyleSheet("""
                QWidget {
                    background: transparent;
                    border: none;
                    border-radius: 8px;
                }
                QWidget:hover {
                    background: rgba(255, 255, 255, 0.06);
                }
                QWidget > QWidget {
                    border: none !important;
                }
            """)

        container_layout = QHBoxLayout(item_container)
        container_layout.setContentsMargins(12, 8, 12, 8)
        container_layout.setSpacing(12)

        # Icon container with mouse transparency
        icon_container = QWidget()
        icon_container.setFixedSize(34, 34)
        icon_container.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)

        # Icon colors based on folder name
        icon_colors = {
            'Battle.net': '#ff6b6b',
            'Twitch': '#9146ff',
            'Epic Games': '#0078f2',
            'Minecraft': '#00c851',
            'Gmail': '#ea4335',
            'Random Pass': '#666666',
            'Social Media': '#1da1f2',
            'Banking': '#ffa726',
            'Work': '#795548'
        }

        bg_color = icon_colors.get(folder_name, "#666666")
        icon_container.setStyleSheet(f"""
            QWidget {{
                background: {bg_color};
                border-radius: 8px;
                border: none;
            }}
        """)

        # Create SVG folder icon
        icon_layout = QHBoxLayout(icon_container)
        icon_layout.setContentsMargins(0, 0, 0, 0)

        icon_label = QLabel("📂")
        icon_label.setStyleSheet("color: white; font-size: 18px; background: transparent; border: none;")
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        icon_layout.addWidget(icon_label)

        # Folder info with mouse transparency
        info_layout = QVBoxLayout()
        info_layout.setSpacing(3)
        info_layout.setContentsMargins(0, 2, 0, 2)

        name_label = QLabel(folder_name)
        name_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Medium))
        name_label.setStyleSheet("color: #ffffff; background: transparent; border: none;")
        name_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)

        count_text = f"{password_count} password{'s' if password_count != 1 else ''}"
        count_label = QLabel(count_text)
        count_label.setFont(QFont("Segoe UI", 10))
        count_color = "#999999"
        count_label.setStyleSheet(f"color: {count_color}; background: transparent; border: none;")
        count_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)

        info_layout.addWidget(name_label)
        info_layout.addWidget(count_label)

        container_layout.addWidget(icon_container)
        container_layout.addLayout(info_layout, 1)

        # NO separate indicator - using unified border only

        # Connect click handler
        def on_folder_click(event):
            self.select_folder(folder_name)
            event.accept()

        item_container.mousePressEvent = on_folder_click

        return item_container

    def create_enhanced_folders_section(self):
        """Create the enhanced folders section with clean styling"""
        section = QWidget()
        layout = QVBoxLayout(section)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        # Header with add button - FOLDERS text now white
        header_layout = QHBoxLayout()
        header_layout.setSpacing(0)

        folders_title = QLabel("FOLDERS")
        folders_title.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        folders_title.setStyleSheet("color: #ffffff; background: transparent; letter-spacing: 0.5px;")

        add_folder_btn = QPushButton("+")
        add_folder_btn.setFixedSize(20, 20)
        add_folder_btn.setStyleSheet("""
            QPushButton {
                background: rgba(255, 255, 255, 0.1);
                border: none;
                border-radius: 10px;
                color: #ffffff;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 0.2);
            }
            QPushButton:focus {
                outline: none;
            }
        """)
        add_folder_btn.clicked.connect(self.add_folder)

        header_layout.addWidget(folders_title)
        header_layout.addStretch()
        header_layout.addWidget(add_folder_btn)
        layout.addLayout(header_layout)

        # CREATE SCROLL AREA for folders
        from PyQt6.QtWidgets import QScrollArea, QSizePolicy

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFixedHeight(280)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
            QScrollArea > QWidget > QWidget {
                background: transparent;
            }
            QScrollBar:vertical {
                background: rgba(255, 255, 255, 0.05);
                width: 8px;
                border-radius: 4px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: rgba(255, 255, 255, 0.2);
                border-radius: 4px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: rgba(255, 255, 255, 0.3);
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
                height: 0px;
            }
        """)

        # Folders container widget inside scroll area
        folders_container = QWidget()
        folders_container.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.MinimumExpanding)
        self.folders_list_layout = QVBoxLayout(folders_container)
        self.folders_list_layout.setContentsMargins(0, 0, 8, 10)
        self.folders_list_layout.setSpacing(2)
        self.folders_list_layout.setSizeConstraint(QVBoxLayout.SizeConstraint.SetMinimumSize)

        # Set the folders container as the scroll area's widget
        scroll_area.setWidget(folders_container)

        # Store reference for updates
        self.folders_container = folders_container

        # Add scroll area to main layout instead of direct container
        layout.addWidget(scroll_area)
        return section

    def create_quick_actions_section(self):
        """Clean Quick Actions without gray background"""
        section = QWidget()
        section.setStyleSheet("background: transparent;")

        layout = QVBoxLayout(section)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        # Title
        title = QLabel("Quick Actions")
        title.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        title.setStyleSheet("color: #ffffff; background: transparent;")
        layout.addWidget(title)

        # Action buttons
        actions = [
            ("➕", "Add Password", self.add_entry_to_current_folder),
            ("📁", "New Folder", self.add_folder),
            ("📥", "Import Passwords", self.show_import_dialog)
        ]

        for icon, text, handler in actions:
            btn = QPushButton()
            btn.setFixedHeight(36)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)

            btn_layout = QHBoxLayout(btn)
            btn_layout.setContentsMargins(12, 0, 12, 0)
            btn_layout.setSpacing(8)

            icon_label = QLabel(icon)
            icon_label.setStyleSheet("font-size: 14px; background: transparent;")

            text_label = QLabel(text)
            text_label.setFont(QFont("Segoe UI", 10))
            text_label.setStyleSheet("color: #ffffff; background: transparent;")

            btn_layout.addWidget(icon_label)
            btn_layout.addWidget(text_label, 1)

            btn.setStyleSheet("""
                QPushButton {
                    background: transparent;
                    border: 1px solid rgba(255, 255, 255, 0.1);
                    border-radius: 6px;
                }
                QPushButton:hover {
                    background: rgba(255, 255, 255, 0.05);
                }
            """)

            btn.clicked.connect(handler)
            layout.addWidget(btn)

        return section

    def create_quick_action_button(self, icon, text, handler):
        """Create a quick action button with proper styling"""
        btn = QPushButton()
        btn.setFixedHeight(40)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)

        btn_layout = QHBoxLayout(btn)
        btn_layout.setContentsMargins(12, 0, 12, 0)
        btn_layout.setSpacing(12)

        icon_label = QLabel(icon)
        icon_label.setFixedSize(16, 16)
        icon_label.setStyleSheet("background: transparent; font-size: 14px;")

        text_label = QLabel(text)
        text_label.setFont(QFont("Segoe UI", 10))
        text_label.setStyleSheet("color: #ffffff; background: transparent;")

        btn_layout.addWidget(icon_label)
        btn_layout.addWidget(text_label, 1)

        btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 6px;
                text-align: left;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 0.05);
                border: 1px solid rgba(255, 255, 255, 0.2);
            }
            QPushButton:pressed {
                background: rgba(255, 255, 255, 0.08);
            }
        """)

        btn.clicked.connect(handler)
        return btn

    def create_recent_activity_section(self):
        """Create recent activity section with clean styling"""
        section = QWidget()
        layout = QVBoxLayout(section)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        # Title - white like FOLDERS
        title = QLabel("Recent Activity")
        title.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        title.setStyleSheet("color: #ffffff; background: transparent; letter-spacing: 0.5px;")
        layout.addWidget(title)

        # Activity container - no borders
        activity_container = QWidget()
        activity_layout = QVBoxLayout(activity_container)
        activity_layout.setContentsMargins(0, 0, 0, 0)
        activity_layout.setSpacing(8)

        # Activity items
        activities = [
            ("Steam password updated", "2 min ago"),
            ("Alice shared Netflix", "1 hour ago"),
            ("New folder created", "Yesterday")
        ]

        for activity, time_ago in activities:
            item = self.create_activity_item(activity, time_ago)
            activity_layout.addWidget(item)

        layout.addWidget(activity_container)
        return section

    def create_activity_item(self, activity, time_ago):
        """Create an activity item with dot indicator - no borders"""
        item = QWidget()
        item.setFixedHeight(32)

        layout = QHBoxLayout(item)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # Green dot indicator
        dot = QLabel("●")
        dot.setFixedSize(8, 8)
        dot.setStyleSheet("color: #4CAF50; font-size: 8px; background: transparent;")

        # Activity info
        info_layout = QVBoxLayout()
        info_layout.setSpacing(0)
        info_layout.setContentsMargins(0, 0, 0, 0)

        activity_label = QLabel(activity)
        activity_label.setFont(QFont("Segoe UI", 10))
        activity_label.setStyleSheet("color: #ffffff; background: transparent;")

        time_label = QLabel(time_ago)
        time_label.setFont(QFont("Segoe UI", 8))
        time_label.setStyleSheet("color: #888888; background: transparent;")

        info_layout.addWidget(activity_label)
        info_layout.addWidget(time_label)

        layout.addWidget(dot)
        layout.addLayout(info_layout, 1)

        return item

    def refresh_folders_enhanced(self):
        """Enhanced folder refresh for modern list-style display"""
        # Clear existing folder items
        if hasattr(self, 'folders_list_layout'):
            while self.folders_list_layout.count():
                child = self.folders_list_layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()

            self.folder_buttons.clear()

            # Force clean styling on the container to remove any inherited indicators
            if hasattr(self, 'folders_container'):
                self.folders_container.setStyleSheet("""
                    QWidget {
                        background: transparent;
                        border: none;
                    }
                    QWidget > QWidget {
                        border: none;
                    }
                """)

            # Get vault folders
            vault_folders = list(self.vault_data.get("data", {}).keys())

            if not vault_folders:
                # Show message if no folders
                no_folders_label = QLabel("No folders yet")
                no_folders_label.setStyleSheet("""
                    color: #888888; 
                    font-size: 11px; 
                    background: transparent;
                    border: none;
                    padding: 20px;
                """)
                no_folders_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                self.folders_list_layout.addWidget(no_folders_label)
                return

            # Add enhanced folder items - THIS WAS MISSING!
            for folder_name in vault_folders:
                # Get entry count for this folder
                folder_data = self.vault_data.get("data", {}).get(folder_name, {})
                entry_count = len(folder_data.get("entries", []))

                # Check if this folder is selected
                is_selected = (folder_name == self.selected_folder)

                # Force create our enhanced folder item (not any other method)
                folder_item = self.create_enhanced_folder_item(folder_name, entry_count, is_selected)

                # Store reference
                self.folder_buttons[folder_name] = folder_item

                # Add to layout
                self.folders_list_layout.addWidget(folder_item)

            # Add stretch to push folders to top
            self.folders_list_layout.addStretch()

    def create_enhanced_folder_item(self, folder_name, entry_count, is_selected=False):
        """Create a modern folder list item with enhanced styling"""
        item = QWidget()
        item.setProperty("folderWidget", False)
        item.setFixedHeight(50)
        item.setCursor(Qt.CursorShape.PointingHandCursor)

        # Enhanced folder item styling with unified green border for selected items
        if is_selected:
            item.setStyleSheet("""
                QWidget {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 rgba(76, 175, 80, 0.15), 
                        stop:1 rgba(76, 175, 80, 0.08));
                    border: 2px solid #4CAF50;
                    border-radius: 8px;
                }
                QWidget > QWidget {
                    border: none !important;
                    background: transparent !important;
                }
                QWidget QLabel {
                    background: transparent !important;
                    border: none !important;
                }
                QWidget QLabel:hover, QWidget QLabel:focus, QWidget QLabel:pressed {
                    background: transparent !important;
                    border: none !important;
                }
            """)
        else:
            item.setStyleSheet("""
                QWidget {
                    background: transparent;
                    border: none;
                    border-radius: 8px;
                }
                QWidget:hover {
                    background: rgba(255, 255, 255, 0.06);
                }
                QWidget > QWidget {
                    border: none !important;
                    background: transparent !important;
                }
                QWidget QLabel {
                    background: transparent !important;
                    border: none !important;
                }
                QWidget QLabel:hover, QWidget QLabel:focus, QWidget QLabel:pressed {
                    background: transparent !important;
                    border: none !important;
                }
            """)

        layout = QHBoxLayout(item)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(12)

        # Enhanced folder icon with mouse transparency
        icon_container = QWidget()
        icon_container.setFixedSize(34, 34)
        icon_container.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)

        # Improved folder color mapping
        folder_colors = {
            'Battle.net': '#ff6b6b',
            'Twitch': '#9146ff',
            'Epic Games': '#0078f2',
            'Minecraft': '#00c851',
            'Gmail': '#ea4335',
            'Random Pass': '#666666',
            'Social Media': '#1da1f2',
            'Banking': '#ffa726',
            'Work': '#795548'
        }

        folder_color = folder_colors.get(folder_name, '#666666')

        icon_container.setStyleSheet(f"""
            QWidget {{
                background: {folder_color};
                border-radius: 8px;
                border: none;
            }}
        """)

        # Better folder icon
        icon_layout = QVBoxLayout(icon_container)
        icon_layout.setContentsMargins(0, 0, 0, 0)
        icon_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Use emoji that displays consistently
        folder_icon = QLabel("📂")
        folder_icon.setStyleSheet("color: white; font-size: 18px; background: transparent; border: none;")
        folder_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        folder_icon.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        icon_layout.addWidget(folder_icon)

        # Enhanced text container with mouse transparency
        text_container = QWidget()
        text_container.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        text_layout = QVBoxLayout(text_container)
        text_layout.setContentsMargins(0, 2, 0, 2)
        text_layout.setSpacing(3)

        # Enhanced folder name styling - disable mouse events and interactions
        name_label = QLabel(folder_name)
        name_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Medium))
        name_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        name_label.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        name_label.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        name_color = "#ffffff"
        name_label.setStyleSheet(f"""
            QLabel {{
                color: {name_color}; 
                background: transparent !important; 
                border: none !important;
                font-weight: 500;
            }}
            QLabel:hover {{
                background: transparent !important;
                border: none !important;
            }}
        """)

        # Enhanced entry count styling - disable mouse events and interactions
        count_text = f"{entry_count} password{'s' if entry_count != 1 else ''}"
        count_label = QLabel(count_text)
        count_label.setFont(QFont("Segoe UI", 10))
        count_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        count_label.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        count_label.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        count_color = "#999999"
        count_label.setStyleSheet(f"""
            QLabel {{
                color: #999999 !important; 
                background: transparent !important; 
                border: none !important;
                font-weight: 400;
            }}
            QLabel:hover, QLabel:focus, QLabel:pressed, QLabel:selected {{
                color: #999999 !important;
                background: transparent !important;
                border: none !important;
            }}
        """)

        text_layout.addWidget(name_label)
        text_layout.addWidget(count_label)

        layout.addWidget(icon_container)
        layout.addWidget(text_container, 1)

        # No indicator widget - unified border only!

        # Enhanced click handler
        def on_folder_click(event):
            self.select_folder(folder_name)
            event.accept()

        item.mousePressEvent = on_folder_click

        return item

    def check_security_issues(self, vault_data):
        """Quick check for security issues"""
        if not vault_data:
            return False

        # Simple check - count entries with weak passwords
        weak_count = 0
        for folder_name, folder_data in vault_data.items():
            entries = folder_data.get("entries", [])
            for entry in entries:
                for field in ['Password', 'password']:
                    if field in entry:
                        password = entry[field]
                        if password and len(password) < 8:
                            weak_count += 1
                        break

        return weak_count > 0

    def show_entry_modal(self, entry_idx, entry, schema):
        """Show entry details in a modal dialog"""
        from gui.widgets.modern_widgets import ModernDialog, ModernButton
        from PyQt6.QtWidgets import QVBoxLayout, QLabel, QHBoxLayout, QFrame
        from PyQt6.QtGui import QFont
        from PyQt6.QtCore import Qt

        # Calculate height based on number of fields (more compact)
        field_count = len([field for field in schema if entry.get(field, "")])
        base_height = 180  # Header + buttons + padding
        field_height = field_count * 60  # Each field takes ~60px
        total_height = base_height + field_height

        # Create modal dialog with proper sizing
        modal = ModernDialog(self, "Entry Details")
        modal.setFixedSize(450, total_height)  # Narrower and dynamic height
        modal.setModal(True)
        # DON'T set custom window flags - let ModernDialog handle it

        # Use the standard layout method like other modals
        title = self.get_entry_display_name(entry, schema)
        layout = modal.setup_basic_layout(title)
        layout.addSpacing(10)

        # Entry fields
        for field in schema:
            field_value = entry.get(field, "")
            if field_value:
                field_container = self.create_modal_field(field, field_value, modal)
                layout.addWidget(field_container)

        layout.addStretch()

        # Action buttons at bottom using icons
        from gui.widgets.svg_icons import SvgIcon, Icons
        from PyQt6.QtWidgets import QPushButton
        from PyQt6.QtCore import QSize

        button_layout = QHBoxLayout()

        # Edit button with icon
        edit_btn = QPushButton()
        edit_btn.setFixedSize(40, 40)
        edit_icon = SvgIcon.create_icon(Icons.EDIT, QSize(18, 18), "#ffffff")
        edit_btn.setIcon(edit_icon)
        edit_btn.setToolTip("Edit Entry")
        edit_btn.setStyleSheet("""
            QPushButton {
                background: rgba(255, 255, 255, 0.1);
                border: 2px solid rgba(255, 255, 255, 0.25);
                border-radius: 8px;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 0.15);
                border: 2px solid rgba(255, 255, 255, 0.35);
            }
        """)
        edit_btn.clicked.connect(lambda: (modal.accept(), self.edit_entry(entry_idx, entry)))

        # Delete button with icon
        delete_btn = QPushButton()
        delete_btn.setFixedSize(40, 40)
        delete_icon = SvgIcon.create_icon(Icons.DELETE, QSize(18, 18), "#ffffff")
        delete_btn.setIcon(delete_icon)
        delete_btn.setToolTip("Delete Entry")
        delete_btn.setStyleSheet("""
            QPushButton {
                background: rgba(255, 71, 87, 0.2);
                border: 2px solid #ff4757;
                border-radius: 8px;
            }
            QPushButton:hover {
                background: rgba(255, 71, 87, 0.3);
            }
        """)
        delete_btn.clicked.connect(lambda: (modal.accept(), self.delete_entry(entry_idx)))

        close_btn = ModernButton("Close", primary=True)
        close_btn.clicked.connect(modal.accept)

        button_layout.addWidget(edit_btn)
        button_layout.addWidget(delete_btn)
        button_layout.addStretch()
        button_layout.addWidget(close_btn)

        layout.addLayout(button_layout)

        # Show modal (this blocks until closed)
        modal.exec()

    def create_modal_field(self, field_name, field_value, modal_parent):
        """Create a field display for the modal with proper eye toggle functionality"""
        from gui.widgets.svg_icons import SvgIcon, Icons
        from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton
        from PyQt6.QtGui import QFont
        from PyQt6.QtCore import QSize

        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(15)

        # Field label
        label = QLabel(f"{field_name}:")
        label.setFont(QFont("Segoe UI", 12, QFont.Weight.Medium))
        label.setStyleSheet("color: #ffffff; background: transparent;")
        label.setFixedWidth(100)

        # Field value
        if field_name.lower() == "password":
            value_label = QLabel("••••••••")
            value_label.setStyleSheet("color: #888888; font-family: monospace; background: transparent;")

            # Eye button with proper toggle state
            eye_btn = QPushButton()
            eye_btn.setFixedSize(32, 32)

            # Create both icons
            eye_icon = SvgIcon.create_icon(Icons.EYE, QSize(16, 16), "#ffffff")
            eye_off_icon = SvgIcon.create_icon(Icons.EYE_OFF, QSize(16, 16), "#ffffff")

            # Set initial state
            eye_btn.setIcon(eye_icon)
            eye_btn.setStyleSheet("""
                QPushButton {
                    background: rgba(255, 255, 255, 0.08);
                    border: 1px solid rgba(255, 255, 255, 0.15);
                    border-radius: 6px;
                }
                QPushButton:hover {
                    background: rgba(255, 255, 255, 0.15);
                }
            """)

            # Track visibility state on the button itself
            eye_btn.password_visible = False

            def toggle_password():
                if not eye_btn.password_visible:
                    # Show confirmation before revealing
                    def reveal():
                        value_label.setText(field_value)
                        value_label.setStyleSheet("color: #ffffff; font-family: monospace; background: transparent;")
                        # Change to eye-off icon
                        eye_btn.setIcon(eye_off_icon)
                        eye_btn.setToolTip("Hide password")
                        eye_btn.password_visible = True

                    self.show_password_confirmation_modal(reveal, modal_parent)
                else:
                    # Hide password directly (no confirmation needed)
                    value_label.setText("••••••••")
                    value_label.setStyleSheet("color: #888888; font-family: monospace; background: transparent;")
                    # Change back to eye icon
                    eye_btn.setIcon(eye_icon)
                    eye_btn.setToolTip("Show password")
                    eye_btn.password_visible = False

            eye_btn.clicked.connect(toggle_password)
            eye_btn.setToolTip("Show password")

            layout.addWidget(label)
            layout.addWidget(value_label, 1)
            layout.addWidget(eye_btn)
        else:
            value_label = QLabel(field_value)
            value_label.setStyleSheet("color: #ffffff; background: transparent;")
            layout.addWidget(label)
            layout.addWidget(value_label, 1)

        # Copy button with feedback animation
        copy_btn = QPushButton()
        copy_btn.setFixedSize(32, 32)
        copy_icon = SvgIcon.create_icon(Icons.COPY, QSize(16, 16), "#ffffff")
        copy_btn.setIcon(copy_icon)
        copy_btn.setStyleSheet("""
            QPushButton {
                background: rgba(255, 255, 255, 0.08);
                border: 1px solid rgba(255, 255, 255, 0.15);
                border-radius: 6px;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 0.15);
            }
        """)

        def copy_with_feedback():
            # Copy to clipboard
            self.copy_to_clipboard(field_value)

            # Show checkmark feedback
            from PyQt6.QtCore import QTimer
            check_icon = SvgIcon.create_icon(Icons.SECURITY, QSize(16, 16),
                                             "#4CAF50")  # Using SECURITY icon which has checkmark
            copy_btn.setIcon(check_icon)
            copy_btn.setStyleSheet("""
                QPushButton {
                    background: rgba(76, 175, 80, 0.2);
                    border: 1px solid #4CAF50;
                    border-radius: 6px;
                }
            """)

            # Reset to original after 1 second
            def reset_icon():
                copy_btn.setIcon(copy_icon)
                copy_btn.setStyleSheet("""
                    QPushButton {
                        background: rgba(255, 255, 255, 0.08);
                        border: 1px solid rgba(255, 255, 255, 0.15);
                        border-radius: 6px;
                    }
                    QPushButton:hover {
                        background: rgba(255, 255, 255, 0.15);
                    }
                """)

            QTimer.singleShot(1000, reset_icon)

        copy_btn.clicked.connect(copy_with_feedback)
        copy_btn.setToolTip(f"Copy {field_name.lower()}")
        layout.addWidget(copy_btn)

        return container

    def show_password_confirmation_modal(self, callback, parent_modal):
        """Show confirmation dialog with proper parent and click-outside-to-close"""
        from gui.widgets.modern_widgets import ModernDialog, ModernButton
        from PyQt6.QtWidgets import QVBoxLayout, QLabel, QHBoxLayout
        from PyQt6.QtCore import Qt

        dialog = ModernDialog(parent_modal, "Show Password")
        dialog.setFixedSize(350, 180)
        dialog.setModal(True)

        # Enable click outside to close by connecting backdrop
        def handle_mouse_press(event):
            # Check if click is outside the dialog content area
            if event.button() == Qt.MouseButton.LeftButton:
                widget_under_cursor = dialog.childAt(event.pos())
                if widget_under_cursor is None:
                    dialog.reject()
                    return
            # Call the original event handler for normal behavior
            QDialog.mousePressEvent(dialog, event)

        from PyQt6.QtWidgets import QDialog
        dialog.mousePressEvent = handle_mouse_press

        layout = QVBoxLayout(dialog)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Header
        header_label = QLabel("Show Password")
        header_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #4CAF50; background: transparent;")
        layout.addWidget(header_label)

        # Warning message
        warning_label = QLabel("Are you sure you want to reveal this password?")
        warning_label.setStyleSheet("color: #ffffff; font-size: 12px; background: transparent;")
        warning_label.setWordWrap(True)
        layout.addWidget(warning_label)

        layout.addStretch()

        # Buttons
        button_layout = QHBoxLayout()

        cancel_btn = ModernButton("Cancel", primary=False)
        cancel_btn.clicked.connect(dialog.reject)

        show_btn = ModernButton("Show Password", primary=True)
        show_btn.clicked.connect(lambda: (dialog.accept(), callback()))

        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(show_btn)
        layout.addLayout(button_layout)

        dialog.exec()

    def get_security_issues(self, vault_data):
        """Get basic security issues"""
        issues = []

        weak_count = 0
        for folder_name, folder_data in vault_data.items():
            entries = folder_data.get("entries", [])
            for entry in entries:
                for field in ['Password', 'password']:
                    if field in entry:
                        password = entry[field]
                        if password and len(password) < 8:
                            weak_count += 1
                        break

        if weak_count > 0:
            issues.append({
                'severity': 'high',
                'message': f'{weak_count} weak passwords found'
            })

        return issues

    def add_entry_to_current_folder(self):
        """Add entry to currently selected folder"""
        if not self.selected_folder:
            # Get first folder if none selected
            vault_folders = list(self.vault_data.get("data", {}).keys())
            if vault_folders:
                self.select_folder(vault_folders[0])
            else:
                # No folders exist, create one first
                self.add_folder()
                return

        self.add_entry_to_folder()

    def show_import_dialog(self):
        """Show import dialog placeholder"""
        from gui.widgets.modern_widgets import ModernDialog, ModernButton

        dialog = ModernDialog(self, "Import Passwords")
        dialog.setFixedSize(400, 200)

        layout = QVBoxLayout(dialog)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        header_label = QLabel("Import Feature")
        header_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #4CAF50;")
        layout.addWidget(header_label)

        desc_label = QLabel("Import from other password managers coming soon!")
        desc_label.setStyleSheet("color: #ffffff; font-size: 12px;")
        layout.addWidget(desc_label)

        layout.addStretch()

        close_btn = ModernButton("Close", primary=True)
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn)

        dialog.exec()

    def create_folders_section(self):
        group = QGroupBox("📁 FOLDERS")
        group.setStyleSheet("""
            QGroupBox {
                color: #ffffff;
                font-weight: bold;
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)

        layout = QVBoxLayout(group)
        layout.setSpacing(15)

        # Add New Folder button
        new_folder_btn = QPushButton("+ New Folder")
        new_folder_btn.setFixedHeight(35)
        new_folder_btn.setStyleSheet("""
            QPushButton {
                background: rgba(76, 175, 80, 0.2);
                border: 2px solid rgba(76, 175, 80, 0.5);
                border-radius: 8px;
                color: #4CAF50;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background: rgba(76, 175, 80, 0.3);
                border: 2px solid rgba(76, 175, 80, 0.7);
            }
            QPushButton:pressed {
                background: rgba(76, 175, 80, 0.4);
            }
        """)
        new_folder_btn.clicked.connect(self.add_folder)
        layout.addWidget(new_folder_btn)

        # Create scroll area for folder grid
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFixedHeight(460)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background: #2d2d30;  /* Solid color instead of transparent */
            }
            QScrollArea > QWidget > QWidget {
                background: #2d2d30;  /* Target the internal content widget */
            }
            QScrollBar:vertical {
                background-color: #2d2d30;  /* Use background-color instead */
                width: 12px;
                border-radius: 6px;
                margin: 0px;
                border: none;
            }
            QScrollBar::handle:vertical {
                background-color: rgba(255, 255, 255, 0.2);
                border-radius: 6px;
                min-height: 20px;
                border: none;
            }
            QScrollBar::handle:vertical:hover {
                background-color: rgba(255, 255, 255, 0.3);
            }
            QScrollBar::handle:vertical:pressed {
                background-color: rgba(255, 255, 255, 0.4);
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
                height: 0px;
                width: 0px;
            }
            QScrollBar::sub-page:vertical, QScrollBar::add-page:vertical {
                background: #2d2d30;  /* This targets the track areas */
            }
        """)

        # Create widget to hold the grid
        grid_widget = QWidget()
        self.folders_layout = QGridLayout(grid_widget)
        self.folders_layout.setSpacing(10)
        self.folders_layout.setContentsMargins(10, 10, 10, 10)

        scroll_area.setWidget(grid_widget)
        layout.addWidget(scroll_area)

        return group

    def create_right_panel(self):
        """Create the main content area with card layout"""
        right_widget = QWidget()
        right_widget.setStyleSheet("""
            QWidget {
                background: #1a1a1d;
            }
        """)

        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(24, 24, 24, 24)
        right_layout.setSpacing(20)

        # Header section
        header_section = self.create_entries_header()
        right_layout.addWidget(header_section)

        # Password cards container - BACK TO GRID LAYOUT
        self.cards_container = QWidget()
        self.cards_layout = QGridLayout(self.cards_container)  # Back to QGridLayout
        self.cards_layout.setContentsMargins(0, 0, 0, 0)
        self.cards_layout.setSpacing(16)
        self.cards_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Set column stretch to make cards fill available width equally
        self.cards_layout.setColumnStretch(0, 1)
        self.cards_layout.setColumnStretch(1, 1)

        # Scroll area for password cards
        scroll_area = QScrollArea()
        scroll_area.setWidget(self.cards_container)
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
            QScrollBar:vertical {
                background: rgba(255, 255, 255, 0.05);
                width: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background: rgba(255, 255, 255, 0.2);
                border-radius: 4px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: rgba(255, 255, 255, 0.3);
            }
        """)

        right_layout.addWidget(scroll_area)
        return right_widget

    def create_entries_header(self):
        """Create header that matches mockup style"""
        header = QWidget()
        header.setFixedHeight(80)

        layout = QHBoxLayout(header)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        # Left side - Folder title with subtitle and action icons below
        left_layout = QVBoxLayout()
        left_layout.setSpacing(4)

        # Main title - just the folder name
        self.folder_title = QLabel("Select a Folder")
        self.folder_title.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        self.folder_title.setStyleSheet("color: #ffffff; background: transparent;")

        # Subtitle
        self.folder_subtitle = QLabel("Choose a folder to view passwords")
        self.folder_subtitle.setFont(QFont("Segoe UI", 12))
        self.folder_subtitle.setStyleSheet("color: #888888; background: transparent;")

        # Small action icons below subtitle
        self.folder_actions_widget = QWidget()
        actions_layout = QHBoxLayout(self.folder_actions_widget)
        actions_layout.setContentsMargins(0, 0, 0, 0)
        actions_layout.setSpacing(8)

        # Edit icon
        edit_btn = QPushButton()
        edit_btn.setFixedSize(24, 24)
        edit_icon = SvgIcon.create_icon(Icons.EDIT, QSize(16, 16), "#ffffff")
        edit_btn.setIcon(edit_icon)
        edit_btn.setIconSize(QSize(16, 16))
        edit_btn.setStyleSheet("""
            QPushButton {
                background: rgba(255, 255, 255, 0.08);
                border: 1px solid rgba(255, 255, 255, 0.15);
                border-radius: 4px;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 0.15);
            }
        """)
        edit_btn.clicked.connect(self.edit_folder)

        # Delete icon
        delete_btn = QPushButton()
        delete_btn.setFixedSize(24, 24)
        delete_icon = SvgIcon.create_icon(Icons.DELETE, QSize(16, 16), "#ffffff")
        delete_btn.setIcon(delete_icon)
        delete_btn.setIconSize(QSize(16, 16))
        delete_btn.setStyleSheet("""
            QPushButton {
                background: rgba(255, 255, 255, 0.08);
                border: 1px solid rgba(255, 255, 255, 0.15);
                border-radius: 4px;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 0.15);
            }
        """)
        delete_btn.clicked.connect(self.delete_folder)

        actions_layout.addWidget(edit_btn)
        actions_layout.addWidget(delete_btn)
        actions_layout.addStretch()

        # Hide actions initially
        self.folder_actions_widget.hide()

        left_layout.addWidget(self.folder_title)
        left_layout.addWidget(self.folder_subtitle)
        left_layout.addWidget(self.folder_actions_widget)

        layout.addLayout(left_layout)
        layout.addStretch()

        # Right side - Add Password button only
        self.add_password_btn = QPushButton("Add Password")
        self.add_password_btn.setFixedHeight(40)
        add_icon = SvgIcon.create_icon(Icons.PLUS, QSize(16, 16), "#ffffff")
        self.add_password_btn.setIcon(add_icon)
        self.add_password_btn.setIconSize(QSize(16, 16))
        self.add_password_btn.setStyleSheet("""
            QPushButton {
                background: rgba(255, 255, 255, 0.08);
                border: 1px solid rgba(255, 255, 255, 0.15);
                border-radius: 8px;
                color: #ffffff;
                font-size: 12px;
                font-weight: 600;
                padding: 0px 24px;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 0.15);
            }
        """)
        self.add_password_btn.clicked.connect(self.add_entry_to_folder)
        self.add_password_btn.hide()  # Hide initially

        layout.addWidget(self.add_password_btn)

        return header

    def create_password_card(self, entry_idx, entry, schema):
        """Create modern password card with proper styling and hover effects"""
        card = QWidget()
        card.setFixedHeight(100)  # Increased height for better proportions
        card.setMaximumWidth(500)
        card.setMinimumWidth(350)

        # Modern card styling with depth, elevation, and shadows
        card.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #404043, stop:1 #373739);
                border: 1px solid rgba(255, 255, 255, 0.12);
                border-radius: 12px;
                cursor: pointer;
            }
            QWidget:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4a4a4d, stop:1 #404043);
                border: 1px solid rgba(255, 255, 255, 0.25);
            }
        """)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(8)

        # Top row - Title and status indicator
        top_row = QHBoxLayout()
        top_row.setSpacing(0)

        # Entry title (larger and more prominent, no borders)
        title = self.get_entry_display_name(entry, schema)
        title_label = QLabel(title)
        title_label.setFont(QFont("Segoe UI", 15, QFont.Weight.DemiBold))
        title_label.setStyleSheet("""
            color: #ffffff; 
            background: transparent;
            font-weight: 600;
            border: none;
            padding: 0px;
        """)
        title_label.setWordWrap(False)

        top_row.addWidget(title_label)
        top_row.addStretch()

        layout.addLayout(top_row)

        # Bottom row - Username/email as plain text (no input field)
        username = self.get_entry_username(entry, schema)
        if username:
            username_label = QLabel(username)
            username_label.setFont(QFont("Segoe UI", 12))
            username_label.setStyleSheet("""
                color: #b0b0b0; 
                background: transparent;
                font-weight: 400;
                border: none;
                padding: 0px;
            """)
            username_label.setWordWrap(False)
            layout.addWidget(username_label)
        else:
            # If no username, add spacing to maintain card height
            layout.addSpacing(18)

        layout.addStretch()

        # Card click handler with smooth animation feel
        def open_modal(event):
            # Add subtle visual feedback before opening modal
            card.setStyleSheet(card.styleSheet() + """
                QWidget {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #4a4a4d, stop:1 #454548);
                }
            """)

            # Open modal after brief delay for visual feedback
            QTimer.singleShot(50, lambda: self.show_entry_modal(entry_idx, entry, schema))
            event.accept()

        card.mousePressEvent = open_modal

        return card

    def get_entry_username(self, entry, schema):
        """Extract username/email from entry"""
        username_fields = ['Username', 'username', 'User', 'user', 'Email', 'email']
        for field in username_fields:
            if field in entry and entry[field]:
                return entry[field]
        return None

    def get_entry_password(self, entry, schema):
        """Extract password from entry"""
        password_fields = ['Password', 'password', 'Pass', 'pass']
        for field in password_fields:
            if field in entry and entry[field]:
                return entry[field]
        return ""

    def refresh_entries_cards(self):
        """Refresh entries using card layout with proper header"""
        # Clear existing cards
        while self.cards_layout.count():
            child = self.cards_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        if not self.selected_folder:
            # Update header for no selection and hide buttons
            self.folder_title.setText("Select a Folder")
            self.folder_subtitle.setText("Choose a folder to view passwords")
            self.folder_actions_widget.hide()
            self.add_password_btn.hide()

            # Show "no folder selected" message (spans full width)
            no_folder_card = self.create_no_folder_message()
            self.cards_layout.addWidget(no_folder_card, 0, 0, 1, 2)  # Back to grid positioning
            return

        # Show buttons when folder is selected
        self.folder_actions_widget.show()
        self.add_password_btn.show()

        # Get folder data
        folder_data = self.vault_data.get("data", {}).get(self.selected_folder)
        if not folder_data:
            self.folder_title.setText("Error")
            self.folder_subtitle.setText("")
            self.folder_actions_widget.hide()
            self.add_password_btn.hide()
            error_card = self.create_error_message(f"Folder '{self.selected_folder}' not found")
            self.cards_layout.addWidget(error_card, 0, 0, 1, 2)  # Back to grid positioning
            return

        # Update header with folder info
        entries = folder_data.get("entries", [])
        entry_count = len(entries)

        # Update header to match mockup style
        self.folder_title.setText(self.selected_folder)
        self.folder_subtitle.setText(f"{entry_count} passwords • Last updated 2 days ago")

        # Get schema
        schema = folder_data.get("schema", ["Title", "Username", "Password"])

        if not entries:
            # Show add new entry button (spans full width)
            no_entries_card = self.create_no_entries_message()
            self.cards_layout.addWidget(no_entries_card, 0, 0, 1, 2)
        else:
            # Add password cards in grid layout (2 per row) - BACK TO GRID
            cards_per_row = 2
            for entry_idx, entry in enumerate(entries):
                row = entry_idx // cards_per_row
                col = entry_idx % cards_per_row
                card = self.create_password_card(entry_idx, entry, schema)
                self.cards_layout.addWidget(card, row, col)

    def create_no_folder_message(self):
        """Create message widget when no folder is selected"""
        message_card = QWidget()
        message_card.setStyleSheet("""
            QWidget {
                background: transparent;
            }
        """)

        layout = QVBoxLayout(message_card)
        layout.setSpacing(8)
        layout.setContentsMargins(0, 0, 0, 0)

        # Add stretch at top to push content to center
        layout.addStretch(2)

        # Use SVG folder icon instead of emoji
        icon_label = QLabel()
        folder_icon = SvgIcon.create_icon(Icons.FOLDER, QSize(48, 48), "#666666")
        icon_label.setPixmap(folder_icon.pixmap(48, 48))
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setStyleSheet("background: transparent;")

        title = QLabel("No Folder Selected")
        title.setFont(QFont("Segoe UI", 14, QFont.Weight.Medium))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: #ffffff; background: transparent;")

        subtitle = QLabel("Choose a folder from the sidebar to view your passwords")
        subtitle.setFont(QFont("Segoe UI", 11))
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("color: #888888; background: transparent;")

        layout.addWidget(icon_label)
        layout.addWidget(title)
        layout.addWidget(subtitle)

        # Add stretch at bottom to center content vertically
        layout.addStretch(3)

        return message_card

    def create_no_entries_message(self):
        """Updated no entries message to match mockup"""
        message_card = QWidget()
        message_card.setFixedHeight(160)
        message_card.setStyleSheet("""
            QWidget {
                background: transparent;
            }
        """)

        layout = QVBoxLayout(message_card)
        layout.setSpacing(16)

        # Large add button in center
        add_btn = QPushButton("+ ADD NEW ENTRY")
        add_btn.setFixedHeight(48)
        add_btn.setFixedWidth(200)
        add_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: 2px dashed rgba(76, 175, 80, 0.5);
                border-radius: 12px;
                color: #4CAF50;
                font-size: 13px;
                font-weight: 600;
                letter-spacing: 0.5px;
            }
            QPushButton:hover {
                background: rgba(76, 175, 80, 0.05);
                border: 2px dashed rgba(76, 175, 80, 0.7);
            }
        """)
        add_btn.clicked.connect(self.add_entry_to_folder)

        # Center the button
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(add_btn)
        button_layout.addStretch()

        layout.addStretch()
        layout.addLayout(button_layout)
        layout.addStretch()

        return message_card

    def create_error_message(self, error_text):
        """Create error message widget"""
        error_card = QWidget()
        error_card.setFixedHeight(100)
        error_card.setStyleSheet("""
            QWidget {
                background: transparent;
            }
        """)

        layout = QVBoxLayout(error_card)
        layout.setSpacing(8)

        icon = QLabel("⚠️")
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon.setStyleSheet("font-size: 24px; background: transparent;")

        text = QLabel(error_text)
        text.setFont(QFont("Segoe UI", 12))
        text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        text.setStyleSheet("color: #ff4757; background: transparent;")

        layout.addWidget(icon)
        layout.addWidget(text)

        return error_card

    def refresh_entries(self):
        """Main method to refresh entries - now uses card layout"""
        self.refresh_entries_cards()

    def create_status_bar(self, parent_layout):
        status_bar = QFrame()
        status_bar.setFixedHeight(30)
        status_bar.setStyleSheet("""
            QFrame {
                background: #1a1a1d; 
                border-top: 1px solid rgba(255, 255, 255, 0.08);
                border-bottom-left-radius: 15px;
                border-bottom-right-radius: 15px;

            }
        """)

        status_layout = QHBoxLayout(status_bar)
        status_layout.setContentsMargins(20, 5, 20, 5)

        status_layout.addStretch()

        version_label = QLabel(get_current_version())
        version_label.setStyleSheet("color: #ffffff; font-size: 10px;")
        status_layout.addWidget(version_label)

        parent_layout.addWidget(status_bar)

    def load_vault_data(self, vault_data, username, vault_key):
        # Structure vault data
        self.vault_data = {
            "username": username,
            "data": vault_data
        }
        self.vault_key = vault_key
        self.selected_folder = None

        from gui.analytics_manager import update_vault_stats
        update_vault_stats(vault_data)

        # CHANGE: Use the enhanced refresh method
        self.refresh_folders_enhanced()  # Instead of self.refresh_folders()
        self.refresh_entries_cards()

        return True

    def refresh_folders(self):
        # Clear existing folder buttons
        while self.folders_layout.count():
            child = self.folders_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        self.folder_buttons.clear()

        # Get vault folders
        vault_folders = list(self.vault_data.get("data", {}).keys())

        if not vault_folders:
            # Show message if no folders
            no_folders_label = QLabel("No folders yet. Click '+ New Folder' to create one.")
            no_folders_label.setStyleSheet("color: #888888; font-size: 12px;")
            no_folders_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.folders_layout.addWidget(no_folders_label, 0, 0, 1, 2)
            self.folders_layout.parentWidget().setMinimumHeight(100)
            return

        # Add folder buttons with 2-column layout
        for i, folder_name in enumerate(vault_folders):
            row = i // 2
            col = i % 2

            folder_btn = QPushButton(folder_name)
            folder_btn.setFixedSize(140, 100)

            # Store button reference
            self.folder_buttons[folder_name] = folder_btn

            folder_btn.setStyleSheet(self.get_folder_button_style(False))
            folder_btn.clicked.connect(lambda checked, name=folder_name: self.select_folder(name))

            self.folders_layout.addWidget(folder_btn, row, col)

        # Calculate proper height
        rows_needed = (len(vault_folders) + 1) // 2

        if rows_needed <= 4:
            content_height = rows_needed * 110 + 20
            self.folders_layout.parentWidget().setFixedHeight(content_height)
        else:
            # 🔧 KEY FIX: Set minimum height for scroll area to work
            scroll_height = rows_needed * 110 + 20  # Total content height
            self.folders_layout.parentWidget().setMinimumHeight(scroll_height)

            # Reset any fixed height constraint
            self.folders_layout.parentWidget().setMaximumHeight(16777215)  # Qt's max

    def refresh_entries(self):
        """Main method to refresh entries - now uses card layout"""
        self.refresh_entries_cards()

    def get_folder_button_style(self, is_selected=False):
        if is_selected:
            return """
                QPushButton {
                    background: rgba(255, 255, 255, 0.12);
                    border: 2px solid #4CAF50;
                    border-radius: 8px;
                    color: #ffffff;
                    font-weight: bold;
                    font-size: 11px;
                    text-align: center;
                }
                QPushButton:hover {
                    background: rgba(255, 255, 255, 0.18);
                    border: 2px solid #4CAF50;
                }
                QPushButton:pressed {
                    background: rgba(255, 255, 255, 0.25);
                }
            """
        else:
            return """
                QPushButton {
                    background: rgba(255, 255, 255, 0.08);
                    border: 1px solid rgba(255, 255, 255, 0.15);
                    border-radius: 8px;
                    color: #ffffff;
                    font-weight: bold;
                    font-size: 11px;
                    text-align: center;
                }
                QPushButton:hover {
                    background: rgba(255, 255, 255, 0.15);
                    border: 1px solid rgba(255, 255, 255, 0.25);
                }
                QPushButton:pressed {
                    background: rgba(255, 255, 255, 0.2);
                }
            """

    def select_folder(self, folder_name):
        self.selected_folder = folder_name

        # CHANGE: Use enhanced refresh to update styling
        self.refresh_folders_enhanced()
        self.refresh_entries_cards()

    def create_entry_widget(self, entry_idx, entry, schema):
        # Get display name
        display_name = self.get_entry_display_name(entry, schema)

        # Main entry frame
        entry_frame = ModernEntryFrame()

        entry_layout = QVBoxLayout(entry_frame)
        entry_layout.setSpacing(0)
        entry_layout.setContentsMargins(0, 0, 0, 0)

        # Collapsible header
        header_btn = ModernEntryHeader(f"▶ {display_name}")

        # Content widget
        content_widget = QWidget()
        content_widget.setVisible(False)
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(8)
        content_layout.setContentsMargins(15, 10, 15, 15)

        # Entry fields
        for field in schema:
            if field.lower() == 'title':
                continue

            field_value = entry.get(field, "")
            if field_value:
                field_layout = QHBoxLayout()

                field_label = QLabel(f"{field}:")
                field_label.setFont(QFont("Segoe UI", 10))
                field_label.setStyleSheet("color: #b0b0b0;")
                field_label.setFixedWidth(80)

                if field.lower() == "password":
                    value_label = QLabel("••••••••")
                    value_label.setStyleSheet("color: #888888; font-family: monospace;")

                    show_btn = ModernSmallButton("Show")
                    show_btn.setFixedSize(50, 25)

                    # Store the password value for toggling
                    def make_toggle_password(btn, label, value):
                        def toggle():
                            if btn.text() == "Show":
                                # Show confirmation before revealing
                                self.show_password_confirmation(lambda: reveal_password())
                            else:
                                label.setText("••••••••")
                                label.setStyleSheet("color: #888888; font-family: monospace;")
                                btn.setText("Show")

                        def reveal_password():
                            label.setText(value)
                            label.setStyleSheet("color: #ffffff; font-family: monospace;")
                            btn.setText("Hide")

                        return toggle

                    show_btn.clicked.connect(make_toggle_password(show_btn, value_label, field_value))
                else:
                    value_label = QLabel(field_value)
                    value_label.setStyleSheet("color: #ffffff;")
                    show_btn = None

                copy_btn = ModernSmallButton("Copy")
                copy_btn.setFixedSize(50, 25)
                copy_btn.clicked.connect(lambda checked, val=field_value: self.copy_to_clipboard(val))

                field_layout.addWidget(field_label)
                field_layout.addWidget(value_label, 1)
                if show_btn:
                    field_layout.addWidget(show_btn)
                field_layout.addWidget(copy_btn)

                content_layout.addLayout(field_layout)

        # Action buttons
        action_layout = QHBoxLayout()
        action_layout.addStretch()

        edit_btn = ModernSmallButton("✏️ Edit")
        edit_btn.setFixedSize(70, 30)
        edit_btn.clicked.connect(lambda: self.edit_entry(entry_idx, entry))

        delete_btn = ModernSmallButton("🗑️ Delete", delete_style=True)
        delete_btn.setFixedSize(80, 30)
        delete_btn.clicked.connect(lambda: self.delete_entry(entry_idx))

        action_layout.addWidget(edit_btn)
        action_layout.addWidget(delete_btn)
        content_layout.addLayout(action_layout)



        # Toggle function
        def toggle_content():
            is_visible = content_widget.isVisible()
            content_widget.setVisible(not is_visible)
            header_btn.set_expanded(not is_visible)
            entry_frame.set_expanded(not is_visible)

            # Update frame border based on expansion
            if not is_visible:
                entry_frame.setStyleSheet("""
                   QFrame[entryWidget="true"] {
                       background: rgba(255, 255, 255, 0.08);
                       border: 2px solid #4CAF50;
                       border-radius: 8px;
                       margin: 2px;
                   }
               """)
            else:
                entry_frame.setStyleSheet("""
                   QFrame[entryWidget="true"] {
                       background: rgba(255, 255, 255, 0.08);
                       border: 1px solid rgba(255, 255, 255, 0.15);
                       border-radius: 8px;
                       margin: 2px;
                   }
               """)

        header_btn.clicked.connect(toggle_content)

        entry_layout.addWidget(header_btn)
        entry_layout.addWidget(content_widget)

        return entry_frame

    def get_entry_display_name(self, entry, schema):
        title_fields = ['title', 'name', 'label']

        # Check for title fields
        for title_field in title_fields:
            for field_name in entry.keys():
                if field_name.lower() == title_field and entry[field_name] and str(entry[field_name]).strip():
                    return str(entry[field_name]).strip()

        # Fallback to other fields
        fallback_fields = ['site', 'website', 'service', 'account', 'app']
        for field in fallback_fields:
            if field in entry and entry[field] and str(entry[field]).strip():
                return str(entry[field]).strip()

        # Use any non-empty field
        for field in schema:
            if field in entry and entry[field] and str(entry[field]).strip():
                value = str(entry[field]).strip()
                if field.lower() == "password":
                    return "Password Entry"
                if '@' in value and field.lower() in ['email', 'username']:
                    return value.split('@')[0]
                return value[:25] + "..." if len(value) > 25 else value

        return "Unnamed Entry"

    def show_password_confirmation(self, callback):
        """Show confirmation dialog before revealing password"""
        from gui.widgets.modern_widgets import ModernDialog, ModernButton
        from PyQt6.QtWidgets import QVBoxLayout, QLabel, QHBoxLayout

        dialog = ModernDialog(self, "Show Password")
        dialog.setFixedSize(350, 180)

        dialog.setStyleSheet("""
            QDialog {
                background: #2d2d30;
                border: 2px solid #4CAF50;
                border-radius: 12px;
            }
            QLabel {
                background: transparent;
            }
        """)

        layout = QVBoxLayout(dialog)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Header
        header_label = QLabel("Show Password")
        header_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #4CAF50; background: transparent;")
        layout.addWidget(header_label)

        # Warning message
        warning_label = QLabel("Are you sure you want to reveal this password?")
        warning_label.setStyleSheet("color: #ffffff; font-size: 12px; background: transparent;")
        warning_label.setWordWrap(True)
        layout.addWidget(warning_label)

        layout.addStretch()

        # Buttons
        button_layout = QHBoxLayout()

        cancel_btn = ModernButton("Cancel", primary=False)
        cancel_btn.clicked.connect(dialog.reject)

        show_btn = ModernButton("Show Password", primary=True)
        show_btn.clicked.connect(lambda: (dialog.accept(), callback()))

        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(show_btn)
        layout.addLayout(button_layout)

        dialog.exec()

    def copy_to_clipboard(self, text):
        from PyQt6.QtWidgets import QApplication
        from gui.analytics_manager import increment_counter

        clipboard = QApplication.clipboard()
        clipboard.setText(text)
        increment_counter("feature_usage.copy_password_clicks")

    def add_entry_to_folder(self):
        if not self.selected_folder:
            return

        folder_data = self.vault_data.get("data", {}).get(self.selected_folder)
        if not folder_data:
            return

        schema = folder_data.get("schema", ["Title", "Username", "Password"])

        # Create dialog
        dialog_height = 350 + (len(schema) * 40)
        dialog = ModernDialog(self, f"Add Entry to: {self.selected_folder}")
        dialog.setFixedSize(450, dialog_height)

        layout = dialog.setup_basic_layout(f"Add entry to folder: {self.selected_folder}")
        layout.addSpacing(20)

        # Input fields
        input_fields = {}
        for i, field in enumerate(schema):
            field_container = QWidget()
            field_container.setFixedHeight(60)
            field_layout = QVBoxLayout(field_container)
            field_layout.setContentsMargins(0, 0, 0, 0)
            field_layout.setSpacing(5)

            label = QLabel(f"{field}:")
            label.setStyleSheet("color: #ffffff; font-size: 12px;")
            label.setFixedHeight(20)

            if field.lower() == "password":
                input_field = ModernLineEdit()
                input_field.setEchoMode(QLineEdit.EchoMode.Password)
            else:
                input_field = ModernLineEdit()

            input_field.setFixedHeight(35)
            input_fields[field] = input_field

            field_layout.addWidget(label)
            field_layout.addWidget(input_field)

            layout.addWidget(field_container)

            if i < len(schema) - 1:
                layout.addSpacing(10)

        layout.addSpacing(20)

        # Error message
        error_label = QLabel("")
        error_label.setStyleSheet("color: #ff4757; font-size: 11px;")
        error_label.setFixedHeight(20)
        layout.addWidget(error_label)

        layout.addSpacing(15)
        layout.addStretch()

        # Buttons
        button_layout = QHBoxLayout()

        cancel_btn = ModernButton("Cancel", primary=False)
        cancel_btn.clicked.connect(dialog.reject)

        add_btn = ModernButton("Add Entry", primary=True)
        add_btn.setDefault(True)

        def confirm_add():
            new_entry = {}
            for field, input_field in input_fields.items():
                value = input_field.text().strip()
                if not value:
                    error_label.setText("All fields are required")
                    return
                new_entry[field] = value

            # Add to vault data
            self.vault_data["data"][self.selected_folder]["entries"].append(new_entry)

            # Save to backend
            from core.vault_manager import save_vault
            save_vault(self.vault_data["data"], self.vault_key)

            from gui.analytics_manager import update_vault_stats
            update_vault_stats(self.vault_data["data"])

            # Refresh UI
            self.refresh_entries_cards()
            dialog.accept()

        add_btn.clicked.connect(confirm_add)

        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(add_btn)
        layout.addLayout(button_layout)

        dialog.exec()


    def edit_entry(self, entry_idx, entry):
        if not self.selected_folder:
            return

        folder_data = self.vault_data.get("data", {}).get(self.selected_folder)
        if not folder_data:
            return

        schema = folder_data.get("schema", ["Title", "Username", "Password"])

        # Create dialog
        dialog_height = 350 + (len(schema) * 40)
        dialog = ModernDialog(self, "Edit Entry")
        dialog.setFixedSize(450, dialog_height)

        layout = dialog.setup_basic_layout(f"Edit entry in: {self.selected_folder}")
        layout.addSpacing(20)

        # Input fields with existing values
        input_fields = {}
        for i, field in enumerate(schema):
            field_container = QWidget()
            field_container.setFixedHeight(60)
            field_layout = QVBoxLayout(field_container)
            field_layout.setContentsMargins(0, 0, 0, 0)
            field_layout.setSpacing(5)

            label = QLabel(f"{field}:")
            label.setStyleSheet("color: #ffffff; font-size: 12px;")
            label.setFixedHeight(20)

            current_value = entry.get(field, "")

            if field.lower() == "password":
                input_field = ModernLineEdit()
                input_field.setEchoMode(QLineEdit.EchoMode.Password)
                input_field.setText(current_value)
            else:
                input_field = ModernLineEdit()
                input_field.setText(current_value)

            input_field.setFixedHeight(35)
            input_fields[field] = input_field

            field_layout.addWidget(label)
            field_layout.addWidget(input_field)

            layout.addWidget(field_container)

            if i < len(schema) - 1:
                layout.addSpacing(10)

        layout.addSpacing(20)

        # Error message
        error_label = QLabel("")
        error_label.setStyleSheet("color: #ff4757; font-size: 11px;")
        error_label.setFixedHeight(20)
        layout.addWidget(error_label)

        layout.addSpacing(15)
        layout.addStretch()

        # Buttons
        button_layout = QHBoxLayout()

        cancel_btn = ModernButton("Cancel", primary=False)
        cancel_btn.clicked.connect(dialog.reject)

        save_btn = ModernButton("Save Changes", primary=True)
        save_btn.setDefault(True)

        def confirm_edit():
            updated_entry = {}
            for field, input_field in input_fields.items():
                value = input_field.text().strip()
                if not value:
                    error_label.setText("All fields are required")
                    return
                updated_entry[field] = value

            # Update the entry
            folder_data["entries"][entry_idx] = updated_entry

            # Save to backend
            from core.vault_manager import save_vault
            save_vault(self.vault_data["data"], self.vault_key)

            from gui.analytics_manager import update_vault_stats
            update_vault_stats(self.vault_data["data"])

            # Refresh UI
            self.refresh_entries_cards()
            dialog.accept()

        save_btn.clicked.connect(confirm_edit)

        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(save_btn)
        layout.addLayout(button_layout)

        dialog.exec()

    def delete_entry(self, entry_idx):
        # Create confirmation dialog
        dialog = ModernDialog(self, "Delete Entry")
        dialog.setFixedSize(350, 220)

        layout = dialog.setup_basic_layout("Delete Entry")

        # Warning message
        warning_label = QLabel("Are you sure you want to delete this entry?")
        warning_label.setStyleSheet("font-size: 14px; color: #ffffff;")
        layout.addWidget(warning_label)

        danger_label = QLabel("This action cannot be undone!")
        danger_label.setStyleSheet("font-size: 12px; color: #ff4757; font-weight: bold;")
        layout.addWidget(danger_label)

        layout.addStretch()

        # Buttons
        button_layout = QHBoxLayout()

        cancel_btn = ModernButton("Cancel", primary=False)
        cancel_btn.clicked.connect(dialog.reject)

        delete_btn = ModernButton("Yes, Delete", primary=True)
        delete_btn.setStyleSheet("""
            ModernButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #ff4757, stop:1 #ff3742);
                color: white;
            }
            ModernButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #ff3742, stop:1 #ff2d38);
            }
        """)

        def confirm_delete():
            # Remove entry from vault data
            folder_data = self.vault_data["data"][self.selected_folder]
            folder_data["entries"].pop(entry_idx)

            # Save to backend
            from core.vault_manager import save_vault
            save_vault(self.vault_data["data"], self.vault_key)

            from gui.analytics_manager import update_vault_stats
            update_vault_stats(self.vault_data["data"])

            # Refresh UI
            self.refresh_entries_cards()
            dialog.accept()

        delete_btn.clicked.connect(confirm_delete)

        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(delete_btn)
        layout.addLayout(button_layout)

        dialog.exec()

    def edit_folder(self):
        if not self.selected_folder:
            return

        folder_data = self.vault_data.get("data", {}).get(self.selected_folder)
        if not folder_data:
            return

        schema = folder_data.get("schema", ["Title", "Username", "Password"])

        # Create dialog
        dialog = ModernDialog(self, "Edit Folder")
        dialog.setFixedSize(450, 380)

        layout = dialog.setup_basic_layout(f"Edit Folder: {self.selected_folder}")
        layout.addSpacing(20)

        # Folder name field
        name_container = QWidget()
        name_container.setFixedHeight(60)
        name_layout = QVBoxLayout(name_container)
        name_layout.setContentsMargins(0, 0, 0, 0)
        name_layout.setSpacing(5)

        name_label = QLabel("Folder Name:")
        name_label.setStyleSheet("color: #ffffff; font-size: 12px;")
        name_label.setFixedHeight(20)

        folder_name_input = ModernLineEdit()
        folder_name_input.setText(self.selected_folder)
        folder_name_input.setFixedHeight(35)

        name_layout.addWidget(name_label)
        name_layout.addWidget(folder_name_input)
        layout.addWidget(name_container)

        layout.addSpacing(15)

        # Fields input
        fields_container = QWidget()
        fields_container.setFixedHeight(60)
        fields_layout = QVBoxLayout(fields_container)
        fields_layout.setContentsMargins(0, 0, 0, 0)
        fields_layout.setSpacing(5)

        fields_label = QLabel("Fields:")
        fields_label.setStyleSheet("color: #ffffff; font-size: 12px;")
        fields_label.setFixedHeight(20)

        fields_input = ModernLineEdit()
        fields_input.setText(", ".join(schema))
        fields_input.setFixedHeight(35)

        fields_layout.addWidget(fields_label)
        fields_layout.addWidget(fields_input)
        layout.addWidget(fields_container)

        layout.addSpacing(15)

        # Info text
        info_label = QLabel("Note: A 'Title' field will be automatically added if not included")
        info_label.setStyleSheet("color: #888888; font-size: 10px; font-style: italic;")
        info_label.setFixedHeight(15)
        layout.addWidget(info_label)

        layout.addSpacing(10)

        # Error message
        error_label = QLabel("")
        error_label.setStyleSheet("color: #ff4757; font-size: 11px;")
        error_label.setFixedHeight(20)
        layout.addWidget(error_label)

        layout.addStretch()

        # Buttons
        button_layout = QHBoxLayout()

        cancel_btn = ModernButton("Cancel", primary=False)
        cancel_btn.clicked.connect(dialog.reject)

        save_btn = ModernButton("Save Changes", primary=True)
        save_btn.setDefault(True)

        def confirm_edit():
            new_folder_name = folder_name_input.text().strip()
            fields_text = fields_input.text().strip()

            if not new_folder_name:
                error_label.setText("Folder name is required")
                return

            if not fields_text:
                error_label.setText("At least one field is required")
                return

            # Check if new name conflicts
            if new_folder_name != self.selected_folder and new_folder_name in self.vault_data.get("data", {}):
                error_label.setText(f"Folder '{new_folder_name}' already exists")
                return

            # Process fields
            new_fields = [field.strip() for field in fields_text.split(',') if field.strip()]

            # Ensure Title field
            title_fields = ['title', 'name', 'label']
            has_title = any(field.lower() in title_fields for field in new_fields)
            if not has_title:
                new_fields = ["Title"] + new_fields

            # Get current folder data
            current_folder_data = self.vault_data["data"][self.selected_folder]

            # Update the schema
            current_folder_data["schema"] = new_fields

            # If name changed, rename folder
            if new_folder_name != self.selected_folder:
                self.vault_data["data"][new_folder_name] = current_folder_data
                del self.vault_data["data"][self.selected_folder]
                self.selected_folder = new_folder_name

            # Save to backend
            from core.vault_manager import save_vault
            save_vault(self.vault_data["data"], self.vault_key)

            # Update UI
            self.refresh_folders_enhanced()
            self.refresh_entries_cards()

            dialog.accept()

        save_btn.clicked.connect(confirm_edit)

        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(save_btn)
        layout.addLayout(button_layout)

        folder_name_input.setFocus()
        dialog.exec()

    def delete_folder(self):
        if not self.selected_folder:
            return

        # Create confirmation dialog
        dialog = ModernDialog(self, "Delete Folder")
        dialog.setFixedSize(400, 250)

        layout = dialog.setup_basic_layout("Delete Folder")

        # Warning message
        warning_label = QLabel(f"Are you sure you want to delete folder '{self.selected_folder}'?")
        warning_label.setStyleSheet("font-size: 14px; color: #ffffff;")
        layout.addWidget(warning_label)

        # Entry count info
        folder_data = self.vault_data.get("data", {}).get(self.selected_folder, {})
        entry_count = len(folder_data.get("entries", []))

        if entry_count > 0:
            count_label = QLabel(f"This folder contains {entry_count} entry(ies) that will also be deleted.")
            count_label.setStyleSheet("font-size: 12px; color: #ffaa00;")
            layout.addWidget(count_label)

        danger_label = QLabel("This action cannot be undone!")
        danger_label.setStyleSheet("font-size: 12px; color: #ff4757; font-weight: bold;")
        layout.addWidget(danger_label)

        layout.addStretch()

        # Buttons
        button_layout = QHBoxLayout()

        cancel_btn = ModernButton("Cancel", primary=False)
        cancel_btn.clicked.connect(dialog.reject)

        delete_btn = ModernButton("Yes, Delete Folder", primary=True)
        delete_btn.setStyleSheet("""
            ModernButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #ff4757, stop:1 #ff3742);
                color: white;
            }
            ModernButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #ff3742, stop:1 #ff2d38);
            }
        """)

        def confirm_delete():
            # Remove folder from vault data
            del self.vault_data["data"][self.selected_folder]

            # Save to backend
            from core.vault_manager import save_vault
            save_vault(self.vault_data["data"], self.vault_key)

            from gui.analytics_manager import update_vault_stats
            update_vault_stats(self.vault_data["data"])

            # Reset selection and refresh UI
            self.selected_folder = None
            self.refresh_folders_enhanced()
            self.refresh_entries_cards()

            dialog.accept()

        delete_btn.clicked.connect(confirm_delete)

        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(delete_btn)
        layout.addLayout(button_layout)

        dialog.exec()

    def connect_profile_button(self, profile_button):
        profile_button.clicked.connect(self.show_settings_dialog)

    def show_settings_dialog(self):
        print("Starting settings dialog...")
        try:
            from PyQt6.QtWidgets import QLabel, QWidget, QHBoxLayout, QVBoxLayout
            from PyQt6.QtCore import Qt

            dialog = ModernDialog(self, "Settings")
            dialog.setFixedSize(500, 450)
            layout = dialog.setup_basic_layout("Settings")
            layout.addSpacing(20)

            def create_toggle_widget(is_enabled, disabled=False):
                toggle_container = QWidget()
                toggle_container.setFixedSize(50, 25)

                if disabled:
                    bg_color = "#666666"
                    border_color = "#666666"
                else:
                    bg_color = "#4CAF50" if is_enabled else "#444444"
                    border_color = "#4CAF50" if is_enabled else "#666666"

                toggle_container.setStyleSheet(f"""
                    QWidget {{
                        background: {bg_color};
                        border: 2px solid {border_color};
                        border-radius: 12px;
                    }}
                """)

                toggle_circle = QLabel("●")
                toggle_circle.setParent(toggle_container)
                circle_x = 25 if is_enabled else 3
                toggle_circle.setGeometry(circle_x, 1, 22, 22)
                toggle_circle.setStyleSheet("""
                    QLabel {
                        color: white;
                        font-size: 16px;
                        font-weight: bold;
                        background: transparent;
                        border: none;
                    }
                """)
                toggle_circle.setAlignment(Qt.AlignmentFlag.AlignCenter)

                toggle_container.circle = toggle_circle
                toggle_container.is_enabled = is_enabled
                return toggle_container

            def update_toggle_widget(toggle_container, is_enabled):
                bg_color = "#4CAF50" if is_enabled else "#444444"
                border_color = "#4CAF50" if is_enabled else "#666666"

                toggle_container.setStyleSheet(f"""
                    QWidget {{
                        background: {bg_color};
                        border: 2px solid {border_color};
                        border-radius: 12px;
                    }}
                """)

                circle_x = 25 if is_enabled else 3
                toggle_container.circle.setGeometry(circle_x, 1, 22, 22)
                toggle_container.is_enabled = is_enabled

            def create_setting_row(text, toggle_widget):
                row = QWidget()
                row.setFixedHeight(40)
                row_layout = QHBoxLayout(row)
                row_layout.setContentsMargins(0, 0, 0, 0)

                label = QLabel(text)
                label.setStyleSheet("color: #ffffff; font-size: 12px;")

                row_layout.addWidget(label)
                row_layout.addStretch()
                row_layout.addWidget(toggle_widget)
                return row

            # === USERNAME SECTION ===
            username_label = QLabel("Account")
            username_label.setStyleSheet("color: #4CAF50; font-size: 14px; font-weight: bold;")

            username_input = ModernLineEdit()
            username_input.setText(self.vault_data.get('username', ''))
            username_input.setFixedHeight(40)
            username_input.setReadOnly(True)
            username_input.setStyleSheet("""
                ModernLineEdit {
                    background: rgba(255, 255, 255, 0.05);
                    border: 1px solid rgba(255, 255, 255, 0.1);
                    color: #888888;
                    font-size: 12px;
                }
            """)

            layout.addWidget(username_label)
            layout.addWidget(username_input)
            layout.addSpacing(25)

            # === ANALYTICS SECTION ===
            analytics_label = QLabel("Privacy")
            analytics_label.setStyleSheet("color: #4CAF50; font-size: 14px; font-weight: bold;")

            try:
                from gui.analytics_manager import should_collect_analytics, set_consent_choice
                current_analytics = should_collect_analytics()
                analytics_available = True
            except ImportError:
                current_analytics = False
                analytics_available = False

            analytics_toggle = create_toggle_widget(current_analytics, not analytics_available)

            def toggle_analytics():
                if not analytics_available:
                    return
                try:
                    new_state = not analytics_toggle.is_enabled
                    success = set_consent_choice(new_state)
                    if success:
                        update_toggle_widget(analytics_toggle, new_state)
                except Exception as e:
                    print(f"Analytics toggle error: {e}")

            analytics_toggle.mousePressEvent = lambda e: toggle_analytics()
            analytics_row = create_setting_row("Anonymous Analytics", analytics_toggle)

            layout.addWidget(analytics_label)
            layout.addWidget(analytics_row)
            layout.addSpacing(25)

            # === SYSTEM SECTION ===
            system_label = QLabel("System")
            system_label.setStyleSheet("color: #4CAF50; font-size: 14px; font-weight: bold;")

            try:
                from tray.startup_manager import StartupManager
                startup_manager = StartupManager()
                current_startup = startup_manager.is_startup_enabled()
                print(f"DEBUG: Initial startup state detected: {current_startup}")
            except ImportError:
                startup_manager = None
                current_startup = False

            startup_toggle = create_toggle_widget(current_startup, startup_manager is None)

            def toggle_startup():
                if not startup_manager:
                    return
                try:
                    new_state = not startup_toggle.is_enabled
                    result = startup_manager.enable_startup() if new_state else startup_manager.disable_startup()
                    if result:
                        update_toggle_widget(startup_toggle, new_state)
                except Exception as e:
                    print(f"Startup toggle error: {e}")

            if startup_manager:
                startup_toggle.mousePressEvent = lambda e: toggle_startup()

            startup_row = create_setting_row("Start with Windows", startup_toggle)

            layout.addWidget(system_label)
            layout.addWidget(startup_row)
            layout.addSpacing(25)

            # === THEME SECTION ===
            theme_label = QLabel("Appearance")
            theme_label.setStyleSheet("color: #4CAF50; font-size: 14px; font-weight: bold;")

            theme_toggle = create_toggle_widget(True, disabled=True)

            theme_row_widget = QWidget()
            theme_row_widget.setFixedHeight(40)  # Add this line
            theme_row_layout = QHBoxLayout(theme_row_widget)
            theme_row_layout.setContentsMargins(0, 0, 0, 0)

            theme_text = QLabel("Dark Theme")
            theme_text.setStyleSheet("color: #ffffff; font-size: 12px;")

            coming_soon = QLabel("Light theme coming soon")
            coming_soon.setStyleSheet("color: #888888; font-size: 10px; font-style: italic;")

            theme_row_layout.addWidget(theme_text)
            theme_row_layout.addStretch()
            theme_row_layout.addWidget(coming_soon)
            theme_row_layout.addWidget(theme_toggle)

            layout.addWidget(theme_label)
            layout.addWidget(theme_row_widget)

            layout.addSpacing(30)
            layout.addStretch()

            # === BUTTONS ===
            button_layout = QHBoxLayout()

            close_btn = ModernButton("Close", primary=True)
            close_btn.clicked.connect(dialog.reject)

            button_layout.addWidget(close_btn)
            layout.addLayout(button_layout)

            layout.addSpacing(10)

            dialog.exec()
            print("Settings dialog completed successfully!")


        except Exception as e:
            print(f"Settings dialog failed: {e}")
            import traceback
            traceback.print_exc()



    def show_analytics_consent_dialog(self):
        from gui.widgets.modern_widgets import ModernDialog, ModernButton
        from PyQt6.QtWidgets import QVBoxLayout, QLabel, QHBoxLayout

        dialog = ModernDialog(self, "Help Improve The Vault")
        dialog.setFixedSize(500, 350)

        layout = dialog.setup_basic_layout("Help Improve The Vault")
        layout.addSpacing(15)

        explanation = QLabel("""We'd like to collect anonymous usage data to help improve The Vault. This includes:

    - Basic usage statistics (number of folders, entries)
    - Feature usage (which features you use most)
    - Performance metrics (app startup time)
    - Version and OS information

    No personal data, passwords, or vault contents are ever collected.
    You can change this choice later in Settings.""")

        explanation.setStyleSheet("color: #ffffff; font-size: 12px; line-height: 1.4;")
        explanation.setWordWrap(True)
        layout.addWidget(explanation)

        layout.addSpacing(20)
        layout.addStretch()

        # Buttons
        button_layout = QHBoxLayout()

        decline_btn = ModernButton("No Thanks", primary=False)
        decline_btn.clicked.connect(lambda: self._handle_consent_choice(False, dialog))

        accept_btn = ModernButton("Help Improve", primary=True)
        accept_btn.clicked.connect(lambda: self._handle_consent_choice(True, dialog))

        button_layout.addWidget(decline_btn)
        button_layout.addWidget(accept_btn)
        layout.addLayout(button_layout)

        dialog.exec()

    def _handle_consent_choice(self, consent_given, dialog):
        from gui.analytics_manager import set_consent_choice

        # Store the choice
        set_consent_choice(consent_given)
        dialog.accept()

    def add_folder(self):
        """Show the new enhanced folder creation dialog"""
        dialog = FolderCreationDialog(self)
        dialog.exec()


class FolderCreationDialog(ModernDialog):
    def __init__(self, parent: 'VaultWindow'):
        super().__init__(parent, "Create New Folder")
        self.parent = parent
        self.setFixedSize(520, 700)  # Even taller dialog
        self.setup_ui()

    def setup_ui(self):
        layout = self.setup_basic_layout("Create New Folder")

        # Mode selector - use QPushButton like the template buttons
        self.mode_layout = QHBoxLayout()
        self.simple_btn = QPushButton("Simplified")
        self.advanced_btn = QPushButton("Advanced")

        # Make them wider and use template button styling
        self.simple_btn.setFixedHeight(35)
        self.simple_btn.setFixedWidth(120)  # Wider
        self.simple_btn.setStyleSheet(self.get_preset_button_style(True))  # Start selected

        self.advanced_btn.setFixedHeight(35)
        self.advanced_btn.setFixedWidth(120)  # Wider
        self.advanced_btn.setStyleSheet(self.get_preset_button_style(False))

        # Connect with lambda to force our methods to be called
        self.simple_btn.clicked.connect(lambda: self.switch_to_simple())
        self.advanced_btn.clicked.connect(lambda: self.switch_to_advanced())

        self.mode_layout.addWidget(self.simple_btn)
        self.mode_layout.addWidget(self.advanced_btn)
        layout.addLayout(self.mode_layout)

        layout.addSpacing(15)

        # Content area in scroll area (switches between modes)
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFixedHeight(450)  # Much larger scroll area
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
        """)

        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        scroll_area.setWidget(self.content_widget)
        layout.addWidget(scroll_area)

        # Error label
        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: #ff4757; font-size: 11px;")
        self.error_label.hide()
        layout.addWidget(self.error_label)

        layout.addStretch()

        # Buttons
        button_layout = QHBoxLayout()
        self.cancel_btn = ModernButton("Cancel", primary=False)
        self.create_btn = ModernButton("Create Folder", primary=True)

        self.cancel_btn.clicked.connect(self.reject)
        self.create_btn.clicked.connect(self.create_folder)

        button_layout.addWidget(self.cancel_btn)
        button_layout.addWidget(self.create_btn)
        layout.addLayout(button_layout)

        # Start in simple mode
        self.switch_to_simple()

    def switch_to_simple(self):
        """Switch to simple mode and update button styles"""
        print("SWITCH TO SIMPLE CLICKED!")
        # Update button styles like template buttons do
        self.simple_btn.setStyleSheet(self.get_preset_button_style(True))  # Selected
        self.advanced_btn.setStyleSheet(self.get_preset_button_style(False))  # Not selected
        self.show_simple_mode()

    def switch_to_advanced(self):
        """Switch to advanced mode and update button styles"""
        print("SWITCH TO ADVANCED CLICKED!")
        # Update button styles like template buttons do
        self.simple_btn.setStyleSheet(self.get_preset_button_style(False))  # Not selected
        self.advanced_btn.setStyleSheet(self.get_preset_button_style(True))  # Selected
        self.show_advanced_mode()

    def get_primary_button_style(self):
        """Get green primary button style"""
        return """
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #4CAF50, stop:1 #45a049);
                color: white;
                border: none;
                border-radius: 12px;
                padding: 12px 24px;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 1px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #45a049, stop:1 #3d8b40);
            }
        """

    def get_secondary_button_style(self):
        """Get gray secondary button style"""
        return """
            QPushButton {
                background: rgba(255, 255, 255, 0.1);
                color: #ffffff;
                border: 2px solid rgba(255, 255, 255, 0.25);
                border-radius: 12px;
                padding: 10px 22px;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 1px;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 0.15);
                border: 2px solid rgba(255, 255, 255, 0.35);
            }
        """

    def show_simple_mode(self):
        """Switch to simplified preset mode"""
        self.update_mode_buttons(simple_active=True)
        self.clear_content()

        # Folder name input
        name_label = QLabel("Folder Name:")
        name_label.setStyleSheet("color: #ffffff; font-size: 12px;")
        self.folder_name_input = ModernLineEdit("Enter folder name")

        self.content_layout.addWidget(name_label)
        self.content_layout.addWidget(self.folder_name_input)
        self.content_layout.addSpacing(15)

        # Preset selector
        preset_label = QLabel("Choose Template:")
        preset_label.setStyleSheet("color: #ffffff; font-size: 12px;")
        self.content_layout.addWidget(preset_label)

        # Preset buttons in horizontal row
        preset_layout = QHBoxLayout()
        preset_layout.setSpacing(6)
        presets = self.get_folder_presets()

        self.selected_preset = None
        self.preset_buttons = {}

        for name, schema in presets.items():
            preset_btn = QPushButton(name)
            preset_btn.setFixedHeight(35)
            preset_btn.setFixedWidth(80)  # Smaller buttons
            preset_btn.setStyleSheet(self.get_preset_button_style(False))
            preset_btn.clicked.connect(lambda checked, n=name, s=schema: self.select_preset(n, s))

            self.preset_buttons[name] = preset_btn
            preset_layout.addWidget(preset_btn)

        self.content_layout.addLayout(preset_layout)
        self.content_layout.addSpacing(15)

        # Field editor area (will be populated when preset is selected)
        self.field_editor_area = QWidget()
        self.field_editor_layout = QVBoxLayout(self.field_editor_area)
        self.field_editor_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.addWidget(self.field_editor_area)
        self.content_layout.addSpacing(10)

        # Selected preset info (kept for reference)
        self.preset_info = QLabel("Select a template to see its fields")
        self.preset_info.setStyleSheet("color: #888888; font-size: 10px; font-style: italic;")
        self.content_layout.addWidget(self.preset_info)
        self.preset_info.hide()  # Hide since we show fields inline now

    def show_advanced_mode(self):
        """Switch to advanced custom mode"""
        self.update_mode_buttons(simple_active=False)
        self.clear_content()

        # Also clear the field editor area when switching modes
        self.clear_field_editor_area()

        # Folder name
        name_label = QLabel("Folder Name:")
        name_label.setStyleSheet("color: #ffffff; font-size: 12px;")
        self.folder_name_input = ModernLineEdit("Enter folder name")

        self.content_layout.addWidget(name_label)
        self.content_layout.addWidget(self.folder_name_input)
        self.content_layout.addSpacing(15)

        # Custom fields
        fields_label = QLabel("Fields:")
        fields_label.setStyleSheet("color: #ffffff; font-size: 12px;")
        self.fields_input = ModernLineEdit("Username, Password, Email")

        self.content_layout.addWidget(fields_label)
        self.content_layout.addWidget(self.fields_input)
        self.content_layout.addSpacing(10)

        # Info text
        info_label = QLabel("Note: A 'Title' field will be automatically added if not included")
        info_label.setStyleSheet("color: #888888; font-size: 10px; font-style: italic;")
        self.content_layout.addWidget(info_label)

    def clear_field_editor_area(self):
        """Clear the field editor area when switching modes"""
        if hasattr(self, 'field_editor_area') and self.field_editor_area:
            # Clear the field editor layout
            while self.field_editor_layout.count():
                child = self.field_editor_layout.takeAt(0)
                if child.widget():
                    child.widget().setParent(None)

        # Reset field tracking
        if hasattr(self, 'field_button_widgets'):
            self.field_button_widgets = {}
        if hasattr(self, 'selected_preset'):
            self.selected_preset = None

    def get_folder_presets(self):
        """Define preset folder templates - 3 specific options"""
        return {
            "Valorant": ["Username", "Email", "Password"],
            "Epic Games": ["Name", "Email", "Password"],
            "Gmail": ["Email", "Password"]
        }

    def get_preset_button_style(self, selected):
        """Get styling for preset buttons"""
        if selected:
            return """
                QPushButton {
                    background: rgba(76, 175, 80, 0.2);
                    border: 2px solid #4CAF50;
                    border-radius: 8px;
                    color: #4CAF50;
                    font-weight: bold;
                    font-size: 11px;
                }
                QPushButton:hover {
                    background: rgba(76, 175, 80, 0.3);
                }
            """
        else:
            return """
                QPushButton {
                    background: rgba(255, 255, 255, 0.08);
                    border: 1px solid rgba(255, 255, 255, 0.15);
                    border-radius: 8px;
                    color: #ffffff;
                    font-weight: bold;
                    font-size: 11px;
                }
                QPushButton:hover {
                    background: rgba(255, 255, 255, 0.15);
                    border: 1px solid rgba(255, 255, 255, 0.25);
                }
            """

    def select_preset(self, name, schema):
        """Handle preset selection"""
        # Update button styles
        for btn_name, btn in self.preset_buttons.items():
            btn.setStyleSheet(self.get_preset_button_style(btn_name == name))

        self.selected_preset = {"name": name, "schema": schema.copy()}

        # Show field editor in the dedicated area
        self.show_field_editor_inline()

    def show_field_editor_inline(self):
        """Show field editing in the dedicated area below buttons"""
        # Clear existing content
        while self.field_editor_layout.count():
            child = self.field_editor_layout.takeAt(0)
            if child.widget():
                child.widget().setParent(None)

        # Reset field button tracking
        self.field_button_widgets = {}

        # Header
        header_label = QLabel(f"Fields for {self.selected_preset['name']}:")
        header_label.setStyleSheet("color: #4CAF50; font-size: 12px; font-weight: bold;")
        self.field_editor_layout.addWidget(header_label)

        self.field_editor_layout.addSpacing(8)

        # Field buttons in horizontal rows - ONLY called once during initial setup
        self.create_initial_field_buttons()

        self.field_editor_layout.addSpacing(10)

        # Add field button
        add_field_btn = QPushButton("+ Add Field")
        add_field_btn.setFixedHeight(30)
        add_field_btn.setFixedWidth(100)
        add_field_btn.setStyleSheet("""
            QPushButton {
                background: rgba(76, 175, 80, 0.1);
                border: 1px solid rgba(76, 175, 80, 0.3);
                border-radius: 6px;
                color: #4CAF50;
                font-size: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: rgba(76, 175, 80, 0.2);
            }
        """)
        add_field_btn.clicked.connect(self.add_field)
        self.field_editor_layout.addWidget(add_field_btn)

    def create_initial_field_buttons(self):
        """Create field buttons using a grid layout that wraps properly"""
        # Create a widget to hold the field buttons in a grid
        self.fields_container = QWidget()
        self.fields_layout = QGridLayout(self.fields_container)
        self.fields_layout.setSpacing(8)
        self.fields_layout.setContentsMargins(0, 0, 0, 0)

        # Store button references for individual removal
        self.field_button_widgets = {}

        # Add all initial field buttons in a grid (4 per row)
        fields_per_row = 4
        for i, field in enumerate(self.selected_preset["schema"]):
            row = i // fields_per_row
            col = i % fields_per_row
            self.create_single_field_button_in_grid(field, row, col)

        # Add the container to the main layout
        self.field_editor_layout.addWidget(self.fields_container)

    def create_single_field_button_in_grid(self, field_name, row, col):
        """Create field button and place it in the grid"""
        # Create field button
        field_btn = QPushButton(field_name)
        field_btn.setFixedHeight(30)
        field_btn.setFixedWidth(100)  # Wider buttons (was 80)

        # Create container for the button (this prevents layout issues)
        field_container = QWidget()
        field_container.setFixedWidth(108)  # Wider container to match (was 88)
        field_container_layout = QHBoxLayout(field_container)
        field_container_layout.setContentsMargins(4, 0, 4, 0)
        field_container_layout.addWidget(field_btn)

        # Different styling for Title vs other fields
        if field_name.lower() == "title":
            field_btn.setStyleSheet(self.get_field_button_style(deleteable=False))
            field_btn.setEnabled(False)
        else:
            field_btn.setStyleSheet(self.get_field_button_style(deleteable=True))
            field_btn.clicked.connect(
                lambda checked, f=field_name, container=field_container: self.remove_field_safely(f, container))

        # Store reference to container
        self.field_button_widgets[field_name] = field_container

        # Add to grid at specific position
        self.fields_layout.addWidget(field_container, row, col)

    def remove_field_safely(self, field_name, container):
        """Use the safe approach that worked before"""
        if field_name in self.selected_preset["schema"] and field_name.lower() != "title":
            # Remove from schema
            self.selected_preset["schema"].remove(field_name)

            # Hide container (this worked before)
            container.hide()

            # Remove from tracking
            if field_name in self.field_button_widgets:
                del self.field_button_widgets[field_name]

    def update_field_buttons(self):
        """Update field buttons display"""
        # Create field buttons in rows
        current_row_layout = None
        fields_per_row = 3

        for i, field in enumerate(self.selected_preset["schema"]):
            # Start new row every 3 fields
            if i % fields_per_row == 0:
                current_row_layout = QHBoxLayout()
                row_widget = QWidget()
                row_widget.setLayout(current_row_layout)
                self.field_editor_layout.addWidget(row_widget)

            # Create field button
            field_btn = QPushButton(field)
            field_btn.setFixedHeight(30)
            field_btn.setMinimumWidth(80)

            # Different styling for Title (can't delete) vs other fields
            if field.lower() == "title":
                field_btn.setStyleSheet(self.get_field_button_style(deleteable=False))
                field_btn.setEnabled(False)  # Can't click Title
            else:
                field_btn.setStyleSheet(self.get_field_button_style(deleteable=True))
                field_btn.clicked.connect(lambda checked, f=field: self.remove_field_by_name(f))

            current_row_layout.addWidget(field_btn)

        # Fill remaining space in last row
        if current_row_layout:
            current_row_layout.addStretch()

    def get_field_button_style(self, deleteable=True):
        """Get styling for field buttons"""
        if deleteable:
            return """
                QPushButton {
                    background: rgba(255, 255, 255, 0.1);
                    border: 1px solid rgba(255, 255, 255, 0.2);
                    border-radius: 6px;
                    color: #ffffff;
                    font-size: 10px;
                    font-weight: bold;
                    padding: 5px 10px;
                }
                QPushButton:hover {
                    background: rgba(255, 71, 87, 0.3);
                    border: 1px solid #ff4757;
                    color: #ff4757;
                }
                QPushButton:pressed {
                    background: rgba(255, 71, 87, 0.4);
                }
            """
        else:
            return """
                QPushButton {
                    background: rgba(76, 175, 80, 0.1);
                    border: 1px solid rgba(76, 175, 80, 0.3);
                    border-radius: 6px;
                    color: #4CAF50;
                    font-size: 10px;
                    font-weight: bold;
                    padding: 5px 10px;
                }
            """

    def remove_field_by_name(self, field_name):
        """Remove field by name and refresh display"""
        if field_name in self.selected_preset["schema"] and field_name.lower() != "title":
            self.selected_preset["schema"].remove(field_name)
            self.update_field_buttons()

    def show_field_editor(self):
        """Show field editing section after preset selection"""
        # Remove existing field editor if present
        if hasattr(self, 'field_editor_widget'):
            self.field_editor_widget.setParent(None)

        self.field_editor_widget = QWidget()
        editor_layout = QVBoxLayout(self.field_editor_widget)
        editor_layout.setSpacing(8)
        editor_layout.setContentsMargins(0, 10, 0, 0)

        # Header
        edit_label = QLabel("Customize Fields:")
        edit_label.setStyleSheet("color: #FFD700; font-size: 11px; font-weight: bold;")
        editor_layout.addWidget(edit_label)

        # Field list with add/remove buttons
        self.field_list_layout = QVBoxLayout()
        self.update_field_list()
        editor_layout.addLayout(self.field_list_layout)

        # Add field button
        add_field_btn = QPushButton("+ Add Field")
        add_field_btn.setFixedHeight(30)
        add_field_btn.setStyleSheet("""
            QPushButton {
                background: rgba(76, 175, 80, 0.1);
                border: 1px solid rgba(76, 175, 80, 0.3);
                border-radius: 6px;
                color: #4CAF50;
                font-size: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: rgba(76, 175, 80, 0.2);
            }
        """)
        add_field_btn.clicked.connect(self.add_field)
        editor_layout.addWidget(add_field_btn)

        # Insert after preset info
        preset_info_index = self.content_layout.indexOf(self.preset_info)
        self.content_layout.insertWidget(preset_info_index + 1, self.field_editor_widget)

    def update_field_list(self):
        """Update the field list display"""
        # Clear existing field widgets
        while self.field_list_layout.count():
            child = self.field_list_layout.takeAt(0)
            if child.widget():
                child.widget().setParent(None)

        # Add each field with remove button
        for i, field in enumerate(self.selected_preset["schema"]):
            field_widget = QWidget()
            field_layout = QHBoxLayout(field_widget)
            field_layout.setContentsMargins(0, 0, 0, 0)
            field_layout.setSpacing(8)

            # Field name
            field_label = QLabel(field)
            field_label.setStyleSheet("color: #ffffff; font-size: 10px;")
            field_layout.addWidget(field_label)

            field_layout.addStretch()

            # Remove button (don't allow removing Title)
            if field.lower() != "title":
                remove_btn = QPushButton("✕")
                remove_btn.setFixedSize(20, 20)
                remove_btn.setStyleSheet("""
                    QPushButton {
                        background: rgba(255, 71, 87, 0.2);
                        border: 1px solid rgba(255, 71, 87, 0.4);
                        border-radius: 10px;
                        color: #ff4757;
                        font-size: 10px;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background: rgba(255, 71, 87, 0.3);
                    }
                """)
                remove_btn.clicked.connect(lambda checked, idx=i: self.remove_field(idx))
                field_layout.addWidget(remove_btn)

            self.field_list_layout.addWidget(field_widget)

    def add_field(self):
        """Add a new field"""
        from gui.widgets.modern_widgets import ModernDialog, ModernButton, ModernLineEdit

        # Simple input dialog
        dialog = ModernDialog(self, "Add Field")
        dialog.setFixedSize(300, 150)

        layout = QVBoxLayout(dialog)
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)

        label = QLabel("Field Name:")
        label.setStyleSheet("color: #ffffff; font-size: 12px;")
        layout.addWidget(label)

        field_input = ModernLineEdit("Enter field name")
        layout.addWidget(field_input)

        button_layout = QHBoxLayout()
        cancel_btn = ModernButton("Cancel", primary=False)
        add_btn = ModernButton("Add", primary=True)

        cancel_btn.clicked.connect(dialog.reject)
        add_btn.clicked.connect(lambda: self.confirm_add_field(field_input.text(), dialog))

        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(add_btn)
        layout.addLayout(button_layout)

        dialog.exec()

    def confirm_add_field(self, field_name, dialog):
        """Confirm and add the field"""
        field_name = field_name.strip()
        if field_name and field_name not in self.selected_preset["schema"]:
            self.selected_preset["schema"].append(field_name)

            # Add just the new field button instead of rebuilding all
            self.add_single_field_button(field_name)
            dialog.accept()

    def add_single_field_button(self, field_name):
        """Add new field using grid layout"""
        # Find the next available position in the grid
        current_count = len(self.field_button_widgets)
        fields_per_row = 4
        row = current_count // fields_per_row
        col = current_count % fields_per_row

        self.create_single_field_button_in_grid(field_name, row, col)

    def remove_field(self, index):
        """Remove a field by index"""
        if 0 <= index < len(self.selected_preset["schema"]):
            field = self.selected_preset["schema"][index]
            if field.lower() != "title":  # Don't allow removing Title
                self.selected_preset["schema"].pop(index)
                self.update_field_list()
                self.update_preset_info_text()

    def update_preset_info_text(self):
        """Update the preset info text with current fields"""
        fields_text = ", ".join(self.selected_preset["schema"])
        self.preset_info.setText(f"Fields: {fields_text}")

    def update_mode_buttons(self, simple_active):
        """Update mode button styling"""
        if simple_active:
            self.simple_btn.setProperty("primary", True)
            self.advanced_btn.setProperty("primary", False)
        else:
            self.simple_btn.setProperty("primary", False)
            self.advanced_btn.setProperty("primary", True)

    def clear_content(self):
        """Clear the content area safely"""
        # Hide all widgets first
        for i in range(self.content_layout.count()):
            item = self.content_layout.itemAt(i)
            if item and item.widget():
                item.widget().hide()

        # Remove from layout without deleting immediately
        while self.content_layout.count():
            child = self.content_layout.takeAt(0)
            if child.widget():
                child.widget().setParent(None)
            elif child.layout():
                # Clear nested layouts (like preset button layout)
                while child.layout().count():
                    nested_child = child.layout().takeAt(0)
                    if nested_child.widget():
                        nested_child.widget().setParent(None)

        # Reset state
        self.selected_preset = None
        self.preset_buttons = {}

        # Also clear field editor area
        self.clear_field_editor_area()

    def create_folder(self):
        """Create the folder based on current mode"""
        folder_name = self.folder_name_input.text().strip()
        self.error_label.hide()

        if not folder_name:
            self.show_error("Folder name is required")
            return

        # Check if folder exists
        if folder_name in self.parent.vault_data.get("data", {}):
            self.show_error(f"Folder '{folder_name}' already exists")
            return

        # Get schema based on mode
        if hasattr(self, 'selected_preset') and self.selected_preset:
            # Simple mode with preset
            schema = self.selected_preset["schema"].copy()
        elif hasattr(self, 'fields_input'):
            # Advanced mode with custom fields
            fields_text = self.fields_input.text().strip()
            if not fields_text:
                self.show_error("At least one field is required")
                return

            schema = [field.strip() for field in fields_text.split(',') if field.strip()]
        else:
            self.show_error("Please select a template or switch to advanced mode")
            return

        # Ensure Title field exists
        title_fields = ['title', 'name', 'label']
        has_title = any(field.lower() in title_fields for field in schema)
        if not has_title:
            schema = ["Title"] + schema

        # Create folder using existing backend
        from core.vault_manager import add_folder
        add_folder(self.parent.vault_key, folder_name, schema)

        # Update analytics and UI
        from gui.analytics_manager import update_vault_stats
        update_vault_stats(self.parent.vault_data["data"])

        # Reload vault data
        from core.vault_manager import load_vault
        updated_vault_data = load_vault(self.parent.vault_key)
        self.parent.vault_data["data"] = updated_vault_data
        self.parent.refresh_folders_enhanced()

        self.accept()

    def show_error(self, message):
        """Show error message"""
        self.error_label.setText(message)
        self.error_label.show()