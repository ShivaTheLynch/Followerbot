from Extendedcorelib import *


module_name = "FarmingBot"
outpost_coordinate_list = [
( -4268, 11628),
( -5490, 13672)
]

map_paths = { 
    200: [
        (-8394, -9801),
        (-13046, -9347),
        (-17348, -9895),
        (-17929, -10300),
        (-14702, -6671),
        (-11080, -6126),
        (-13426, -2344),
        (-15055, -3226),
        (-9448, -283),
        (-9918, 2826),
        (-8721, 7682),
        (-3749, 8053),
        (-7474, -1144),
        (-9666, 2625),
        (-5895, -3959),
        (-3509, -8000),
        (-195, -9095),
        (6298, -8707),
        (3981, -3295),
        (496, -2581),
        (2069, 1127),
        (5859, 1599),
        (6412, 6572),
        (10507, 8140),
        (14403, 6938),
        (18080, 3127),
        (13518, -35),
        (13450, -6084),
        (13764, -4816),
        (13450, -6084),
        (15390, -8892),
        (13764, -4816)
    ]
}
FARM_MODEL_IDS = [] 
OUTPOST_ID = 389
FARM_END_ID = 200

skill_config = {
    8: {
        "type": "enchantment",
        "condition": lambda: not Combat.HasBuff(Player.GetAgentID(), 8) and Combat.IsSkillReady(8) and Combat.HasEnoughEnergy(8),
        "action": lambda: Combat.CastSkill(8),
        "aftercast": Combat.GetAftercast(8) + 50
    },
    1: {
        "type": "damage",
        "condition": lambda: Combat.IsSkillReady(1) and Combat.HasEnoughEnergy(1),
        "action": lambda: Combat.CastSkill(1),
        "aftercast": Combat.GetAftercast(1) + 50
    },
    7: {
        "type": "damage",
        "condition": lambda: Combat.HasBuff(Player.GetAgentID(), 1) and Combat.IsSkillReady(7) and Combat.HasEnoughEnergy(7),
        "action": lambda: Combat.CastSkill(7),
        "aftercast": Combat.GetAftercast(7) + 50
    },
    2: {
        "type": "damage",
        "condition": lambda: Combat.HasBuff(Player.GetAgentID(), 1) and Combat.IsSkillReady(2) and Combat.HasEnoughEnergy(2),
        "action": lambda: Combat.CastSkill(2),
        "aftercast": Combat.GetAftercast(2) + 50
    },
    3: {
        "type": "damage",
        "condition": lambda: Combat.HasBuff(Player.GetAgentID(), 1) and Combat.IsSkillReady(3) and Combat.HasEnoughAdrenaline(3),
        "action": lambda: Combat.CastSkill(3),
        "aftercast": Combat.GetAftercast(3) + 50
    },
    4: {
        "type": "damage",
        "condition": lambda: Combat.HasBuff(Player.GetAgentID(), 1) and Combat.IsSkillReady(4) and Combat.HasEnoughAdrenaline(4),
        "action": lambda: Combat.CastSkill(4),
        "aftercast": Combat.GetAftercast(4) + 50
    },
    5: {
        "type": "damage",
        "condition": lambda: Combat.HasBuff(Player.GetAgentID(), 1) and Combat.IsSkillReady(5) and Combat.HasEnoughEnergy(5),
        "action": lambda: Combat.CastSkill(5),
        "aftercast": Combat.GetAftercast(5) + 50
    },
    6: {
        "type": "damage",
        "condition": lambda: Combat.HasBuff(Player.GetAgentID(), 1) and Combat.IsSkillReady(6) and Combat.HasEnoughAdrenaline(6),
        "action": lambda: Combat.CastSkill(6),
        "aftercast": Combat.GetAftercast(6) + 50
    }
}


class BotVars:
    def __init__(self, starting_outpost_id=0, farm_end_id=0):
        self.starting_map = starting_outpost_id
        self.farm_end_id = farm_end_id
        self.bot_started = False
        self.window_module = None
        self.variables = {}
        self.has_env_reset = False

        # Simple Farm Configurations
        self.resign_to_farm = True
        self.pick_up_chests = True
        self.load_skillbar = False

        
        # Simple Farm Tracking Metrics
        self.farm_timer = Py4GW.Timer()
        self.farm_count = 0
        self.chests_found = 0
        self.deaths = 0
        

bot_vars = BotVars(starting_outpost_id=OUTPOST_ID, farm_end_id=FARM_END_ID)
bot_vars.window_module = ImGui.WindowModule(module_name, window_name="Simple Farming", window_size=(300, 350))

