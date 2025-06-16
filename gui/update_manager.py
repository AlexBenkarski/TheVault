import requests
import json
import subprocess
import sys
import os
import webbrowser
from packaging import version
from config import is_dev_environment
import dev_tools.dev_manager

# Version management
VERSION_FILE = "version.txt"
GITHUB_API_URL = "https://api.github.com/repos/AlexBenkarski/TheVault/releases/latest"
CACHED_SECRETS = None

def get_window_title():
    current_version = get_current_version()

    if is_dev_environment():
        return f"Vault DEVELOPMENT v{current_version}"
    else:
        return f"The Vault v{current_version}"

def get_discord_webhook():
    if CACHED_SECRETS is None:
        return None
    try:
        return CACHED_SECRETS["discord"]["webhook_url"]
    except KeyError:
        return None


def get_firebase_credentials():
    try:
        if os.path.exists("vaultfirebase.json"):
            return "vaultfirebase.json"
        return None
    except Exception as e:
        print(f"Error loading Firebase credentials: {e}")
        return None

def load_secrets():
    global CACHED_SECRETS
    loaded_services = []

    secrets_path = get_secrets_path()
    print(f"Looking for secrets at: {secrets_path}")

    if os.path.exists(secrets_path):
        try:
            if secrets_path.endswith('.enc'):
                # Load encrypted secrets (production)
                with open(secrets_path, 'r', encoding='utf-8') as f:
                    encrypted_data = f.read().strip()

                # Decrypt using embedded decryption function
                from secrets_encryption import decrypt_secrets_data
                secrets = decrypt_secrets_data(encrypted_data)

                if secrets is None:
                    print("Failed to decrypt secrets")
                    CACHED_SECRETS = {}
                    return []

                print("Encrypted secrets loaded successfully")

            else:
                # Load plaintext secrets (development)
                with open(secrets_path, 'r', encoding='utf-8') as f:
                    secrets = json.load(f)
                print("Using plaintext secrets (development mode)")

            CACHED_SECRETS = secrets

            if "discord" in secrets:
                loaded_services.append("discord")
            if "google_analytics" in secrets:
                loaded_services.append("google_analytics")

            print(f"Loaded services: {loaded_services}")

        except Exception as e:
            print(f"Error loading secrets: {e}")
            CACHED_SECRETS = {}

    else:
        print("Secrets file not found - analytics disabled")
        CACHED_SECRETS = {}

    return loaded_services


def get_secrets_path():
    if getattr(sys, 'frozen', False):
        app_dir = sys._MEIPASS
        encrypted_path = os.path.join(app_dir, 'secrets.enc')
        if os.path.exists(encrypted_path):
            return encrypted_path
        # Fallback to plaintext (development)
        return os.path.join(app_dir, 'secrets.json')
    else:
        # Running as script - development mode, use plaintext
        app_dir = get_app_directory()
        return os.path.join(app_dir, 'secrets.json')


def get_app_directory():
    if getattr(sys, 'frozen', False):
        # Running as exe
        return os.path.dirname(sys.executable)
    else:
        # Running as script (development)
        return os.path.dirname(os.path.abspath(__file__))


