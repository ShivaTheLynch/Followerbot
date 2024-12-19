from Py4GWCoreLib import *
module_name = "Hello Widget"

# Configuration class for the widget
class config:
    def __init__(self):
        self.message = "Hello"

widget_config = config()
window_module = ImGui.WindowModule(module_name, window_name="Hello Widget", window_size=(200, 100), window_flags=PyImGui.WindowFlags.AlwaysAutoResize)

def configure():
    """Configuration function to adjust widget settings."""
    global widget_config
    if PyImGui.begin("Hello Widget Configuration"):
        widget_config.message = PyImGui.input_text("Message", widget_config.message)
    PyImGui.end()

def DrawWindow():
    """Function to draw the widget window with the message."""
    global widget_config, window_module

    if PyImGui.begin(window_module.window_name, window_module.window_flags):
        PyImGui.text(widget_config.message)
    PyImGui.end()

def main():
    """Main function to check conditions and display the widget."""
    if Map.IsMapReady() and Party.IsPartyLoaded():
        DrawWindow()

if __name__ == "__main__":
    main() 