class StateMachineVars:
        def __init__(self):
            # FSMs
            self.state_machine = FSM("Main")
            self.path_to_farm_machine = FSM("PathToFarm")
            self.farm_machine = FSM("Farm")
            self.loot_items = FSM("Loot")
            self.loot_chest = FSM("Chest")
            self.fight_enemies = FSM("Fight")

            # Movement
            self.outpost_pathing = Routines.Movement.PathHandler(outpost_coordinate_list)
            self.current_map_pathing = Routines.Movement.PathHandler([])
            self.chest_found_pathing = None
            self.current_map_id = 0
            self.movement_handler = Routines.Movement.FollowXY()

            # Other tools and variables
            self.ping_handler = Py4GW.PingHandler()
            self.timer = Py4GW.Timer()
            self.timer_check = 0
            self.has_resigned = False
            self.map_loaded = False
            self.explorable_loading = False
            self.finished_resigning = False
            self.collected_coords = []
            self.current_target = None
            self.current_loot_target = None
            self.current_chest_target = 0
            self.completed_chests = []
            self.bounty_npc = Routines.Movement.PathHandler([(-8394, -9801)])  # Add Bounty NPC path
            self.has_bounty = False  # Add tracking for bounty status

FSM_vars = StateMachineVars()

#Helper Functions
def StartBot():
    global bot_vars

    if not bot_vars.has_env_reset:
        ResetEnvironment()
        bot_vars.has_env_reset = True
        bot_vars.farm_timer.reset()

    bot_vars.bot_started = True

def StopBot():
    global bot_vars
    bot_vars.farm_timer.stop()
    bot_vars.bot_started = False

def IsBotStarted():
    global bot_vars
    return bot_vars.bot_started

def IfActionIsPending():
    global FSM_vars
    if FSM_vars.timer_check != 0 and FSM_vars.timer.get_elapsed_time() > 0:
        if FSM_vars.timer.has_elapsed(FSM_vars.timer_check):
            FSM_vars.timer_check = 0
            FSM_vars.timer.stop()
            return False
    if FSM_vars.timer_check == 0 and FSM_vars.timer.get_elapsed_time() == 0:
        return False
    return True

def SetPendingAction(timer_check=1000):
    global FSM_vars
    FSM_vars.timer_check = timer_check
    FSM_vars.timer.reset()

def DoesNeedInventoryHandling():
    return ( Inventory.GetFreeSlotCount() < 1 or Inventory.GetModelCount(22751) < 1)

def CheckMapLocation():
    global bot_vars, FSM_vars
    if IfActionIsPending():
        return

    if Routines.Transition.IsExplorableLoaded():
        if Map.GetMapID() not in map_paths:
            Routines.Transition.TravelToOutpost(bot_vars.starting_map) # travel to starting outpost if not in one of the zones
            SetPendingAction(2000)
            return
        
        Py4GW.Console.Log(bot_vars.window_module.module_name, f"{Map.GetMapName(Map.GetMapID())} ({Map.GetMapID()}) already loaded. Switching to Farm step.", Py4GW.Console.MessageType.Info)
        FSM_vars.current_map_id = 0
        FSM_vars.current_map_pathing = Routines.Movement.PathHandler([])
        FSM_vars.state_machine.jump_to_state_by_name("Start Pathing for Farm")
        return
        
    if Routines.Transition.IsOutpostLoaded():
        Py4GW.Console.Log(bot_vars.window_module.module_name, f"Outpost loaded", Py4GW.Console.MessageType.Info)
        if Map.GetMapID() != bot_vars.starting_map:
            Routines.Transition.TravelToOutpost(bot_vars.starting_map)
            SetPendingAction(3000)
            return
        
        FSM_vars.timer.stop()
        FSM_vars.state_machine.jump_to_state_by_name("Leaving Outpost")
    
    SetPendingAction(int(FSM_vars.ping_handler.GetCurrentPing()) * 2) # to help prevent it from checking too frequently

def LoadSkillBar(): # TODO ould need to set skill templates for the farm
    global bot_vars
    if bot_vars.load_skillbar:
        primary_profession, secondary_profession = Agent.GetProfessionNames(Player.GetAgentID())
    if primary_profession == "Dervish":
            SkillBar.LoadSkillTemplate("OgCikysMtdJd9cFg1cltJG2DCA") # this is what the skill_config is set for

def IsSkillBarLoaded():
    global bot_vars
    if bot_vars.load_skillbar:
        Py4GW.Console.Log(bot_vars.window_module.module_name, f"SkillBar Loaded.", Py4GW.Console.MessageType.Info)       
    return True