def get_current_version():
    if dev_tools.dev_manager.DEV_MODE_ACTIVE:
        project_root = os.path.dirname(get_app_directory())
        version_path = os.path.join(project_root, VERSION_FILE)
        print(f"DEBUG: Dev mode - looking at: {version_path}")
        print(f"DEBUG: File exists: {os.path.exists(version_path)}")
        if os.path.exists(version_path):
            with open(version_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                print(f"DEBUG: File content: '{content}'")
                return content
    else:
        app_dir = get_app_directory()
        version_path = os.path.join(app_dir, VERSION_FILE)
        if os.path.exists(version_path):
            with open(version_path, 'r', encoding='utf-8') as f:
                return f.read().strip()
    return "Unknown"



def check_for_updates():
   try:
       print("Checking for updates...")

       headers = {
           'User-Agent': 'TheVault-UpdateChecker/1.0',
           'Accept': 'application/vnd.github.v3+json'
       }

       response = requests.get(GITHUB_API_URL, headers=headers, timeout=10)

       if response.status_code == 200:
           release_data = response.json()
           latest_version = release_data['tag_name'].lstrip('v')
           current_version = get_current_version()

           # Add fallback for Unknown version
           if current_version == "Unknown":
               current_version = "2.0.4-beta"
               print("Using fallback version for update check")

           print(f"Current version: {current_version}")
           print(f"Latest version: {latest_version}")

           if version.parse(latest_version) > version.parse(current_version):
               # Find the .exe asset in the release
               exe_asset = None
               for asset in release_data['assets']:

                   if asset['name'] == 'Vault.exe' or (
                           asset['name'].endswith('.exe') and 'Setup' not in asset['name']):
                       exe_asset = asset
                       break

               if exe_asset:
                   print(f"Update available: {exe_asset['name']}")
                   return {
                       'available': True,
                       'version': latest_version,
                       'download_url': exe_asset['browser_download_url'],
                       'patch_notes': release_data['body'] or "No patch notes available.",
                       'release_name': release_data['name'],
                       'asset_name': exe_asset['name']
                   }
               else:
                   print("No suitable .exe file found in latest release")
           else:
               print("No update needed - you have the latest version")
       else:
           print(f"Failed to check for updates: HTTP {response.status_code}")

   except requests.exceptions.RequestException as e:
       print(f"Network error checking for updates: {e}")
   except Exception as e:
       print(f"Update check failed: {e}")

   return {'available': False}


def show_update_popup(parent, update_info):
    """Show update available dialog using PyQt6"""
    try:
        from gui.widgets.modern_widgets import ModernDialog, ModernButton
        from PyQt6.QtWidgets import QVBoxLayout, QLabel, QHBoxLayout, QScrollArea, QWidget
        from PyQt6.QtCore import Qt

        # Create update dialog
        dialog = ModernDialog(parent, "Update Available")
        dialog.setFixedSize(600, 510)

        # Override dialog styling
        dialog.setStyleSheet("""
            QDialog {
                background: #2d2d30;
                border: 2px solid #4CAF50;
                border-radius: 12px;
            }
            QLabel {
                background: transparent;
            }
            QScrollArea {
                background: transparent;
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 8px;
            }
        """)

        # Create layout
        layout = QVBoxLayout(dialog)
        layout.setSpacing(15)
        layout.setContentsMargins(25, 25, 25, 25)

        # Header
        header_label = QLabel(f"Version {update_info['version']} is available!")
        header_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #4CAF50; background: transparent;")
        layout.addWidget(header_label)

        layout.addSpacing(10)

        # Version info
        current_label = QLabel(f"Current version: {get_current_version()}")
        current_label.setStyleSheet("color: #ffffff; font-size: 12px; background: transparent;")
        layout.addWidget(current_label)

        latest_label = QLabel(f"Latest version: {update_info['version']}")
        latest_label.setStyleSheet("color: #ffffff; font-size: 12px; background: transparent;")
        layout.addWidget(latest_label)

        layout.addSpacing(15)

        # What's New section
        whats_new_label = QLabel("What's New:")
        whats_new_label.setStyleSheet("color: #FFD700; font-size: 14px; font-weight: bold; background: transparent;")
        layout.addWidget(whats_new_label)

        # Scrollable patch notes
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFixedHeight(250)

        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setSpacing(5)
        scroll_layout.setContentsMargins(15, 15, 15, 15)

        patch_lines = update_info['patch_notes'].split('\n')
        for line in patch_lines:
            line = line.strip()
            if line:
                if line.startswith('# '):
                    # Main header
                    note_label = QLabel(line[2:])
                    note_label.setStyleSheet(
                        "color: #FFD700; font-size: 14px; font-weight: bold; background: transparent;")
                    note_label.setWordWrap(True)
                elif line.startswith('## '):
                    # Sub header
                    note_label = QLabel(line[3:])
                    note_label.setStyleSheet(
                        "color: #FFA500; font-size: 13px; font-weight: bold; background: transparent;")
                    note_label.setWordWrap(True)
                elif line.startswith('- '):
                    # Bullet point
                    note_label = QLabel(f"  • {line[2:]}")
                    note_label.setStyleSheet("color: #ffffff; font-size: 12px; background: transparent;")
                    note_label.setWordWrap(True)
                else:
                    # Regular text
                    note_label = QLabel(line)
                    note_label.setStyleSheet("color: #ffffff; font-size: 12px; background: transparent;")
                    note_label.setWordWrap(True)

                scroll_layout.addWidget(note_label)

        scroll_area.setWidget(scroll_content)
        layout.addWidget(scroll_area)

        layout.addSpacing(20)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(20)

        update_btn = ModernButton("Update Now", primary=False)
        update_btn.setMinimumWidth(150)
        update_btn.setStyleSheet("""
            ModernButton {
                background: rgba(255, 255, 255, 0.1);
                color: #ffffff;
                border: 2px solid #4CAF50;
                border-radius: 12px;
                padding: 12px 24px;
                font-weight: 600;
            }
            ModernButton:hover {
                background: rgba(255, 255, 255, 0.15);
                border: 2px solid #45a049;
            }
            ModernButton:pressed {
                background: rgba(255, 255, 255, 0.2);
            }
        """)
        update_btn.clicked.connect(lambda: start_update_process(parent, update_info, dialog))

        remind_btn = ModernButton("Remind Me Later", primary=False)
        remind_btn.setMinimumWidth(150)
        remind_btn.clicked.connect(dialog.reject)

        button_layout.addStretch()
        button_layout.addWidget(update_btn)
        button_layout.addWidget(remind_btn)
        button_layout.addStretch()
        layout.addLayout(button_layout)

        dialog.exec()

    except Exception as e:
        print(f"Error showing update popup: {e}")


def start_update_process(parent, update_info, update_dialog):
    """Start the update process"""
    try:
        # Close update dialog
        update_dialog.accept()

        # Show updating dialog
        show_updating_popup(parent, update_info)

        # Find updater.exe
        app_dir = get_app_directory()
        updater_path = os.path.join(app_dir, "updater.exe")

        if os.path.exists(updater_path):
            print(f"Starting updater: {updater_path}")
            print(f"Download URL: {update_info['download_url']}")

            # Launch updater with the .exe download URL
            try:
                process = subprocess.Popen([
                    updater_path,
                    update_info['download_url'],
                    update_info['version'],
                    update_info['patch_notes']
                ], cwd=app_dir)

                print(f"Updater started with PID: {process.pid}")

                from PyQt6.QtWidgets import QApplication
                QApplication.instance().quit()

            except Exception as e:
                raise Exception(f"Failed to start updater process: {str(e)}")
        else:
            print(f"Updater not found at: {updater_path}")
            webbrowser.open(update_info['download_url'])
            show_error_popup(parent,
                             "Updater not found.\n\nThe download will open in your browser.\nPlease download and replace TheVault.exe manually.")

    except Exception as e:
        print(f"Update process failed: {str(e)}")
        show_error_popup(parent, f"Update failed: {str(e)}")


def show_updating_popup(parent, update_info):
    """Show updating progress dialog"""
    try:
        from gui.widgets.modern_widgets import ModernDialog
        from PyQt6.QtWidgets import QVBoxLayout, QLabel
        from PyQt6.QtCore import Qt

        # Create updating dialog
        dialog = ModernDialog(parent, "Updating...")
        dialog.setFixedSize(400, 200)

        # Override dialog styling
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

        # Create layout
        layout = QVBoxLayout(dialog)
        layout.setSpacing(15)
        layout.setContentsMargins(25, 25, 25, 25)

        # Status messages
        status_label = QLabel("Downloading update...")
        status_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #4CAF50; background: transparent;")
        status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(status_label)

        version_label = QLabel(f"Version: {update_info['version']}")
        version_label.setStyleSheet("color: #ffffff; font-size: 12px; background: transparent;")
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(version_label)

        file_label = QLabel(f"File: {update_info.get('asset_name', 'TheVault.exe')}")
        file_label.setStyleSheet("color: #ffffff; font-size: 12px; background: transparent;")
        file_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(file_label)

        restart_label = QLabel("The Vault will restart automatically.")
        restart_label.setStyleSheet("color: #FFD700; font-size: 12px; background: transparent;")
        restart_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(restart_label)

        wait_label = QLabel("Please wait...")
        wait_label.setStyleSheet("color: #888888; font-size: 12px; background: transparent;")
        wait_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(wait_label)

        dialog.show()

    except Exception as e:
        print(f"Error showing updating popup: {e}")


def show_error_popup(parent, message):
    """Show error dialog"""
    try:
        from gui.widgets.modern_widgets import ModernDialog, ModernButton
        from PyQt6.QtWidgets import QVBoxLayout, QLabel, QHBoxLayout

        # Create error dialog
        dialog = ModernDialog(parent, "Update Error")
        dialog.setFixedSize(450, 250)

        # Override dialog styling
        dialog.setStyleSheet("""
            QDialog {
                background: #2d2d30;
                border: 2px solid #ff4757;
                border-radius: 12px;
            }
            QLabel {
                background: transparent;
            }
        """)

        # Create layout
        layout = QVBoxLayout(dialog)
        layout.setSpacing(15)
        layout.setContentsMargins(25, 25, 25, 25)

        # Error message
        lines = message.split('\n')
        for line in lines:
            if line.strip():
                error_label = QLabel(line.strip())
                error_label.setStyleSheet("color: #ff4757; font-size: 12px; background: transparent;")
                error_label.setWordWrap(True)
                layout.addWidget(error_label)

        layout.addSpacing(20)

        # OK button
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        ok_btn = ModernButton("OK", primary=True)
        ok_btn.setMinimumWidth(80)
        ok_btn.clicked.connect(dialog.accept)

        button_layout.addWidget(ok_btn)
        button_layout.addStretch()
        layout.addLayout(button_layout)

        # Show dialog
        dialog.exec()

    except Exception as e:
        print(f"Error showing error popup: {e}")


def show_post_update_popup(parent, patch_notes):
    """Show post-update 'what's new' dialog"""
    try:
        from gui.widgets.modern_widgets import ModernDialog, ModernButton
        from PyQt6.QtWidgets import QVBoxLayout, QLabel, QHBoxLayout, QScrollArea, QWidget

        # Create post-update dialog
        dialog = ModernDialog(parent, "Update Complete!")
        dialog.setFixedSize(600, 500)

        # Override dialog styling
        dialog.setStyleSheet("""
            QDialog {
                background: #2d2d30;
                border: 2px solid #4CAF50;
                border-radius: 12px;
            }
            QLabel {
                background: transparent;
            }
            QScrollArea {
                background: transparent;
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 8px;
            }
        """)

        # Create layout
        layout = QVBoxLayout(dialog)
        layout.setSpacing(15)
        layout.setContentsMargins(25, 25, 25, 25)

        # Success message
        success_label = QLabel("The Vault has been updated successfully!")
        success_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #4CAF50; background: transparent;")
        layout.addWidget(success_label)

        layout.addSpacing(15)

        # What's New section
        whats_new_label = QLabel("What's New in This Version:")
        whats_new_label.setStyleSheet("color: #FFD700; font-size: 14px; font-weight: bold; background: transparent;")
        layout.addWidget(whats_new_label)

        # Scrollable patch notes
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFixedHeight(280)

        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setSpacing(5)
        scroll_layout.setContentsMargins(15, 15, 15, 15)

        # Parse patch notes
        patch_lines = patch_notes.split('\n')
        for line in patch_lines:
            line = line.strip()
            if line:
                if line.startswith('# '):
                    # Main header
                    note_label = QLabel(line[2:])
                    note_label.setStyleSheet(
                        "color: #FFD700; font-size: 14px; font-weight: bold; background: transparent;")
                    note_label.setWordWrap(True)
                elif line.startswith('## '):
                    # Sub header
                    note_label = QLabel(line[3:])
                    note_label.setStyleSheet(
                        "color: #FFA500; font-size: 13px; font-weight: bold; background: transparent;")
                    note_label.setWordWrap(True)
                elif line.startswith('- '):
                    # Bullet point
                    note_label = QLabel(f"  • {line[2:]}")
                    note_label.setStyleSheet("color: #ffffff; font-size: 12px; background: transparent;")
                    note_label.setWordWrap(True)
                else:
                    # Regular text
                    note_label = QLabel(line)
                    note_label.setStyleSheet("color: #ffffff; font-size: 12px; background: transparent;")
                    note_label.setWordWrap(True)

                scroll_layout.addWidget(note_label)

        scroll_area.setWidget(scroll_content)
        layout.addWidget(scroll_area)

        layout.addSpacing(15)

        # Buttons
        button_layout = QHBoxLayout()

        continue_btn = ModernButton("Continue", primary=True)
        continue_btn.setMinimumWidth(120)
        continue_btn.clicked.connect(dialog.accept)

        github_btn = ModernButton("View Release on GitHub", primary=False)
        github_btn.setMinimumWidth(180)
        github_btn.clicked.connect(lambda: open_github_releases())

        button_layout.addWidget(continue_btn)
        button_layout.addStretch()
        button_layout.addWidget(github_btn)
        layout.addLayout(button_layout)

        # Show dialog
        dialog.exec()

    except Exception as e:
        print(f"Error showing post-update popup: {e}")


def open_github_releases():
    try:
        # Extract repo URL from API URL
        repo_url = GITHUB_API_URL.replace('/releases/latest', '/releases').replace('api.github.com/repos/',
                                                                                   'github.com/')
        webbrowser.open(repo_url)
    except Exception as e:
        print(f"Failed to open GitHub releases: {e}")


def check_post_update_launch(parent):
    """Check if this is a post-update launch and show patch notes"""
    try:
        app_dir = get_app_directory()
        temp_file = os.path.join(app_dir, "update_completed.tmp")

        if os.path.exists(temp_file):
            with open(temp_file, 'r', encoding='utf-8') as f:
                patch_notes = f.read()

            print("Post-update launch detected - will show patch notes")

            # Show post-update popup
            show_post_update_popup(parent, patch_notes)

            # Clean up temp file
            try:
                os.remove(temp_file)
                print("Update completion flag removed")
            except Exception as e:
                print(f"Failed to remove update flag: {e}")

    except Exception as e:
        print(f"Post-update check failed: {e}")
