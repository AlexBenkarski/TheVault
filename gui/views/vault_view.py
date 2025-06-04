import dearpygui.dearpygui as dpg
from core.vault_manager import load_vault, save_vault, add_folder
from gui.helpers.view_manager import set_view
from gui.views.login_view import show_login_view


_selected_folder = None
_vault_data = {}
_vault_key = None


def load_folder(sender, app_data, user_data):
    global _selected_folder
    folder_name = user_data

    if folder_name in _vault_data.get("data", {}):
        _selected_folder = folder_name
        redraw_vault()
    else:
        print(f"Error: Folder {folder_name} not found in vault data")


def redraw_vault():
    if dpg.does_item_exist("vault_view"):
        dpg.delete_item("vault_view")

    with dpg.group(parent="MainWindow", tag="vault_view"):
        with dpg.table(header_row=False, policy=dpg.mvTable_SizingStretchProp):
            dpg.add_table_column(init_width_or_weight=0.8)
            dpg.add_table_column(init_width_or_weight=0.2)

            with dpg.table_row():
                with dpg.table_cell():
                    dpg.add_text("Your Vault", color=(255, 255, 255))
                with dpg.table_cell():
                    with dpg.group(horizontal=True):
                        dpg.add_spacer()
                        dpg.add_button(
                            label=f"{_vault_data.get('username', 'Unknown')}",
                            callback=show_user_menu,
                            width=120
                        )

        dpg.add_separator()
        dpg.add_spacer(height=10)

        # Folders section
        dpg.add_text("Folders:", color=(200, 200, 200))

        # Create a scrollable window for folders with reduced height
        with dpg.child_window(height=130, width=-1, horizontal_scrollbar=True, border=False):
            # Force single line
            with dpg.group(horizontal=True):

                dpg.add_spacer(height=10)

                # Get folder list and add buttons
                folders = ["+"] + list(_vault_data.get("data", {}).keys())
                for folder in folders:
                    if folder == "+":
                        dpg.add_button(
                            label="   [+]\nNew Folder",
                            callback=add_folder_callback,
                            width=100,
                            height=100
                        )
                    else:
                        dpg.add_button(
                            label=folder,
                            callback=load_folder,
                            user_data=folder,
                            width=100,
                            height=100
                        )
                    dpg.add_spacer(width=10)

                dpg.add_spacer(height=10)

        dpg.add_spacer(height=10)
        dpg.add_separator()
        dpg.add_spacer(height=10)

        # Selected Folder Section
        if _selected_folder and "data" in _vault_data:
            folder_data = _vault_data["data"].get(_selected_folder)
            if folder_data:
                with dpg.group(horizontal=True):
                    dpg.add_text(f"Selected Folder: {_selected_folder}", color=(200, 200, 200))
                    dpg.add_spacer(width=20)
                    dpg.add_button(label="Edit", callback=rename_folder_callback, width=80)
                    dpg.add_spacer(width=5)
                    dpg.add_button(label="Delete", callback=delete_folder_callback, width=80)

                dpg.add_spacer(height=10)

                # Entry Table
                with dpg.table(header_row=True,
                               policy=dpg.mvTable_SizingFixedFit,
                               borders_innerH=True,
                               borders_outerH=True,
                               borders_innerV=True,
                               borders_outerV=True,
                               row_background=True):

                    # First add all columns with fixed width
                    schema = folder_data.get("schema", ["Website", "Username", "Password"])

                    # Calculate width for each field column
                    field_width = 200  # Base width for field columns

                    # Add regular columns with fixed width
                    for field in schema:
                        dpg.add_table_column(
                            label=field,
                            width=field_width,
                            init_width_or_weight=field_width
                        )

                    # Add actions column with fixed width
                    actions_width = 150
                    dpg.add_table_column(
                        label="Actions",
                        width=actions_width,
                        init_width_or_weight=actions_width
                    )

                    # Add entries
                    entries = folder_data.get("entries", [])
                    for entry_idx, entry in enumerate(entries):
                        with dpg.table_row():
                            for field in schema:
                                with dpg.table_cell():
                                    with dpg.group(horizontal=True):
                                        # Create a group for the text and buttons
                                        with dpg.group(horizontal=True,
                                                       width=field_width - 90):
                                            if field.lower() == "password":
                                                dpg.add_text("********", tag=f"hidden_pwd_{entry_idx}_{field}")
                                                dpg.add_text(entry.get(field, ""),
                                                             tag=f"visible_pwd_{entry_idx}_{field}",
                                                             show=False)
                                            else:
                                                dpg.add_text(entry.get(field, ""))

                                        # Show/Hide button for passwords
                                        if field.lower() == "password":
                                            dpg.add_button(
                                                label="Show",
                                                callback=toggle_password_visibility,
                                                user_data=(entry_idx, field, entry.get(field, "")),
                                                width=35,
                                                tag=f"toggle_btn_{entry_idx}_{field}"
                                            )

                                        dpg.add_button(
                                            label="Copy",
                                            callback=copy_to_clipboard,
                                            user_data=(entry.get(field, ""), field),
                                            width=35
                                        )

                            # Actions column
                            with dpg.table_cell():
                                with dpg.group(horizontal=True):
                                    dpg.add_button(
                                        label="Edit",
                                        callback=edit_entry_callback,
                                        user_data=(entry_idx, entry),
                                        width=60
                                    )
                                    dpg.add_spacer(width=5)
                                    dpg.add_button(
                                        label="X",
                                        callback=delete_entry_callback,
                                        user_data=(entry_idx, entry),
                                        width=60
                                    )

                dpg.add_spacer(height=20)
                dpg.add_button(label="Add New Entry", width=200, callback=add_entry_callback)
        else:
            dpg.add_text("No folder selected.", color=(150, 150, 150))