def HandleSkills():
    global FSM_vars
    if not Routines.Transition.IsExplorableLoaded():
        return
    
    if IfActionIsPending():
        return

    if not Agent.IsAlive(Player.GetAgentID()):
        return
    
    if Agent.IsCasting(Player.GetAgentID()):
        return

    if Agent.IsKnockedDown(Player.GetAgentID()):
        return

    for i in [1, 2, 3]:
        if Agent.GetEnergy(Player.GetAgentID()) * Agent.GetMaxEnergy(Player.GetAgentID()) >= Skill.Data.GetEnergyCost(SkillBar.GetSkillIDBySlot(i)) and SkillBar.GetSkillData(i).recharge == 0:
            delay = int(Skill.Data.GetActivation(SkillBar.GetSkillIDBySlot(i))) * 1000
            delay += int(Skill.Data.GetAftercast(SkillBar.GetSkillIDBySlot(i))) * 1000
            delay += int(FSM_vars.ping_handler.GetCurrentPing()) * 2
            SetPendingAction(delay)
            SkillBar.UseSkill(i)
            return

def Resign():
    global FSM_vars, bot_vars
    if IfActionIsPending():
        return

    if bot_vars.resign_to_farm == True and FSM_vars.has_resigned == False:
        Player.SendChatCommand("resign") # only resign once
        FSM_vars.has_resigned = True
        bot_vars.farm_count += 1
        SetPendingAction(2000)
    
    if Routines.Transition.IsOutpostLoaded() or Map.IsMapLoading():
        FSM_vars.state_machine.jump_to_state_by_name("Finished")
    
    SetPendingAction(1000) # make sure to wait before spamming IsLoaded

def UpdateTarget(max_distance=2500):
    if IfActionIsPending():
        return
    
    if not Agent.IsAlive(Player.GetAgentID()): # if not alive
        return
    
    # reset target once its dead

    if FSM_vars.current_target != None and Agent.IsDead(FSM_vars.current_target):
        FSM_vars.current_target = None
        return

    # only look for target if we don't have one
    if FSM_vars.current_target == None:
        enemy_array = AgentArray.GetEnemyArray()
        xy = Player.GetXY()
        filtered_enemy_array = Utils.Filters.FilterAgentArrayByAlive(xy, enemy_array, area=2500)
        filtered_enemy_array = AgentArray.Sort.ByDistance(filtered_enemy_array, xy)
        nearby_enemies = [
            agent for agent in filtered_enemy_array 
            if Utils.Distance(xy, Agent.GetXY(agent)) <= max_distance
        ]
        
        for agent in nearby_enemies:
            try:
                # player_number = Agent.GetPlayerNumber(agent) # if you need to check the model id of the enemy to only farm specific enemies

                FSM_vars.current_target = agent
                Py4GW.Console.Log(bot_vars.window_module.module_name, f"Target Farm found! {agent}", Py4GW.Console.MessageType.Info)
                return agent  # Return the target enemy if found
            except Exception as e:
                # Log any errors that occur during the player number retrieval
                Py4GW.Console.Log(bot_vars.window_module.module_name, f"Error retrieving player number: {str(e)}", Py4GW.Console.MessageType.Error)

    return None  # No valid target found


def EnemyFound():
    global FSM_vars
    UpdateTarget(max_distance=1150)
    return FSM_vars.current_target != None

def ChangeTargeting():
    global FSM_vars
    Player.ChangeTarget(FSM_vars.current_target)

def ResetPathing(pathing):
    global FSM_vars
    if not Routines.Movement.IsFollowPathFinished(pathing, FSM_vars.movement_handler):
        pathing.reset()
    else:
        FSM_vars.farm_machine.jump_to_state_by_name("Finished")

def UpdateLootTarget(max_distance=1250):
    global FSM_vars
    if IfActionIsPending():
        return

    # Reset loot target once it's no longer valid or has been picked up
    if FSM_vars.current_loot_target is not None and not Agent.IsItem(FSM_vars.current_loot_target):
        FSM_vars.current_loot_target = None
        return

    # Only look for a new loot target if we don't have one
    if FSM_vars.current_loot_target is None:
        # Retrieve all items within the area
        item_array = AgentArray.GetItemArray()
        xy = Player.GetXY()
        filtered_item_array = AgentArray.Sort.ByDistance(item_array, xy)
        
        # Filter items within the maximum distance
        nearby_items = [
            item for item in filtered_item_array
            if Utils.Distance(xy, Agent.GetXY(item)) <= max_distance
        ]
        
        # Set the current loot target to the nearest valid item
        for item in nearby_items:
            FSM_vars.current_loot_target = item
            Py4GW.Console.Log(bot_vars.window_module.module_name, f"Loot Item found! {item}", Py4GW.Console.MessageType.Info)
            return item  # Return the loot item if found

    return None  # No valid loot item found

