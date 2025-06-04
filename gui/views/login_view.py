from dearpygui import dearpygui as dpg
from core.vault_manager import user_verification
from gui.views.recovery_view import show_recovery_view
from gui.helpers.view_manager import set_view



def show_login_view():
    with dpg.child_window(parent="MainWindow", tag="LoginWindow", border=False):
        dpg.add_spacer(height=5)

        with dpg.group(horizontal=True):
            dpg.add_spacer(width=400)
            dpg.add_image("logo_texture", width=300, height=300)

        dpg.add_spacer(height=0)

        with dpg.group(horizontal=True):
            dpg.add_spacer(width=450)
            dpg.add_text("", tag="login_error_text", color=(255, 0, 0))

        dpg.add_spacer(height=0)

        with dpg.group(horizontal=True):
            dpg.add_spacer(width=450)
            dpg.add_input_text(label="", width=200, hint="Username", tag="login_username")

        dpg.add_spacer(height=0)

        with dpg.group(horizontal=True):
            dpg.add_spacer(width=450)
            dpg.add_input_text(label="", width=200, hint="Password", password=True, tag="login_password")


        dpg.add_spacer(height=5)

        with dpg.group(horizontal=True):
            dpg.add_spacer(width=450)
            dpg.add_button(label="Forgot Password?", width=120, callback=lambda: set_view(show_recovery_view))
            dpg.add_spacer(width=2)
            dpg.add_button(label="Log In", width=60, callback=lambda: try_login())



def try_login():
    input_username = dpg.get_value("login_username")
    input_password = dpg.get_value("login_password")

    key, user = user_verification(input_username, input_password)
    if key:
        from gui.views.vault_view import show_vault_view
        set_view(lambda: show_vault_view(key, user))
    else:
        dpg.set_value("login_error_text", "Invalid username or password")