def show_vault_view(key, user):
    global _vault_data, _selected_folder, _vault_key
    vault_data = load_vault(key)

    _vault_key = key

    _vault_data = {
        "username": user,
        "data": vault_data
    }
    _selected_folder = None
    redraw_vault()


def confirm_rename():
    global _selected_folder
    new_name = dpg.get_value("new_folder_name")
    if not new_name:
        dpg.set_value("rename_error", "Name cannot be empty")
        return

    if new_name in _vault_data.get("data", {}):
        dpg.set_value("rename_error", "A folder with this name already exists")
        return

    # rename
    data = _vault_data.get("data", {})
    data[new_name] = data.pop(_selected_folder)
    save_vault(data, _vault_key)

    # Update the view
    _selected_folder = new_name
    redraw_vault()
    dpg.delete_item("rename_modal")


def confirm_delete():
    global _selected_folder
    data = _vault_data.get("data", {})
    data.pop(_selected_folder)
    save_vault(data, _vault_key)

    # Update the view
    _selected_folder = None
    redraw_vault()
    dpg.delete_item("delete_modal")


def show_user_menu():
    # Create a popup window for user menu
    with dpg.window(label="User Menu", modal=True, show=True, tag="user_menu_modal",
                    width=200, height=120, pos=[600, 100]):
        dpg.add_button(label="Settings", callback=settings_callback, width=150)
        dpg.add_spacer(height=5)
        dpg.add_button(label="Sign Out", callback=logout_callback, width=150)
        dpg.add_spacer(height=5)
        dpg.add_button(label="Cancel", callback=lambda: dpg.delete_item("user_menu_modal"), width=150)


