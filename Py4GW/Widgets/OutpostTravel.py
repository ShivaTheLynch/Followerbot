from Py4GWCoreLib import *
import time
module_name = "Outpost Travel"

# List of outposts with IDs organized by campaign
outposts = {
    # Global/Special
    "[Global] Embark Beach": 857,
    "[Global] Great Temple of Balthazar": 248,
    
    # Pre-Searing
    "[Pre] Ascalon City": 148,
    "[Pre] Ashford Abbey": 164,
    "[Pre] Foible's Fair": 165,
    "[Pre] Fort Ranik": 166,
    "[Pre] The Barradin Estate": 163,
    
    # Prophecies
    "[Proph] Ascalon City": 81,
    "[Proph] Ruins of Surmia": 30,
    "[Proph] Fort Ranik": 29,
    "[Proph] Frontier Gate": 135,
    "[Proph] Grendich Courthouse": 36,
    "[Proph] Piken Square": 40,
    "[Proph] Lion's Arch": 55,
    "[Proph] Bergen Hot Springs": 57,
    "[Proph] Beetletun": 136,
    "[Proph] Temple of the Ages": 138,
    "[Proph] Fishermen's Haven": 137,
    "[Proph] Ventari's Refuge": 139,
    "[Proph] Druids Overlook": 140,
    "[Proph] Quarrel Falls": 142,
    "[Proph] The Wilds": 11,
    "[Proph] Aurora Glade": 12,
    "[Proph] Maguuma Stade": 141,
    "[Proph] Henge of Denravi": 49,
    "[Proph] Kryta Province": 58,
    "[Proph] Gates of Kryta": 14,
    "[Proph] D'Alessio Seaboard": 15,
    "[Proph] Sanctum Cay": 19,
    "[Proph] Droknar's Forge": 20,
    "[Proph] Camp Rankor": 155,
    "[Proph] Ice Tooth Cave": 132,
    "[Proph] Beacon's Perch": 133,
    "[Proph] Yak's Bend": 134,
    "[Proph] Borlis Pass": 25,
    "[Proph] The Granite Citadel": 156,
    "[Proph] Marhan's Grotto": 157,
    "[Proph] Port Sledge": 158,
    
    # Factions
    "[Fact] Kaineng Center": 194,
    "[Fact] Shing Jea Monastery": 242,
    "[Fact] Seitung Harbor": 250,
    "[Fact] Tsumei Village": 249,
    "[Fact] Ran Musu Gardens": 251,
    "[Fact] Maatu Keep": 283,
    "[Fact] Zin Ku Corridor": 284,
    "[Fact] Senji's Corner": 51,
    "[Fact] Vizunah Square": 291,
    "[Fact] Dragon's Throat": 274,
    "[Fact] Nahpui Quarter": 260,
    "[Fact] Tahnnakai Temple": 261,
    "[Fact] Arborstone": 262,
    "[Fact] Boreas Seabed": 263,
    "[Fact] Sunjiang District": 264,
    "[Fact] Raisu Palace": 233,
    "[Fact] Imperial Sanctum": 327,
    "[Fact] Marketplace": 303,
    "[Fact] Bejunkan Pier": 290,
    "[Fact] Cavalon": 193,
    "[Fact] House zu Heltzer": 77,
    "[Fact] Jade Flats (Kurzick)": 390,
    "[Fact] Jade Flats (Luxon)": 391,
    "[Fact] Aspenwood Gate (Kurzick)": 388,
    "[Fact] Aspenwood Gate (Luxon)": 389,
    
    # Nightfall
    "[NF] Kamadan, Jewel of Istan": 370,
    "[NF] Champion's Dawn": 479,
    "[NF] Kodlonu Hamlet": 490,
    "[NF] Beknur Harbor": 487,
    "[NF] Consulate": 429,
    "[NF] Sunspear Great Hall": 431,
    "[NF] Mihanu Township": 396,
    "[NF] Blacktide Den": 492,
    "[NF] Kodash Bazaar": 414,
    "[NF] Dzagonur Bastion": 433,
    "[NF] Chantry of Secrets": 393,
    "[NF] Gate of Desolation": 478,
    "[NF] Gate of Pain": 494,
    "[NF] Gate of Madness": 495,
    "[NF] Gate of Torment": 450,
    "[NF] Gate of Anguish": 451,
    
    # Eye of the North
    "[EOTN] Eye of the North": 642,
    "[EOTN] Gunnar's Hold": 644,
    "[EOTN] Sifhalla": 643,
    "[EOTN] Olafstead": 645,
    "[EOTN] Rata Sum": 640,
    "[EOTN] Central Transfer Chamber": 652,
    "[EOTN] Gadd's Encampment": 638,
    "[EOTN] Tarnished Haven": 641,
    "[EOTN] Umbral Grotto": 639,
    
    # Challenge Missions & Elite Areas
    "[Elite] Urgoz's Warren": 266,
    "[Elite] The Deep": 307
}

class config:
    def __init__(self):
        self.outpost_id = 389
        self.selected_outpost_index = 0
        self.is_hard_mode = False

widget_config = config()
window_module = ImGui.WindowModule(
    module_name, 
    window_name="Outpost Travel", 
    window_size=(300, 200),
    window_flags=PyImGui.WindowFlags.AlwaysAutoResize
)

