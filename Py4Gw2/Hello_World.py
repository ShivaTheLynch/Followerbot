from Py4GWCoreLib import *
checkbox_state = True
def DrawWindow():
    global checkbox_state

    if PyImGui.begin("Hello World!"):
        PyImGui.text(f"This is how you show text")
        if PyImGui.button(IconsFontAwesome5.ICON_COG + "##write to console"):
            Py4GW.Console.Log("Hello World script", f"I salute you.", Py4GW.Console.MessageType.Info)
    PyImGui.end()


def main():
        DrawWindow()

if __name__ == "__main__":
    main()