def settings_callback():
    print("Settings callback triggered!")

    # Close the user menu first
    if dpg.does_item_exist("user_menu_modal"):
        print("Closing user menu modal")
        dpg.delete_item("user_menu_modal")

    # Clean up existing settings modal
    if dpg.does_item_exist("settings_modal"):
        print("Deleting existing settings modal")
        dpg.delete_item("settings_modal")

    print("About to create settings modal...")

    try:
        settings_window = dpg.add_window(
            label="Settings",
            show=True,
            tag="settings_modal",
            width=500,
            height=400,
            pos=[350, 200],
            no_close=False,
            no_collapse=True,
            no_resize=True
        )

        print(f"Settings window created with ID: {settings_window}")

        dpg.add_text("Account Settings", color=(255, 255, 255), parent="settings_modal")
        dpg.add_separator(parent="settings_modal")
        dpg.add_spacer(height=10, parent="settings_modal")

        # Username section
        dpg.add_text("Username:", parent="settings_modal")
        dpg.add_input_text(
            default_value=_vault_data.get('username', ''),
            tag="settings_username",
            width=200,
            readonly=True,
            parent="settings_modal"
        )

        dpg.add_spacer(height=10, parent="settings_modal")
        dpg.add_text("Security Settings", color=(255, 255, 255), parent="settings_modal")
        dpg.add_separator(parent="settings_modal")
        dpg.add_spacer(height=10, parent="settings_modal")

        # Change password section
        dpg.add_text("Change Master Password:", parent="settings_modal")
        dpg.add_spacer(height=5, parent="settings_modal")

        dpg.add_input_text(
            label="Current Password",
            tag="current_password",
            password=True,
            width=200,
            parent="settings_modal",
            readonly=True,
            hint="Coming soon..."
        )
        dpg.add_spacer(height=5, parent="settings_modal")

        dpg.add_input_text(
            label="New Password",
            tag="new_password",
            password=True,
            width=200,
            parent="settings_modal",
            readonly=True,
            hint="Coming soon..."
        )
        dpg.add_spacer(height=5, parent="settings_modal")

        dpg.add_input_text(
            label="Confirm New Password",
            tag="confirm_password",
            password=True,
            width=200,
            parent="settings_modal",
            readonly=True,
            hint="Coming soon..."
        )
        dpg.add_spacer(height=5, parent="settings_modal")

        dpg.add_text("Feature coming soon...", tag="password_change_info", color=(150, 150, 150),
                     parent="settings_modal")
        dpg.add_spacer(height=10, parent="settings_modal")


        button_group = dpg.add_group(horizontal=True, parent="settings_modal")

        dpg.add_button(
            label="Change Password",
            callback=change_password_callback,
            width=120,
            parent=button_group,
            enabled=False
        )
        dpg.add_spacer(width=10, parent=button_group)
        dpg.add_button(
            label="Export Vault",
            callback=export_vault_callback,
            width=120,
            parent=button_group
        )
        dpg.add_spacer(width=10, parent=button_group)
        dpg.add_button(
            label="Close",
            callback=close_settings_modal,
            width=120,
            parent=button_group
        )

        dpg.show_item("settings_modal")
        dpg.focus_item("settings_modal")

        print("Settings modal should now be visible")

    except Exception as e:
        print(f"Error creating settings modal: {e}")
        import traceback
        traceback.print_exc()


def close_settings_modal():
    print("Closing settings modal")
    if dpg.does_item_exist("settings_modal"):
        dpg.delete_item("settings_modal")


def change_password_callback():
    current_pwd = dpg.get_value("current_password")
    new_pwd = dpg.get_value("new_password")
    confirm_pwd = dpg.get_value("confirm_password")

    # Clear previous messages
    dpg.set_value("password_change_error", "")
    dpg.set_value("password_change_success", "")

    # Validate inputs
    if not current_pwd or not new_pwd or not confirm_pwd:
        dpg.set_value("password_change_error", "All fields are required")
        return

    if new_pwd != confirm_pwd:
        dpg.set_value("password_change_error", "New passwords do not match")
        return

    if len(new_pwd) < 6:
        dpg.set_value("password_change_error", "Password must be at least 6 characters")
        return

    dpg.set_value("password_change_success", "Password changed successfully!")

    # Clear the input fields
    dpg.set_value("current_password", "")
    dpg.set_value("new_password", "")
    dpg.set_value("confirm_password", "")


def export_vault_callback():
    try:
        import json
        from tkinter import filedialog
        import tkinter as tk


        root = tk.Tk()
        root.withdraw()

        # Ask user where to save the export
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Export Vault"
        )

        if file_path:

            export_data = {
                "username": _vault_data.get("username"),
                "data": _vault_data.get("data", {}),
            }

            with open(file_path, 'w') as f:
                json.dump(export_data, f, indent=2)

            print(f"Vault exported successfully to: {file_path}")

        root.destroy()

    except ImportError:
        print("Error: tkinter module not available for file dialog")
    except Exception as e:
        print(f"Error exporting vault: {e}")


def logout_callback():
    if dpg.does_item_exist("user_menu_modal"):
        dpg.delete_item("user_menu_modal")

    # Save and encrypt the vault before logging out
    if _vault_data and "data" in _vault_data and _vault_key:
        save_vault(_vault_data["data"], _vault_key)
        print("Vault saved and encrypted before logout")

    set_view(show_login_view)