def LootFound():
    UpdateLootTarget(max_distance=1250)
    return FSM_vars.current_loot_target is not None

def IsChestFound(max_distance=2500):
    return Routines.Targeting.GetNearestChest(max_distance) != 0

def ResetFollowPathToChest():
    global FSM_vars
    FSM_vars.movement_handler.reset()
    ResetPathing(FSM_vars.current_map_pathing)
    if FSM_vars.current_chest_target != 0:
        chest_x, chest_y = Agent.GetXY(FSM_vars.current_chest_target)
        found_chest_coord_list = [(chest_x, chest_y)]
    
    if found_chest_coord_list != None:
        FSM_vars.chest_found_pathing = Routines.Movement.PathHandler(found_chest_coord_list)
        FSM_vars.loot_chest.jump_to_state_by_name("MoveToChest")
    else:
        FSM_vars.loot_chest.jump_to_state_by_name("Finished")

def CheckForChest():   
    global FSM_vars, bot_vars
    if bot_vars.pick_up_chests != False and FSM_vars.current_chest_target != 0 and FSM_vars.current_chest_target not in FSM_vars.completed_chests:
        Py4GW.Console.Log(bot_vars.window_module.module_name, f"Chest {FSM_vars.current_chest_target} found and not in completed_chests {FSM_vars.completed_chests}", Py4GW.Console.MessageType.Info)
        FSM_vars.loot_chest.jump_to_state_by_name("Reset Follow Path To Chest")
    else:
        FSM_vars.loot_chest.jump_to_state_by_name("Finished")

def ChestFound(max_distance=1250):
    global FSM_vars
    if IfActionIsPending():
        return False
    
    chest = Routines.Targeting.GetNearestChest(max_distance)
    if chest != 0 and chest not in FSM_vars.completed_chests:
        Py4GW.Console.Log(bot_vars.window_module.module_name, f"Chest {chest} found!", Py4GW.Console.MessageType.Info)
        FSM_vars.current_chest_target = chest
        return True
    
    FSM_vars.current_chest_target = 0
    return False

def TrackChest():
    global FSM_vars, bot_vars
    
    if FSM_vars.current_chest_target != 0:
        FSM_vars.completed_chests.append(FSM_vars.current_chest_target)
        FSM_vars.current_chest_target = 0
        bot_vars.chests_found += 1

    return True

def PlayerDied():
    global bot_vars
    if not Agent.IsAlive(Player.GetAgentID()):
        FSM_vars.current_target = None # reset target so that it can restart the sub machine
        bot_vars.deaths += 1
        return True
    return False

def CheckForMap():
    global FSM_vars
    if IfActionIsPending():
        return False
    
    current_map = Map.GetMapID()
    if Routines.Transition.IsExplorableLoaded():
        if current_map in map_paths:
            Py4GW.Console.Log(bot_vars.window_module.module_name, f"Setting current map and path to {current_map}", Py4GW.Console.MessageType.Info)
            FSM_vars.current_map_pathing = Routines.Movement.PathHandler(map_paths[current_map])
            FSM_vars.current_map_id = current_map
            return
    
    # not sure if I need to handle the case where this map path doesn't get loaded correctly
    Py4GW.Console.Log(bot_vars.window_module.module_name, f"CheckForMap() when Explorable not loaded.", Py4GW.Console.MessageType.Info)
    SetPendingAction(2000)

def IsCurrentPathFinished():
    # Py4GW.Console.Log(bot_vars.window_module.module_name, f"IsCurrentPathFinished: {(Routines.Movement.IsFollowPathFinished(FSM_vars.current_map_pathing, FSM_vars.movement_handler) and not EnemyFound())}", Py4GW.Console.MessageType.Info)
    return (Routines.Movement.IsFollowPathFinished(FSM_vars.current_map_pathing, FSM_vars.movement_handler) and not EnemyFound())