def configure():
    """Required configuration function for the widget"""
    global widget_config
    try:
        if PyImGui.begin("Outpost Travel Configuration"):
            # Add any configuration options here if needed
            PyImGui.end()
    except Exception as e:
        Py4GW.Console.Log(module_name, f"Error in configure: {str(e)}", Py4GW.Console.MessageType.Debug)

def travel_to_outpost(outpost_id, hard_mode=False):
    try:
        if not Map.IsMapReady():
            Py4GW.Console.Log(module_name, "Map not ready for travel", Py4GW.Console.MessageType.Debug)
            return False
            
        if not Party.IsPartyLoaded():
            Py4GW.Console.Log(module_name, "Party not loaded", Py4GW.Console.MessageType.Debug)
            return False

        # Check if outpost is unlocked (if such an API exists)
        # if not Map.IsOutpostUnlocked(outpost_id):
        #     Py4GW.Console.Log(module_name, "Outpost not unlocked", Py4GW.Console.MessageType.Debug)
        #     return False

        current_map = Map.GetMapID()
        Py4GW.Console.Log(module_name, f"Current map ID: {current_map}", Py4GW.Console.MessageType.Debug)
        
        if current_map == outpost_id:
            Py4GW.Console.Log(module_name, "Already in target outpost", Py4GW.Console.MessageType.Debug)
            return True

        time.sleep(0.5)
        
        Py4GW.Console.Log(module_name, f"Attempting to travel to outpost {outpost_id}", Py4GW.Console.MessageType.Debug)
        if not Map.Travel(outpost_id):
            Py4GW.Console.Log(module_name, "Failed to initiate travel - outpost may be locked or unavailable", Py4GW.Console.MessageType.Debug)
            return False
            
        start_time = time.time()
        while time.time() - start_time < 30:
            if Map.IsMapReady():
                new_map_id = Map.GetMapID()
                Py4GW.Console.Log(module_name, f"New map ID: {new_map_id}", Py4GW.Console.MessageType.Debug)
                if new_map_id == outpost_id:
                    time.sleep(1)
                    Py4GW.Console.Log(module_name, "Successfully arrived at destination", Py4GW.Console.MessageType.Debug)
                    return True
            time.sleep(0.1)
            
        Py4GW.Console.Log(module_name, "Travel timeout - failed to arrive at destination", Py4GW.Console.MessageType.Debug)
        return False
        
    except Exception as e:
        Py4GW.Console.Log(module_name, f"Error during travel: {str(e)}", Py4GW.Console.MessageType.Debug)
        return False

is_traveling = False

def DrawWindow():
    global is_traveling, widget_config
    
    if PyImGui.begin(window_module.window_name, window_module.window_flags):
        try:
            # Title and instructions
            PyImGui.text("Select an outpost and click Travel to move.")
            PyImGui.separator()

            # Outpost selection dropdown
            outpost_names = list(outposts.keys())
            new_index = PyImGui.combo("Outposts", widget_config.selected_outpost_index, outpost_names)
            if new_index != widget_config.selected_outpost_index:
                widget_config.selected_outpost_index = new_index
                selected_outpost_name = outpost_names[widget_config.selected_outpost_index]
                widget_config.outpost_id = outposts[selected_outpost_name]

            # Display selected outpost details
            selected_outpost_name = outpost_names[widget_config.selected_outpost_index]
            PyImGui.text(f"Selected: {selected_outpost_name} (ID: {outposts[selected_outpost_name]})")

            # Hard mode toggle
            widget_config.is_hard_mode = PyImGui.checkbox("Hard Mode", widget_config.is_hard_mode)

            # Display map readiness status
            map_ready_status = "Yes" if Map.IsMapReady() else "No"
            PyImGui.text(f"Map Ready: {map_ready_status}")
            PyImGui.separator()

            if PyImGui.button("Travel") and not is_traveling:
                try:
                    is_traveling = True
                    selected_outpost_name = outpost_names[widget_config.selected_outpost_index]
                    Py4GW.Console.Log(module_name, f"Starting travel to {selected_outpost_name}", Py4GW.Console.MessageType.Debug)
                    success = travel_to_outpost(widget_config.outpost_id, widget_config.is_hard_mode)
                    if not success:
                        Py4GW.Console.Log(module_name, "Travel failed", Py4GW.Console.MessageType.Debug)
                finally:
                    is_traveling = False
                    Py4GW.Console.Log(module_name, "Travel attempt completed", Py4GW.Console.MessageType.Debug)
                    
        except Exception as e:
            is_traveling = False
            Py4GW.Console.Log(module_name, f"Error in DrawWindow: {str(e)}", Py4GW.Console.MessageType.Debug)
            
        PyImGui.end()

def main():
    """Required main function for the widget"""
    try:
        if Map.IsMapReady() and Party.IsPartyLoaded():
            DrawWindow()
    except Exception as e:
        Py4GW.Console.Log(module_name, f"Error in main: {str(e)}", Py4GW.Console.MessageType.Debug)
        return False
    return True

# These functions need to be available at module level
__all__ = ['main', 'configure']

if __name__ == "__main__":
    main()