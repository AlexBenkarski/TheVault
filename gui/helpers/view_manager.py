import dearpygui.dearpygui as dpg

def set_view(view_function):

    if dpg.does_item_exist("MainWindow"):
        dpg.delete_item("MainWindow", children_only=True)
    else:
        with dpg.window(tag="MainWindow"):
            pass

    # Push MainWindow as the current parent before rendering view
    dpg.push_container_stack("MainWindow")
    view_function()
    dpg.pop_container_stack()