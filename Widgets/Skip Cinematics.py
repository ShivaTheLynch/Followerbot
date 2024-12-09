from Py4GWCoreLib import *
module_name = "Skip Cinematic"


class config:
    def __init__(self):
        self.skipped = False

widget_config = config()
config_module = ImGui.WindowModule(f"Config {module_name}", window_name="Skip Cinematic##Skip Cinematic", window_size=(100, 100), window_flags=PyImGui.WindowFlags.AlwaysAutoResize)


def configure():
    global config_module

    if PyImGui.begin(config_module.module_name, config_module.window_flags):
        ImGui.text("Skips cinematics")
    PyImGui.end()

def main():
    global widget_config
    if Map.IsMapReady() and Party.IsPartyLoaded() and Map.IsInCinematic() and widget_config.skipped == False:
        Map.SkipCinematic()
        widget_config.skipped = True
    else:
        widget_config.skipped = False
        

if __name__ == "__main__":
    main()

