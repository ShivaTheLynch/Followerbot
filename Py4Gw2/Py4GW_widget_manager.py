from Py4GWCoreLib import *
import importlib.util
import os

module_name = "Widget Manager"

class WidgetHandler:
    def __init__(self, widgets_path="Widgets"):
        self.widgets_path = widgets_path
        self.widgets = {}  # {widget_name: {"module": module, "enabled": False},"configuring": False}

    def discover_widgets(self):
        """Discover and load all valid widgets from the widgets directory."""
        try:
            for file in os.listdir(self.widgets_path):
                if file.endswith(".py"):
                    widget_path = os.path.join(self.widgets_path, file)
                    widget_name = os.path.splitext(file)[0]
                    try:
                        self.widgets[widget_name] = {
                            "module": self.load_widget(widget_path),
                            "enabled": False,
                            "configuring": False
                        }
                        Py4GW.Console.Log("WidgetHandler", f"Loaded widget: {widget_name}", Py4GW.Console.MessageType.Info)
                    except Exception as e:
                        Py4GW.Console.Log("WidgetHandler", f"Failed to load widget {widget_name}: {str(e)}", Py4GW.Console.MessageType.Error)
                        Py4GW.Console.Log("WidgetHandler", f"Stack trace: {traceback.format_exc()}", Py4GW.Console.MessageType.Error)
        except Exception as e:
            Py4GW.Console.Log("WidgetHandler", f"Unexpected error during widget discovery: {str(e)}", Py4GW.Console.MessageType.Error)
            Py4GW.Console.Log("WidgetHandler", f"Stack trace: {traceback.format_exc()}", Py4GW.Console.MessageType.Error)

    def load_widget(self, widget_path):
        """Load a widget module dynamically from the given path."""
        try:
            spec = importlib.util.spec_from_file_location("widget", widget_path)
            widget_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(widget_module)

            if not hasattr(widget_module, "main") or not hasattr(widget_module, "configure"):
                raise ValueError("Widget is missing required functions: main() and configure()")

            return widget_module
        except ImportError as e:
            raise ImportError(f"ImportError encountered while loading widget: {str(e)}")
        except Exception as e:
            raise Exception(f"Unexpected error during widget loading: {str(e)}")

    def execute_enabled_widgets(self):
        """Execute the main() function of all enabled widgets."""
        try:
            for widget_name, widget_info in self.widgets.items():
                if widget_info["enabled"]:
                    try:
                        widget_info["module"].main()
                    except Exception as e:
                        Py4GW.Console.Log("WidgetHandler", f"Error executing widget {widget_name}: {str(e)}", Py4GW.Console.MessageType.Error)
                        Py4GW.Console.Log("WidgetHandler", f"Stack trace: {traceback.format_exc()}", Py4GW.Console.MessageType.Error)
        except Exception as e:
            Py4GW.Console.Log("WidgetHandler", f"Unexpected error during widget execution: {str(e)}", Py4GW.Console.MessageType.Error)
            Py4GW.Console.Log("WidgetHandler", f"Stack trace: {traceback.format_exc()}", Py4GW.Console.MessageType.Error)

    def execute_configuring_widgets(self):
        """Execute the main() function of all configuring widgets."""
        try:
            for widget_name, widget_info in self.widgets.items():
                if widget_info["configuring"]:
                    try:
                        widget_info["module"].configure()
                    except Exception as e:
                        Py4GW.Console.Log("WidgetHandler", f"Error executing widget {widget_name}: {str(e)}", Py4GW.Console.MessageType.Error)
                        Py4GW.Console.Log("WidgetHandler", f"Stack trace: {traceback.format_exc()}", Py4GW.Console.MessageType.Error)
        except Exception as e:
            Py4GW.Console.Log("WidgetHandler", f"Unexpected error during widget execution: {str(e)}", Py4GW.Console.MessageType.Error)
            Py4GW.Console.Log("WidgetHandler", f"Stack trace: {traceback.format_exc()}", Py4GW.Console.MessageType.Error)


initialized = False
handler = WidgetHandler("Widgets")
enable_all = True
window_module = ImGui.WindowModule(module_name, window_name="Widget Manager", window_size=(100, 100), window_flags=PyImGui.WindowFlags.AlwaysAutoResize)
overlay = Overlay()

class config:
    def __init__(self):
        self.x = 100
        self.y = 100
        self.scale = 2.0
        self.color=0xFFFF0000
        self.string = "00:00:00:000"

widget_config = config()

def main():
    global module_name,window_module, initialized, handler, enable_all, overlay, widget_config
    try:
        if not initialized:
            handler.discover_widgets()
            initialized = True

        if PyImGui.begin(window_module.window_name, window_module.window_flags):
            enable_all = PyImGui.checkbox("Toggle All Widgets", enable_all)
            PyImGui.separator()

            if enable_all:
                if PyImGui.begin_table("Widgets", 2,PyImGui.TableFlags.Borders):
                    for widget_name, widget_info in handler.widgets.items():
                        status = "enabled" if widget_info["enabled"] else "disabled"
                        PyImGui.table_next_row()
                        PyImGui.table_set_column_index(0)
                        widget_info["enabled"] = PyImGui.checkbox(f"{widget_name}", widget_info["enabled"])
                        PyImGui.table_set_column_index(1)
                        widget_info["configuring"] = ImGui.toggle_button(IconsFontAwesome5.ICON_COG + "##Configure" + widget_name, widget_info["configuring"])

                    PyImGui.end_table()
        PyImGui.end()

        if enable_all:
            handler.execute_enabled_widgets()
            handler.execute_configuring_widgets()


    # Handle specific exceptions to provide detailed error messages
    except ImportError as e:
        Py4GW.Console.Log(module_name, f"ImportError encountered: {str(e)}", Py4GW.Console.MessageType.Error)
        Py4GW.Console.Log(module_name, f"Stack trace: {traceback.format_exc()}", Py4GW.Console.MessageType.Error)
    except ValueError as e:
        Py4GW.Console.Log(module_name, f"ValueError encountered: {str(e)}", Py4GW.Console.MessageType.Error)
        Py4GW.Console.Log(module_name, f"Stack trace: {traceback.format_exc()}", Py4GW.Console.MessageType.Error)
    except TypeError as e:
        Py4GW.Console.Log(module_name, f"TypeError encountered: {str(e)}", Py4GW.Console.MessageType.Error)
        Py4GW.Console.Log(module_name, f"Stack trace: {traceback.format_exc()}", Py4GW.Console.MessageType.Error)
    except Exception as e:
        # Catch-all for any other unexpected exceptions
        Py4GW.Console.Log(module_name, f"Unexpected error encountered: {str(e)}", Py4GW.Console.MessageType.Error)
        Py4GW.Console.Log(module_name, f"Stack trace: {traceback.format_exc()}", Py4GW.Console.MessageType.Error)
    finally:
        # Optional: Code that will run whether an exception occurred or not
        #Py4GW.Console.Log(module_name, "Execution of Main() completed", Py4GW.Console.MessageType.Info)
        # Place any cleanup tasks here
        pass

# This ensures that Main() is called when the script is executed directly.
if __name__ == "__main__":
    main()