def format_elapsed_time(milliseconds):
    """
    Converts elapsed time in milliseconds to a human-readable format.
    Displays seconds if under 60 seconds, otherwise displays minutes and seconds.
    """
    total_seconds = milliseconds / 1000
    if total_seconds < 60:
        return f"{total_seconds:.2f} seconds"
    else:
        minutes = int(total_seconds // 60)
        seconds = total_seconds % 60
        return f"{minutes}m {seconds:.2f}s"
    
def WaitForLoot():
    if IfActionIsPending():
        return False
    
    if not LootFound():
        return True
    else:
        SetPendingAction(2000)
        return True
    
def ExecuteSkills():
    global FSM_vars
    if IfActionIsPending():
        return False
    
    for skill_slot, skill_data in skill_config.items():
        if skill_data["condition"]():
            if skill_data["type"] != "damage" or skill_data["type"] == "damage" and FSM_vars.current_target != None:
                print(f"Casting skill in slot {skill_slot}")
                skill_data["action"]()
                SetPendingAction(skill_data["aftercast"])
                return  # Exit after casting a skill to avoid overlapping casts

def Take_Bounty():
    global FSM_vars
    try:
        Player.SendDialog(int("0x85", 16))  # First dialog
        SetPendingAction(1000)  # 1000ms delay
        Player.SendDialog(int("0x86", 16))  # Second dialog
        SetPendingAction(500)   # 500ms delay
        
        current_map_id = Map.GetMapID()
        Py4GW.Console.Log(bot_vars.window_module.module_name, f"Current Map ID: {current_map_id}", Py4GW.Console.MessageType.Info)
        
        if current_map_id in map_paths:
            FSM_vars.has_bounty = True
            FSM_vars.has_resigned = False
            FSM_vars.finished_resigning = False
            FSM_vars.movement_handler.reset()
            
            FSM_vars.current_map_id = current_map_id
            FSM_vars.current_map_pathing = Routines.Movement.PathHandler(map_paths[current_map_id])
            
            FSM_vars.farm_machine.reset()
            FSM_vars.path_to_farm_machine.reset()
            
            return True
            
        else:
            Py4GW.Console.Log(bot_vars.window_module.module_name, f"No path found for map {current_map_id}", Py4GW.Console.MessageType.Error)
            return False
            
    except Exception as e:
        Py4GW.Console.Log(bot_vars.window_module.module_name, f"Error in Take_Bounty: {str(e)}", Py4GW.Console.MessageType.Error)
        return False

def ResetEnvironment():
    global FSM_vars
    FSM_vars.outpost_pathing.reset()
    FSM_vars.movement_handler.reset()
    FSM_vars.state_machine.reset()
    FSM_vars.path_to_farm_machine.reset()
    FSM_vars.loot_items.reset()
    FSM_vars.farm_machine.reset()
    FSM_vars.fight_enemies.reset()
    FSM_vars.timer.stop()
    FSM_vars.timer_check = 0
    FSM_vars.finished_resigning = False
    FSM_vars.has_resigned = False
    FSM_vars.map_loaded = False
    FSM_vars.explorable_loading = False
    FSM_vars.state_machine.log_actions = False
    FSM_vars.current_map_pathing = Routines.Movement.PathHandler([])
    FSM_vars.current_target = None
    FSM_vars.current_loot_target = None
    FSM_vars.current_chest_target = 0
    FSM_vars.completed_chests = []
    FSM_vars.has_bounty = False  # Add reset for bounty status

def main():
    global bot_vars,FSM_vars
    try:
        DrawWindow()

        if IsBotStarted():
            if FSM_vars.state_machine.is_finished():
                ResetEnvironment()
            else:
                FSM_vars.state_machine.update()

    except ImportError as e:
        Py4GW.Console.Log(bot_vars.window_module.module_name, f"ImportError encountered: {str(e)}", Py4GW.Console.MessageType.Error)
        Py4GW.Console.Log(bot_vars.window_module.module_name, f"Stack trace: {traceback.format_exc()}", Py4GW.Console.MessageType.Error)
    except ValueError as e:
        Py4GW.Console.Log(bot_vars.window_module.module_name, f"ValueError encountered: {str(e)}", Py4GW.Console.MessageType.Error)
        Py4GW.Console.Log(bot_vars.window_module.module_name, f"Stack trace: {traceback.format_exc()}", Py4GW.Console.MessageType.Error)
    except TypeError as e:
        Py4GW.Console.Log(bot_vars.window_module.module_name, f"TypeError encountered: {str(e)}", Py4GW.Console.MessageType.Error)
        Py4GW.Console.Log(bot_vars.window_module.module_name, f"Stack trace: {traceback.format_exc()}", Py4GW.Console.MessageType.Error)
    except Exception as e:
        Py4GW.Console.Log(bot_vars.window_module.module_name, f"Unexpected error encountered: {str(e)}", Py4GW.Console.MessageType.Error)
        Py4GW.Console.Log(bot_vars.window_module.module_name, f"Stack trace: {traceback.format_exc()}", Py4GW.Console.MessageType.Error)
    finally:
        pass

if __name__ == "__main__":
    main()
