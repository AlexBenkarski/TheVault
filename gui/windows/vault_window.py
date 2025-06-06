from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea,
                             QFrame, QPushButton, QGroupBox, QGridLayout, QDialog,
                             QLineEdit, QTextEdit, QMessageBox, QFileDialog)
from PyQt6.QtCore import Qt, pyqtSignal, QDateTime
from PyQt6.QtGui import QFont
from gui.widgets.modern_widgets import (ModernButton, ModernSmallButton, ModernEntryHeader,
                                        ModernEntryFrame, ModernDialog, ModernFormField, ModernLineEdit)


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

        # Main content area with fixed layout
        content_layout = QHBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        # Left panel - fixed width
        left_panel = self.create_left_panel()
        left_panel.setFixedWidth(375)

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
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(20, 20, 20, 20)
        left_layout.setSpacing(20)

        # Folders section
        folders_section = self.create_folders_section()
        left_layout.addWidget(folders_section)

        left_layout.addStretch()

        return left_widget

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
        scroll_area.setFixedHeight(430)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
            QScrollBar:vertical {
                background: rgba(255, 255, 255, 0.1);
                width: 12px;
                border-radius: 6px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: rgba(255, 255, 255, 0.3);
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: rgba(255, 255, 255, 0.5);
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
                height: 0px;
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
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(20, 20, 20, 20)
        right_layout.setSpacing(20)

        # Entries section
        entries_section = self.create_entries_section()
        right_layout.addWidget(entries_section)

        return right_widget

    def create_entries_section(self):
        self.entries_section = QGroupBox("📄 ENTRIES")
        self.entries_section.setStyleSheet("""
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

        layout = QVBoxLayout(self.entries_section)

        # Entries scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
        """)

        entries_widget = QWidget()
        self.entries_layout = QVBoxLayout(entries_widget)
        self.entries_layout.setSpacing(10)
        self.entries_layout.setContentsMargins(15, 15, 15, 15)

        scroll_area.setWidget(entries_widget)
        layout.addWidget(scroll_area)

        return self.entries_section

    def create_status_bar(self, parent_layout):
        status_bar = QFrame()
        status_bar.setFixedHeight(30)
        status_bar.setStyleSheet("""
            QFrame {
                background: transparent;
                border: none;
            }
        """)

        status_layout = QHBoxLayout(status_bar)
        status_layout.setContentsMargins(20, 5, 20, 5)

        status_layout.addStretch()

        version_label = QLabel("v1.0.1")
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

        # Refresh the UI
        self.refresh_folders()
        self.refresh_entries()

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
            self.folders_layout.parentWidget().setMinimumHeight(4 * 110 + 20)

    def refresh_entries(self):
        # Clear existing entries
        while self.entries_layout.count():
            child = self.entries_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        if not self.selected_folder:
            no_folder_label = QLabel("No folder selected.")
            no_folder_label.setStyleSheet("color: #888888; font-size: 14px;")
            no_folder_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.entries_layout.addWidget(no_folder_label)
            return

        # Get folder data
        folder_data = self.vault_data.get("data", {}).get(self.selected_folder)
        if not folder_data:
            error_label = QLabel(f"Folder '{self.selected_folder}' not found.")
            error_label.setStyleSheet("color: #ff4757; font-size: 14px;")
            error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.entries_layout.addWidget(error_label)
            return

        # Update entries section title
        self.entries_section.setTitle(f"📄 ENTRIES IN: {self.selected_folder}")

        # Add folder action buttons
        folder_actions_layout = QHBoxLayout()
        folder_actions_layout.addStretch()

        edit_folder_btn = ModernSmallButton("✏️ Edit Folder")
        edit_folder_btn.setFixedSize(100, 30)
        edit_folder_btn.clicked.connect(self.edit_folder)

        delete_folder_btn = ModernSmallButton("🗑️ Delete Folder", delete_style=True)
        delete_folder_btn.setFixedSize(110, 30)
        delete_folder_btn.clicked.connect(self.delete_folder)

        folder_actions_layout.addWidget(edit_folder_btn)
        folder_actions_layout.addWidget(delete_folder_btn)

        folder_actions_widget = QWidget()
        folder_actions_widget.setLayout(folder_actions_layout)
        self.entries_layout.addWidget(folder_actions_widget)

        # Get schema and entries
        schema = folder_data.get("schema", ["Title", "Username", "Password"])
        entries = folder_data.get("entries", [])

        if not entries:
            no_entries_label = QLabel("No entries in this folder.")
            no_entries_label.setStyleSheet("color: #888888; font-size: 14px;")
            no_entries_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.entries_layout.addWidget(no_entries_label)
        else:
            # Add entries
            for entry_idx, entry in enumerate(entries):
                entry_widget = self.create_entry_widget(entry_idx, entry, schema)
                self.entries_layout.addWidget(entry_widget)

        # Add New Entry button
        add_entry_btn = ModernButton("+ Add New Entry", primary=True)
        add_entry_btn.setFixedWidth(200)
        add_entry_btn.clicked.connect(self.add_entry_to_folder)

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(add_entry_btn)
        button_layout.addStretch()

        button_widget = QWidget()
        button_widget.setLayout(button_layout)
        self.entries_layout.addWidget(button_widget)

        self.entries_layout.addStretch()

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
        # Remove selection from previous folder
        if self.selected_folder and self.selected_folder in self.folder_buttons:
            self.folder_buttons[self.selected_folder].setStyleSheet(self.get_folder_button_style(False))

        # Set new selection
        self.selected_folder = folder_name

        # Add selection styling
        if folder_name in self.folder_buttons:
            self.folder_buttons[folder_name].setStyleSheet(self.get_folder_button_style(True))

        # Refresh entries
        self.refresh_entries()

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
                                label.setText(value)
                                label.setStyleSheet("color: #ffffff; font-family: monospace;")
                                btn.setText("Hide")
                            else:
                                label.setText("••••••••")
                                label.setStyleSheet("color: #888888; font-family: monospace;")
                                btn.setText("Show")
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
                field_layout.addWidget(copy_btn)
                if show_btn:
                    field_layout.addWidget(show_btn)

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

    def copy_to_clipboard(self, text):
        from PyQt6.QtWidgets import QApplication
        clipboard = QApplication.clipboard()
        clipboard.setText(text)

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

            # Refresh UI
            self.refresh_entries()
            dialog.accept()

        add_btn.clicked.connect(confirm_add)

        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(add_btn)
        layout.addLayout(button_layout)

        dialog.exec()

    def add_folder(self):
        dialog = ModernDialog(self, "Create New Folder")
        dialog.setFixedSize(450, 380)

        layout = dialog.setup_basic_layout("Create New Folder")
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

        folder_name_input = ModernLineEdit("Enter folder name")
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

        fields_input = ModernLineEdit("Username, Password, Email")
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
        create_btn = ModernButton("Create Folder", primary=True)
        create_btn.setDefault(True)

        def confirm_create():
            folder_name = folder_name_input.text().strip()
            fields_text = fields_input.text().strip()

            if not folder_name:
                error_label.setText("Folder name is required")
                return

            if not fields_text:
                error_label.setText("At least one field is required")
                return

            # Check if folder exists
            if folder_name in self.vault_data.get("data", {}):
                error_label.setText(f"Folder '{folder_name}' already exists")
                return

            # Process fields
            folder_fields = [field.strip() for field in fields_text.split(',') if field.strip()]

            # Ensure Title field
            title_fields = ['title', 'name', 'label']
            has_title = any(field.lower() in title_fields for field in folder_fields)
            if not has_title:
                folder_fields = ["Title"] + folder_fields

            # Use backend method
            from core.vault_manager import add_folder
            add_folder(self.vault_key, folder_name, folder_fields)

            # Reload vault data
            from core.vault_manager import load_vault
            updated_vault_data = load_vault(self.vault_key)

            # Update UI
            self.vault_data["data"] = updated_vault_data
            self.refresh_folders()

            dialog.accept()

        cancel_btn.clicked.connect(dialog.reject)
        create_btn.clicked.connect(confirm_create)

        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(create_btn)
        layout.addLayout(button_layout)

        folder_name_input.setFocus()
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

            # Refresh UI
            self.refresh_entries()
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

            # Refresh UI
            self.refresh_entries()
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
            self.refresh_folders()
            self.refresh_entries()

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

            # Reset selection and refresh UI
            self.selected_folder = None
            self.refresh_folders()
            self.refresh_entries()

            dialog.accept()

        delete_btn.clicked.connect(confirm_delete)

        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(delete_btn)
        layout.addLayout(button_layout)

        dialog.exec()

    def connect_profile_button(self, profile_button):
        profile_button.clicked.connect(self.show_settings_dialog)

    def show_settings_dialog(self):
        dialog = ModernDialog(self, "Settings")
        dialog.setFixedSize(450, 320)

        layout = dialog.setup_basic_layout("Settings")
        layout.addSpacing(20)

        # Username section
        username_container = QWidget()
        username_container.setFixedHeight(60)
        username_layout = QVBoxLayout(username_container)
        username_layout.setContentsMargins(0, 0, 0, 0)
        username_layout.setSpacing(5)

        username_label = QLabel("Username:")
        username_label.setStyleSheet("color: #ffffff; font-size: 12px;")
        username_label.setFixedHeight(20)

        username_input = ModernLineEdit()
        username_input.setText(self.vault_data.get('username', ''))
        username_input.setFixedHeight(35)
        username_input.setReadOnly(True)
        username_input.setStyleSheet("""
            ModernLineEdit {
                background: rgba(255, 255, 255, 0.05);
                border: 1px solid rgba(255, 255, 255, 0.1);
                color: #888888;
            }
        """)

        username_layout.addWidget(username_label)
        username_layout.addWidget(username_input)
        layout.addWidget(username_container)

        layout.addSpacing(20)

        # Theme section
        theme_container = QWidget()
        theme_container.setFixedHeight(60)
        theme_layout = QVBoxLayout(theme_container)
        theme_layout.setContentsMargins(0, 0, 0, 0)
        theme_layout.setSpacing(5)

        theme_label = QLabel("Current Theme:")
        theme_label.setStyleSheet("color: #ffffff; font-size: 12px;")
        theme_label.setFixedHeight(20)

        # Theme toggle row
        theme_row = QWidget()
        theme_row_layout = QHBoxLayout(theme_row)
        theme_row_layout.setContentsMargins(0, 0, 0, 0)
        theme_row_layout.setSpacing(15)

        dark_label = QLabel("Dark")
        dark_label.setStyleSheet("color: #4CAF50; font-size: 11px; font-weight: bold;")

        # Create toggle container
        toggle_container = QWidget()
        toggle_container.setFixedSize(60, 30)
        toggle_container.setStyleSheet("""
            QWidget {
                background: #4CAF50;
                border: 2px solid #45a049;
                border-radius: 15px;
            }
        """)

        # Create toggle circle
        toggle_circle = QLabel("●")
        toggle_circle.setParent(toggle_container)
        toggle_circle.setGeometry(5, 2, 26, 26)
        toggle_circle.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 20px;
                font-weight: bold;
                background: transparent;
                border: none;
            }
        """)
        toggle_circle.setAlignment(Qt.AlignmentFlag.AlignCenter)

        light_label = QLabel("Light")
        light_label.setStyleSheet("color: #888888; font-size: 11px;")

        # Coming soon label
        coming_soon = QLabel("(Coming Soon)")
        coming_soon.setStyleSheet("color: #888888; font-size: 9px; font-style: italic;")

        theme_row_layout.addWidget(dark_label)
        theme_row_layout.addWidget(toggle_container)
        theme_row_layout.addWidget(light_label)
        theme_row_layout.addWidget(coming_soon)
        theme_row_layout.addStretch()

        theme_layout.addWidget(theme_label)
        theme_layout.addWidget(theme_row)
        layout.addWidget(theme_container)

        layout.addSpacing(30)
        layout.addStretch()

        # Buttons
        button_layout = QHBoxLayout()

        export_btn = ModernButton("Export Vault", primary=False)
        export_btn.clicked.connect(self.export_vault)

        close_btn = ModernButton("Close", primary=True)
        close_btn.clicked.connect(dialog.reject)

        button_layout.addWidget(export_btn)
        button_layout.addWidget(close_btn)
        layout.addLayout(button_layout)

        dialog.exec()

    def export_vault(self):
        import json

        # Ask user where to save the export
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Vault",
            f"vault_export_{self.vault_data.get('username', 'user')}.json",
            "JSON files (*.json);;All files (*.*)"
        )

        if file_path:
            export_data = {
                "username": self.vault_data.get("username"),
                "data": self.vault_data.get("data", {}),
                "exported_at": QDateTime.currentDateTime().toString("yyyy-MM-dd hh:mm:ss")
            }

            with open(file_path, 'w') as f:
                json.dump(export_data, f, indent=2)

            # Show success message
            QMessageBox.information(self, "Export Complete",
                                    f"Vault exported successfully to:\n{file_path}")