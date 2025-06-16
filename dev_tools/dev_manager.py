DEV_MODE_ACTIVE = False
MOCK_VAULT_KEY = b"dev_mock_key_32_bytes_padding_xx"
CURRENT_PRESET = "small"


# =============================================================================
# DEV MODE FUNCTIONS - MENU SYSTEM
# =============================================================================

def show_dev_category_menu():
    print("\n" + "=" * 50)
    print("TheVault DEV MODE - Category Menu")
    print("=" * 50)
    print("1. Main Windows")
    print("2. Popups & Dialogs")
    print("3. Special States")
    print("4. Quick Actions")


def show_main_windows_menu():
    print("\n" + "=" * 40)
    print("MAIN WINDOWS:")
    print("=" * 40)
    print("1. Login View")
    print("2. Signup View")
    print("3. Recovery View")
    print("4. Vault View")


def show_popups_menu():
    print("\n" + "=" * 40)
    print("POPUPS & DIALOGS:")
    print("=" * 40)
    print("1. Settings Dialog")
    print("2. Add Folder Popup")
    print("3. Add Entry Popup")
    print("4. Edit Entry Popup")
    print("5. Delete Confirmation")
    print("6. Recovery Key Dialog")
    print("7. Password Reset Dialog")
    print("8. Update Available")
    print("9. Update Complete")


def show_special_states_menu():
    print("\n" + "=" * 40)
    print("SPECIAL STATES:")
    print("=" * 40)
    print("1. Empty Vault")
    print("2. Vault with 100+ passwords")
    print("3. Massive Vault (100 folders, 100 entries each)")


def show_quick_actions_menu():
    print("\n" + "=" * 40)
    print("QUICK ACTIONS:")
    print("=" * 40)
    print("1. Load Small Preset (5 passwords)")
    print("2. Load Large Preset (100+ passwords)")


def get_category_choice():
    """Get category selection with navigation options"""
    while True:
        choice = input("\nEnter choice (1-4) or 'q' to quit: ")
        if choice.lower() == 'q':
            return 'q'
        try:
            choice_num = int(choice)
            if 1 <= choice_num <= 4:
                return choice_num
            else:
                print("Please enter 1-4 or 'q'")
        except ValueError:
            print("Please enter a valid number or 'q'")


def get_submenu_choice(max_options):
    """Get submenu selection with navigation options"""
    while True:
        choice = input(f"\nEnter choice (1-{max_options}), 'b' for back, or 'q' to quit: ")
        if choice.lower() == 'q':
            return 'q'
        elif choice.lower() == 'b':
            return 'b'
        try:
            choice_num = int(choice)
            if 1 <= choice_num <= max_options:
                return choice_num
            else:
                print(f"Please enter 1-{max_options}, 'b', or 'q'")
        except ValueError:
            print("Please enter a valid number, 'b', or 'q'")


def execute_main_window_command(choice, window):
    """Execute main window commands (1.1, 1.2, etc.)"""
    execute_dev_command(f"1.{choice}", window)


def execute_popup_command(choice, window):
    """Execute popup commands (2.1, 2.2, etc.)"""
    execute_dev_command(f"2.{choice}", window)


def execute_special_state_command(choice, window):
    """Execute special state commands (3.1, 3.2, etc.)"""
    execute_dev_command(f"3.{choice}", window)


def execute_quick_action_command(choice, window):
    """Execute quick action commands (4.1, 4.2, etc.)"""
    execute_dev_command(f"4.{choice}", window)


def execute_dev_command(command_id, window):
    """Execute dev commands using hierarchical IDs (e.g., '1.4', '2.1')"""
    print(f"Executing command {command_id}")

    from PyQt6.QtCore import QEvent, QCoreApplication

    class DevCommandEvent(QEvent):
        def __init__(self, command_id):
            super().__init__(QEvent.Type.User)
            self.command_id = command_id

    QCoreApplication.postEvent(window, DevCommandEvent(command_id))


def persistent_dev_cli(window):
    """Main dev CLI loop with hierarchical navigation"""
    try:
        while True:
            show_dev_category_menu()
            category = get_category_choice()

            if category == 'q':
                import os
                os._exit(0)

            while True:
                if category == 1:  # Main Windows
                    show_main_windows_menu()
                    choice = get_submenu_choice(4)
                    if choice == 'b':
                        break
                    elif choice == 'q':
                        import os
                        os._exit(0)
                    else:
                        execute_main_window_command(choice, window)

                elif category == 2:  # Popups & Dialogs
                    show_popups_menu()
                    choice = get_submenu_choice(9)
                    if choice == 'b':
                        break
                    elif choice == 'q':
                        import os
                        os._exit(0)
                    else:
                        execute_popup_command(choice, window)

                elif category == 3:  # Special States
                    show_special_states_menu()
                    choice = get_submenu_choice(3)
                    if choice == 'b':
                        break
                    elif choice == 'q':
                        import os
                        os._exit(0)
                    else:
                        execute_special_state_command(choice, window)

                elif category == 4:  # Quick Actions
                    show_quick_actions_menu()
                    choice = get_submenu_choice(2)
                    if choice == 'b':
                        break
                    elif choice == 'q':
                        import os
                        os._exit(0)
                    else:
                        execute_quick_action_command(choice, window)

                break

    except (EOFError, KeyboardInterrupt):
        import os
        os._exit(0)

def get_mock_credentials():
    return MOCK_VAULT_KEY, "dev_user"

def get_current_mock_data():
    from .mock_data import get_mock_vault_data
    return get_mock_vault_data(CURRENT_PRESET)

def set_dev_mode(active: bool):
    global DEV_MODE_ACTIVE
    DEV_MODE_ACTIVE = active

def set_current_preset(preset_name: str):
    global CURRENT_PRESET
    CURRENT_PRESET = preset_name

