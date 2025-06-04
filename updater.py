"""
The Vault Auto-Updater
Downloads latest .exe from GitHub releases and replaces current executable.
"""

import sys
import os
import time
import json
import requests
import shutil
import subprocess
from pathlib import Path


def log_message(message):
    print(f"[UPDATER] {message}")
    try:
        app_dir = get_app_directory()
        log_file = os.path.join(app_dir, "updater.log")
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {message}\n")
    except:
        pass


def get_app_directory():
    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        return os.path.dirname(sys.executable)
    else:
        # Running as script (development)
        return os.path.dirname(os.path.abspath(__file__))


def download_exe(download_url, temp_exe_path):
    try:
        log_message(f"Downloading new version...")
        log_message(f"URL: {download_url}")

        headers = {
            'User-Agent': 'TheVault-Updater/1.0',
            'Accept': 'application/octet-stream'
        }

        response = requests.get(download_url, stream=True, headers=headers, timeout=30)
        response.raise_for_status()

        total_size = int(response.headers.get('content-length', 0))
        downloaded = 0

        with open(temp_exe_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)

                    # Show progress
                    if total_size > 0:
                        progress = (downloaded / total_size) * 100
                        print(f"\rDownload Progress: {progress:.1f}%", end='', flush=True)

        print()

        # Verify download
        if os.path.exists(temp_exe_path) and os.path.getsize(temp_exe_path) > 0:
            log_message(f"Download completed successfully! Size: {os.path.getsize(temp_exe_path)} bytes")
            return True
        else:
            log_message("Download failed: File is empty or doesn't exist")
            return False

    except requests.exceptions.RequestException as e:
        log_message(f"Network error during download: {str(e)}")
        return False
    except Exception as e:
        log_message(f"Download failed: {str(e)}")
        return False


def backup_current_exe(current_exe_path, backup_path):
    try:
        log_message("Creating backup of current version...")

        if not os.path.exists(current_exe_path):
            log_message(f"Error: Current executable not found at {current_exe_path}")
            return False

        shutil.copy2(current_exe_path, backup_path)
        log_message(f"Backup created successfully at {backup_path}")
        return True

    except Exception as e:
        log_message(f"Backup failed: {str(e)}")
        return False


def replace_executable(temp_exe_path, current_exe_path, backup_path):
    try:
        log_message("Installing new version...")

        # Wait for main app to fully close
        log_message("Waiting for main application to close...")
        time.sleep(3)

        # Additional check to ensure file isn't locked
        max_attempts = 10
        for attempt in range(max_attempts):
            try:
                # Test if we can open the file for writing
                with open(current_exe_path, 'r+b'):
                    pass
                break
            except (PermissionError, OSError):
                if attempt < max_attempts - 1:
                    log_message(f"File still locked, waiting... (attempt {attempt + 1}/{max_attempts})")
                    time.sleep(2)
                else:
                    raise Exception("Could not access executable file - it may still be running")

        # Remove current executable
        if os.path.exists(current_exe_path):
            os.remove(current_exe_path)
            log_message("Removed old executable")

        # Move new executable to main location
        shutil.move(temp_exe_path, current_exe_path)
        log_message("New executable installed!")

        # Verify the new file is in place and has content
        if os.path.exists(current_exe_path) and os.path.getsize(current_exe_path) > 0:
            log_message(f"Installation verified. New file size: {os.path.getsize(current_exe_path)} bytes")

            # Remove backup since update was successful
            if os.path.exists(backup_path):
                os.remove(backup_path)
                log_message("Backup removed after successful installation")

            return True
        else:
            raise Exception("New executable was not properly installed")

    except Exception as e:
        log_message(f"Installation failed: {str(e)}")

        # Restore backup if something went wrong
        try:
            if os.path.exists(backup_path):
                log_message("Restoring backup...")
                if os.path.exists(current_exe_path):
                    try:
                        os.remove(current_exe_path)
                    except:
                        pass
                shutil.move(backup_path, current_exe_path)
                log_message("Backup restored successfully!")
            else:
                log_message("No backup available to restore!")
        except Exception as restore_error:
            log_message(f"CRITICAL: Failed to restore backup: {restore_error}")
            log_message("Manual intervention may be required!")

        return False


def update_version_file(new_version, app_dir):
    try:
        version_file = os.path.join(app_dir, "version.txt")
        with open(version_file, 'w', encoding='utf-8') as f:
            f.write(new_version)
        log_message(f"Version file updated to {new_version}")
        return True
    except Exception as e:
        log_message(f"Failed to update version file: {str(e)}")
        return False


