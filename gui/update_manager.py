import dearpygui.dearpygui as dpg
import requests
import json
import subprocess
import sys
import os
from packaging import version

# Version management
CURRENT_VERSION = "1.0.0"  # Update with each release
VERSION_FILE = "version.txt"
GITHUB_API_URL = "https://api.github.com/repos/AlexBenkarski/TheVault/releases/latest"


def get_app_directory():
    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        return os.path.dirname(sys.executable)
    else:
        # Running as script (development)
        return os.path.dirname(os.path.abspath(__file__))


def get_current_version():
    try:
        app_dir = get_app_directory()
        version_path = os.path.join(app_dir, VERSION_FILE)
        if os.path.exists(version_path):
            with open(version_path, 'r', encoding='utf-8') as f:
                return f.read().strip()
    except Exception as e:
        print(f"Failed to read version file: {e}")
    return CURRENT_VERSION


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

            print(f"Current version: {current_version}")
            print(f"Latest version: {latest_version}")

            if version.parse(latest_version) > version.parse(current_version):
                # Find the .exe asset in the release
                exe_asset = None
                for asset in release_data['assets']:
                    if asset['name'].endswith('.exe') and 'TheVault' in asset['name'] and 'Setup' not in asset['name']:
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


def show_update_popup(update_info):
    with dpg.window(label="Update Available", modal=True, tag="update_popup",
                    width=500, height=450, pos=[350, 175]):

        dpg.add_text(f"Version {update_info['version']} is available!",
                     color=(100, 255, 100))
        dpg.add_spacer(height=10)

        dpg.add_text(f"Current version: {get_current_version()}")
        dpg.add_text(f"Latest version: {update_info['version']}")
        dpg.add_spacer(height=15)

        # Patch notes section
        dpg.add_text("What's New:", color=(255, 255, 100))
        dpg.add_separator()

        # Create scrollable area for patch notes
        with dpg.child_window(height=220, border=True):
            # Split patch notes into lines and display
            patch_lines = update_info['patch_notes'].split('\n')
            for line in patch_lines:
                line = line.strip()
                if line:
                    # Handle markdown-style formatting
                    if line.startswith('# '):
                        dpg.add_text(line[2:], color=(255, 255, 100))
                    elif line.startswith('## '):
                        dpg.add_text(line[3:], color=(200, 200, 100))
                    elif line.startswith('- '):
                        dpg.add_text(f"  • {line[2:]}")
                    else:
                        dpg.add_text(line)

        dpg.add_spacer(height=15)

        # Buttons
        with dpg.group(horizontal=True):
            dpg.add_button(label="Update Now",
                           callback=lambda: start_update_process(update_info),
                           width=120)
            dpg.add_spacer(width=20)
            dpg.add_button(label="Remind Me Later",
                           callback=lambda: dpg.delete_item("update_popup"),
                           width=120)
            dpg.add_spacer(width=20)
            dpg.add_button(label="Skip This Version",
                           callback=lambda: skip_version(update_info['version']),
                           width=120)


def skip_version(version_to_skip):
    try:
        app_dir = get_app_directory()
        skip_file = os.path.join(app_dir, "skip_version.txt")
        with open(skip_file, 'w') as f:
            f.write(version_to_skip)
        print(f"Skipping version {version_to_skip}")
    except Exception as e:
        print(f"Failed to save skip version: {e}")

    dpg.delete_item("update_popup")


def should_skip_version(version_to_check):
    try:
        app_dir = get_app_directory()
        skip_file = os.path.join(app_dir, "skip_version.txt")
        if os.path.exists(skip_file):
            with open(skip_file, 'r') as f:
                skipped_version = f.read().strip()
                return skipped_version == version_to_check
    except:
        pass
    return False


