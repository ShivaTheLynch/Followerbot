from Py4GWCoreLib import *
module_name = "Return to Outpost"


class config:
    def __init__(self):
        self.returned = False

widget_config = config()
config_module = ImGui.WindowModule(f"Config {module_name}", window_name="Return to Outpost##Return to Outpost", window_size=(100, 100), window_flags=PyImGui.WindowFlags.AlwaysAutoResize)


def configure():
    global config_module

    if PyImGui.begin(config_module.window_name, config_module.window_flags):
        ImGui.text("Return to outpost when paty is defeated")
    PyImGui.end()

def main():
    global widget_config
    if Map.IsMapReady() and Party.IsPartyLoaded() and Party.IsPartyDefeated() and widget_config.returned == False:
        Party.ReturnToOutpost()
        widget_config.returned = True
    else:
        widget_config.returned = False
        

if __name__ == "__main__":
    main()