def create_patch_notes_flag(patch_notes, app_dir):
    try:
        flag_file = os.path.join(app_dir, "update_completed.tmp")
        with open(flag_file, 'w', encoding='utf-8') as f:
            f.write(patch_notes)
        log_message("Patch notes flag created")
        return True
    except Exception as e:
        log_message(f"Failed to create patch notes flag: {str(e)}")
        return False


def restart_application(exe_path):
    try:
        log_message("Restarting The Vault...")

        # Ensure the executable is actually there and executable
        if not os.path.exists(exe_path):
            log_message(f"Error: Executable not found at {exe_path}")
            return False

        # Start the new executable
        app_dir = os.path.dirname(exe_path)
        process = subprocess.Popen([exe_path], cwd=app_dir,
                                   creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)

        log_message(f"The Vault restarted successfully! PID: {process.pid}")
        return True

    except Exception as e:
        log_message(f"Failed to restart application: {str(e)}")
        return False


def cleanup_temp_files(app_dir):
    try:
        temp_patterns = [
            "TheVault_v*_temp.exe",
            "*.tmp"
        ]

        import glob
        for pattern in temp_patterns:
            for file_path in glob.glob(os.path.join(app_dir, pattern)):
                try:
                    os.remove(file_path)
                    log_message(f"Cleaned up: {os.path.basename(file_path)}")
                except:
                    pass
    except Exception as e:
        log_message(f"Cleanup failed: {str(e)}")


def main():
    if len(sys.argv) < 3:
        log_message("Error: Insufficient arguments")
        log_message("Usage: updater.exe <download_url> <new_version> [patch_notes]")
        input("Press Enter to exit...")
        sys.exit(1)

    download_url = sys.argv[1]
    new_version = sys.argv[2]
    patch_notes = sys.argv[3] if len(sys.argv) > 3 else "Update completed successfully!"

    try:
        patch_notes = json.loads(patch_notes)
    except:
        pass

    log_message("=" * 60)
    log_message("THE VAULT AUTO-UPDATER")
    log_message("=" * 60)
    log_message(f"Updating to version: {new_version}")
    log_message(f"Download URL: {download_url}")

    # Setup paths
    app_dir = get_app_directory()
    current_exe_path = os.path.join(app_dir, "TheVault.exe")
    temp_exe_path = os.path.join(app_dir, f"TheVault_v{new_version}_temp.exe")
    backup_exe_path = os.path.join(app_dir, "TheVault_backup.exe")

    log_message(f"App directory: {app_dir}")
    log_message(f"Current executable: {current_exe_path}")

    # Verify current executable exists
    if not os.path.exists(current_exe_path):
        log_message(f"Error: TheVault.exe not found at {current_exe_path}")
        log_message("Please ensure the updater is in the same directory as TheVault.exe")
        input("Press Enter to exit...")
        sys.exit(1)

    success = False

    try:
        # Step 1: Download new executable
        log_message("Step 1/5: Downloading new version...")
        if not download_exe(download_url, temp_exe_path):
            raise Exception("Failed to download new version")

        # Step 2: Create backup
        log_message("Step 2/5: Creating backup...")
        if not backup_current_exe(current_exe_path, backup_exe_path):
            raise Exception("Failed to create backup")

        # Step 3: Replace executable
        log_message("Step 3/5: Installing new version...")
        if not replace_executable(temp_exe_path, current_exe_path, backup_exe_path):
            raise Exception("Failed to install new version")

        # Step 4: Update version file and create patch notes flag
        log_message("Step 4/5: Updating configuration...")
        update_version_file(new_version, app_dir)
        create_patch_notes_flag(patch_notes, app_dir)

        # Step 5: Restart application
        log_message("Step 5/5: Restarting The Vault...")
        if restart_application(current_exe_path):
            success = True
            log_message("Update completed successfully!")
        else:
            log_message("Warning: Update completed but failed to restart application")
            log_message("Please manually start The Vault")
            success = True  # Update still successful

    except Exception as e:
        log_message(f"Update failed: {str(e)}")
        log_message("The original version should be restored.")

    finally:
        # Cleanup temporary files
        cleanup_temp_files(app_dir)

    # Keep console open briefly to show final status
    if success:
        log_message("Update process completed successfully!")
        log_message("Updater will close in 3 seconds...")
        time.sleep(3)
    else:
        log_message("Update process failed!")
        log_message("Check updater.log for details.")
        log_message("Press Enter to exit...")
        input()


if __name__ == "__main__":
    main()