def start_update_process(update_info):
    try:
        # Close update popup
        dpg.delete_item("update_popup")

        # Show updating popup
        with dpg.window(label="Updating...", modal=True, tag="updating_popup",
                        width=350, height=180, pos=[425, 310], no_close=True):
            dpg.add_text("Downloading update...", color=(100, 255, 100))
            dpg.add_spacer(height=10)
            dpg.add_text(f"Version: {update_info['version']}")
            dpg.add_text(f"File: {update_info.get('asset_name', 'TheVault.exe')}")
            dpg.add_spacer(height=10)
            dpg.add_text("The Vault will restart automatically.", color=(255, 255, 100))
            dpg.add_spacer(height=10)
            dpg.add_text("Please wait...", color=(200, 200, 200))

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
                    update_info['download_url'],  # Direct .exe download URL
                    update_info['version'],
                    json.dumps(update_info['patch_notes'])
                ], cwd=app_dir)

                print(f"Updater started with PID: {process.pid}")

                # Give updater a moment to start, then close main app
                dpg.set_frame_callback(30, lambda: dpg.stop_dearpygui())

            except Exception as e:
                raise Exception(f"Failed to start updater process: {str(e)}")
        else:
            # Fallback: open browser to download manually
            print(f"Updater not found at: {updater_path}")
            import webbrowser
            webbrowser.open(update_info['download_url'])
            dpg.delete_item("updating_popup")
            show_error_popup(
                "Updater not found.\n\nThe download will open in your browser.\nPlease download and replace TheVault.exe manually.")

    except Exception as e:
        print(f"Update process failed: {str(e)}")
        if dpg.does_item_exist("updating_popup"):
            dpg.delete_item("updating_popup")
        show_error_popup(f"Update failed: {str(e)}")


def show_error_popup(message):
    with dpg.window(label="Update Error", modal=True, tag="error_popup",
                    width=400, height=200, pos=[400, 300]):

        # Split long messages into multiple lines
        lines = message.split('\n')
        for line in lines:
            if line.strip():
                dpg.add_text(line.strip(), color=(255, 100, 100), wrap=380)

        dpg.add_spacer(height=20)
        dpg.add_button(label="OK", callback=lambda: dpg.delete_item("error_popup"), width=80)


def show_post_update_popup(patch_notes):
    with dpg.window(label="Update Complete!", modal=True, tag="post_update_popup",
                    width=500, height=450, pos=[350, 175]):

        dpg.add_text("The Vault has been updated successfully!",
                     color=(100, 255, 100))
        dpg.add_spacer(height=15)

        dpg.add_text("What's New in This Version:", color=(255, 255, 100))
        dpg.add_separator()

        # Scrollable patch notes
        with dpg.child_window(height=280, border=True):
            patch_lines = patch_notes.split('\n')
            for line in patch_lines:
                line = line.strip()
                if line:
                    # Handle markdown-style formatting
                    if line.startswith('# '):
                        dpg.add_text(line[2:], color=(255, 255, 100))
                    elif line.startswith('## '):
                        dpg.add_text(line[3:], color=(200, 200, 100))
                    elif line.startswith('- '):
                        dpg.add_text(f"  • {line[2:]}")
                    else:
                        dpg.add_text(line)

        dpg.add_spacer(height=15)

        with dpg.group(horizontal=True):
            dpg.add_button(label="Continue",
                           callback=lambda: dpg.delete_item("post_update_popup"),
                           width=120)
            dpg.add_spacer(width=20)
            dpg.add_button(label="View Release on GitHub",
                           callback=lambda: open_github_releases(),
                           width=180)


def open_github_releases():
    try:
        import webbrowser
        # Extract repo URL from API URL
        repo_url = GITHUB_API_URL.replace('/releases/latest', '/releases').replace('api.github.com/repos/',
                                                                                   'github.com/')
        webbrowser.open(repo_url)
    except Exception as e:
        print(f"Failed to open GitHub releases: {e}")


def check_post_update_launch():
    try:
        app_dir = get_app_directory()
        temp_file = os.path.join(app_dir, "update_completed.tmp")

        if os.path.exists(temp_file):
            with open(temp_file, 'r', encoding='utf-8') as f:
                patch_notes = f.read()

            print("Post-update launch detected - will show patch notes")

            # Show post-update popup after a delay to let UI load
            dpg.set_frame_callback(90, lambda: show_post_update_popup(patch_notes))

            # Clean up temp file
            try:
                os.remove(temp_file)
                print("Update completion flag removed")
            except Exception as e:
                print(f"Failed to remove update flag: {e}")

    except Exception as e:
        print(f"Post-update check failed: {e}")


def check_for_updates_with_ui():
    update_info = check_for_updates()

    if update_info['available']:
        # Check if this version should be skipped
        if should_skip_version(update_info['version']):
            print(f"Skipping version {update_info['version']} as requested")
            return update_info

        print("Update available - will show popup")
        return update_info

    return update_info