def add_folder_callback():
    # Create a modal popup for adding a new folder
    with dpg.window(label="Create New Folder", modal=True, show=True, tag="add_folder_modal",
                    width=400, height=200, pos=[400, 300]):
        dpg.add_text("Enter folder details:")
        dpg.add_spacer(height=5)

        dpg.add_input_text(label="", hint="Enter folder name", tag="new_folder_name", width=200)
        dpg.add_spacer(height=5)

        dpg.add_input_text(label="",
                           hint="Enter Fields",
                           tag="new_folder_fields",
                           width=200)

        dpg.add_text("", tag="create_folder_error", color=(255, 0, 0))
        dpg.add_spacer(height=5)

        def confirm_create():
            global _vault_data
            new_folder_name = dpg.get_value("new_folder_name")
            new_folder_fields = dpg.get_value("new_folder_fields")

            if not new_folder_name or not new_folder_fields:
                dpg.set_value("create_folder_error", "Folder name and fields are required")
                return

            if new_folder_name in _vault_data.get("data", {}):
                dpg.set_value("create_folder_error", "A folder with this name already exists")
                return

            # Create the folder
            add_folder(_vault_key, new_folder_name, new_folder_fields)

            # Reload vault data
            _vault_data["data"] = load_vault(_vault_key)

            # Close modal and redraw
            dpg.delete_item("add_folder_modal")
            redraw_vault()

        def cancel_create():
            dpg.delete_item("add_folder_modal")

        with dpg.group(horizontal=True):
            dpg.add_button(label="Create", callback=confirm_create, width=100)
            dpg.add_spacer(width=10)
            dpg.add_button(label="Cancel", callback=cancel_create, width=100)


def rename_folder_callback():
    if not _selected_folder:
        return

    # Create a modal popup for rename
    with dpg.window(label="Rename Folder", modal=True, show=True, tag="rename_modal",
                    width=400, height=150, pos=[400, 300]):
        dpg.add_text("Enter new name for folder:")
        dpg.add_input_text(tag="new_folder_name", width=200)
        dpg.add_text("", tag="rename_error", color=(255, 0, 0))

        with dpg.group(horizontal=True):
            dpg.add_button(label="Confirm", callback=confirm_rename)
            dpg.add_button(label="Cancel", callback=lambda: dpg.delete_item("rename_modal"))


def delete_folder_callback():
    if not _selected_folder:
        return

    # Create a popup for confirmation
    with dpg.window(label="Delete Folder", modal=True, show=True, tag="delete_modal",
                    width=400, height=150, pos=[400, 300]):
        dpg.add_text(f"Are you sure you want to delete folder '{_selected_folder}'?")
        dpg.add_text("This action cannot be undone!", color=(255, 150, 150))

        with dpg.group(horizontal=True):
            dpg.add_button(label="Yes, Delete", callback=confirm_delete, width=100)
            dpg.add_button(label="Cancel", callback=lambda: dpg.delete_item("delete_modal"), width=100)


def add_entry_callback():
    if not _selected_folder:
        return

    folder_data = _vault_data["data"][_selected_folder]
    schema = folder_data.get("schema", [])

    # Create a popup for adding new entry
    with dpg.window(label="Add New Entry", modal=True, show=True, tag="add_entry_modal",
                    width=400, height=300, pos=[400, 250]):
        dpg.add_text(f"Add entry to folder: {_selected_folder}")
        dpg.add_separator()
        dpg.add_spacer(height=5)

        # Create input fields dynamically based on schema
        input_tags = {}
        for field in schema:
            tag = f"new_entry_{field.lower()}"
            input_tags[field] = tag

            if field.lower() == "password":
                dpg.add_input_text(
                    label=field,
                    width=200,
                    password=True,
                    tag=tag
                )
            else:
                dpg.add_input_text(
                    label=field,
                    width=200,
                    tag=tag
                )
            dpg.add_spacer(height=2)

        dpg.add_text("", tag="add_entry_error", color=(255, 0, 0))
        dpg.add_spacer(height=5)

        def confirm_add():
            global _vault_data

            # Collect values from all fields
            new_entry = {}
            has_empty = False

            for field, tag in input_tags.items():
                value = dpg.get_value(tag)
                if not value:
                    has_empty = True
                new_entry[field] = value

            if has_empty:
                dpg.set_value("add_entry_error", "All fields are required")
                return

            # Add the new entry
            _vault_data["data"][_selected_folder]["entries"].append(new_entry)

            # Save the updated vault
            save_vault(_vault_data["data"], _vault_key)

            # Close modal and redraw
            dpg.delete_item("add_entry_modal")
            redraw_vault()

        def cancel_add():
            dpg.delete_item("add_entry_modal")

        dpg.add_separator()
        with dpg.group(horizontal=True):
            dpg.add_button(label="Add Entry", callback=confirm_add, width=120)
            dpg.add_spacer(width=10)
            dpg.add_button(label="Cancel", callback=cancel_add, width=120)


