from Py4GWCoreLib import *
module_name = "Vanquish Monitor"


class config:
    def __init__(self):
        self.x = 100
        self.y = 200
        self.scale = 4.0
        self.color=(1.0, 1.0, 1.0, 1.0)
        self.string = "000/000"

widget_config = config()
window_module = ImGui.WindowModule(module_name, window_name="Vanquish Monitor", window_size=(100, 100), window_flags=PyImGui.WindowFlags.AlwaysAutoResize | PyImGui.WindowFlags.NoBackground | PyImGui.WindowFlags.NoTitleBar | PyImGui.WindowFlags.NoCollapse)
config_module = ImGui.WindowModule(f"Config {module_name}", window_name="Vanquish Monitor##Vanquish Monitor", window_size=(100, 100), window_flags=PyImGui.WindowFlags.AlwaysAutoResize)

overlay = Overlay()

def DrawWindow():
    global widget_config, overlay,window_module

    killed = Map.GetFoesKilled()
    total = Map.GetFoesToKill()

    widget_config.string = f"{killed:03}/{total:03}"

    PyImGui.set_next_window_pos(widget_config.x, widget_config.y)

    if PyImGui.begin(window_module.window_name, window_module.window_flags):
        PyImGui.text_scaled(widget_config.string,widget_config.color,widget_config.scale)
    PyImGui.end()

def configure():
    global widget_config,config_module

    if PyImGui.begin(config_module.window_name, config_module.window_flags):
        overlay = Overlay()
        screen_width, screen_height = overlay.GetDisplaySize().x, overlay.GetDisplaySize().y
        widget_config.x = PyImGui.slider_int("X", widget_config.x, 0, screen_width)
        widget_config.y = PyImGui.slider_int("Y", widget_config.y, 0, screen_height)
        widget_config.scale = PyImGui.slider_float("Scale", widget_config.scale, 1.0, 10.0)
        widget_config.color = PyImGui.color_edit4("Color", widget_config.color)
    PyImGui.end()

def main():
    if (
         Map.IsMapReady() and 
         Party.IsPartyLoaded() and 
         Map.IsExplorable() and 
         Map.IsVanquishable() and 
         Party.IsHardMode()
    ):
        DrawWindow()

if __name__ == "__main__":
    main()