def edit_entry_callback(sender, app_data, user_data=None):
    if not user_data or not _selected_folder:
        print("Error: No entry provided for editing")
        return

    entry_idx, entry = user_data
    folder_data = _vault_data["data"][_selected_folder]
    schema = folder_data.get("schema", [])

    # Create a popup for editing entry
    with dpg.window(label="Edit Entry", modal=True, show=True, tag="edit_entry_modal",
                    width=400, height=300, pos=[400, 250]):
        dpg.add_text(f"Edit entry in folder: {_selected_folder}")
        dpg.add_separator()
        dpg.add_spacer(height=5)

        # Create input fields dynamically based on schema
        input_tags = {}
        for field in schema:
            tag = f"edit_entry_{field.lower()}"
            input_tags[field] = tag
            current_value = entry.get(field, "")

            if field.lower() == "password":
                dpg.add_input_text(
                    label=field,
                    default_value=current_value,
                    width=200,
                    password=True,
                    tag=tag
                )
            else:
                dpg.add_input_text(
                    label=field,
                    default_value=current_value,
                    width=200,
                    tag=tag
                )
            dpg.add_spacer(height=2)

        dpg.add_text("", tag="edit_entry_error", color=(255, 0, 0))
        dpg.add_spacer(height=5)

        def confirm_edit():
            # Collect values from all fields
            updated_entry = {}
            has_empty = False

            for field, tag in input_tags.items():
                value = dpg.get_value(tag)
                if not value:
                    has_empty = True
                updated_entry[field] = value

            if has_empty:
                dpg.set_value("edit_entry_error", "All fields are required")
                return

            # Update the entry using the stored index
            folder_data["entries"][entry_idx] = updated_entry

            # Save the updated vault
            save_vault(_vault_data["data"], _vault_key)

            # Close modal and redraw
            dpg.delete_item("edit_entry_modal")
            redraw_vault()

        def cancel_edit():
            dpg.delete_item("edit_entry_modal")

        dpg.add_separator()
        with dpg.group(horizontal=True):
            dpg.add_button(label="Save Changes", callback=confirm_edit, width=120)
            dpg.add_spacer(width=10)
            dpg.add_button(label="Cancel", callback=cancel_edit, width=120)


def delete_entry_callback(sender, app_data, user_data=None):
    if isinstance(user_data, tuple):
        entry_idx, entry = user_data
    else:
        print("Error: Invalid user_data format")
        return

    # Create a popup for confirmation
    with dpg.window(label="Delete Entry", modal=True, show=True, tag="delete_entry_modal",
                    width=400, height=150, pos=[400, 300]):
        dpg.add_text("Are you sure you want to delete this entry?")
        dpg.add_text("This action cannot be undone!", color=(255, 150, 150))

        def confirm_delete_entry():
            # Get current folder and remove entry by index
            folder_name = _selected_folder
            if folder_name in _vault_data["data"]:
                folder_data = _vault_data["data"][folder_name]
                folder_data["entries"].pop(entry_idx)
                # Save changes to vault
                save_vault(_vault_data["data"], _vault_key)

            # Close modal and redraw vault view
            dpg.delete_item("delete_entry_modal")
            redraw_vault()

        with dpg.group(horizontal=True):
            dpg.add_button(label="Yes, Delete", callback=confirm_delete_entry, width=100)
            dpg.add_button(label="Cancel", callback=lambda: dpg.delete_item("delete_entry_modal"), width=100)


def copy_to_clipboard(sender, app_data, user_data):
    try:
        import pyperclip
        value, field = user_data
        pyperclip.copy(value)
        print(f"{field} copied to clipboard!")
    except ImportError:
        print("Error: pyperclip module not found. Please install it with: pip install pyperclip")
    except Exception as e:
        print(f"Error copying to clipboard: {e}")


def toggle_password_visibility(sender, app_data, user_data):
    entry_idx, field, password_value = user_data

    hidden_tag = f"hidden_pwd_{entry_idx}_{field}"
    visible_tag = f"visible_pwd_{entry_idx}_{field}"
    button_tag = f"toggle_btn_{entry_idx}_{field}"

    # Check if password is currently hidden
    if dpg.does_item_exist(hidden_tag) and dpg.does_item_exist(visible_tag):
        is_hidden = dpg.get_item_configuration(hidden_tag)["show"]

        if is_hidden:
            # Currently showing ********, switch to actual password
            dpg.configure_item(hidden_tag, show=False)
            dpg.configure_item(visible_tag, show=True)
            dpg.configure_item(button_tag, label="Hide")
        else:
            # Currently showing password, switch to ********
            dpg.configure_item(hidden_tag, show=True)
            dpg.configure_item(visible_tag, show=False)
            dpg.configure_item(button_tag, label="Show")


def copy_password_callback(entry):
    try:
        import pyperclip
        if "Password" in entry:
            pyperclip.copy(entry["Password"])
    except ImportError:
        print("Error: pyperclip module not found.")

