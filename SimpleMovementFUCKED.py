from Py4GWCoreLib import *
import time

module_name = "SimpleMovement"
OUTPOST_ID = 389  # Your outpost ID
BLESSING_POSITION = (-8394, -9801)

# Coordinates for moving out of outpost
outpost_coordinate_list = [
    (-4268, 11628),
    (-5490, 13672)
]

# Movement path for map 200
map_path = [
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

class BotVars:
    def __init__(self):
        self.bot_started = False
        self.window_module = None
        self.has_env_reset = False

class StateMachineVars:
    def __init__(self):
        # Main state machine
        self.state_machine = FSM("Main")
        
        # Movement handlers
        self.outpost_pathing = Routines.Movement.PathHandler(outpost_coordinate_list)
        self.map_pathing = Routines.Movement.PathHandler(map_path)
        self.blessing_pathing = Routines.Movement.PathHandler([BLESSING_POSITION])
        self.movement_handler = Routines.Movement.FollowXY()
        
        # Other variables
        self.ping_handler = Py4GW.PingHandler()
        self.timer = Py4GW.Timer()
        self.timer_check = 0
        self.last_skill_time = 0
        self.current_skill_index = 1
        self.current_loot_target = None
        self.loot_items = FSM("Loot")

bot_vars = BotVars()
bot_vars.window_module = ImGui.WindowModule(module_name, window_name="Simple Movement", window_size=(300, 200))
FSM_vars = StateMachineVars()

# Helper Functions
def StartBot():
    global bot_vars, FSM_vars
    if not bot_vars.has_env_reset:
        ResetEnvironment()
        
        current_map = Map.GetMapID()
        # If we're in the farm map (200), proceed with finding nearest coordinate
        if current_map == 200:
            try:
                my_id = Player.GetAgentID()
                if my_id:
                    # Find the nearest point in the path with error handling
                    min_distance = float('inf')
                    nearest_index = 0
                    
                    for i, coord in enumerate(map_path):
                        try:
                            distance = ((my_id - coord[0]) ** 2 + (my_id - coord[1]) ** 2) ** 0.5
                            if distance < min_distance:
                                min_distance = distance
                                nearest_index = i
                        except Exception as e:
                            Py4GW.Console.Log("SimpleMovement", f"Error calculating distance for point {i}: {str(e)}", Py4GW.Console.MessageType.Error)
                            continue
                    
                    # Only update if we found a valid point
                    if min_distance != float('inf'):
                        FSM_vars.map_pathing.reset()
                        FSM_vars.map_pathing.current_index = nearest_index
                        Py4GW.Console.Log("SimpleMovement", f"Starting from nearest point: {map_path[nearest_index]}", Py4GW.Console.MessageType.Info)
                        FSM_vars.state_machine.set_state("Follow Map Path")
            except Exception as e:
                Py4GW.Console.Log("SimpleMovement", f"Error finding nearest coordinate: {str(e)}", Py4GW.Console.MessageType.Error)
                FSM_vars.map_pathing.reset()
                FSM_vars.state_machine.reset()
        # If we're not in the outpost (389) or farm map (200), travel to outpost
        elif current_map != OUTPOST_ID:
            Routines.Transition.TravelToOutpost(OUTPOST_ID)
            FSM_vars.state_machine.set_state("Check Map")
        
        bot_vars.has_env_reset = True
    bot_vars.bot_started = True

def StopBot():
    global bot_vars
    bot_vars.bot_started = False

def IsBotStarted():
    global bot_vars
    return bot_vars.bot_started

def IfActionIsPending():
    if FSM_vars.timer_check != 0 and FSM_vars.timer.get_elapsed_time() > 0:
        if FSM_vars.timer.has_elapsed(FSM_vars.timer_check):
            FSM_vars.timer_check = 0
            FSM_vars.timer.stop()
            return False
    if FSM_vars.timer_check == 0 and FSM_vars.timer.get_elapsed_time() == 0:
        return False
    return True

def SetPendingAction(timer_check=1000):
    FSM_vars.timer_check = timer_check
    FSM_vars.timer.reset()

def Take_Bounty():
    if IfActionIsPending():
        return False
    Player.SendDialog(int("0x85", 16))  # First dialog
    SetPendingAction(1000)
    Player.SendDialog(int("0x86", 16))  # Second dialog
    return True

def ResetEnvironment():
    global FSM_vars
    FSM_vars.outpost_pathing.reset()
    FSM_vars.map_pathing.reset()
    FSM_vars.blessing_pathing.reset()
    FSM_vars.movement_handler.reset()
    FSM_vars.state_machine.reset()
    FSM_vars.timer.stop()
    FSM_vars.timer_check = 0
    FSM_vars.current_loot_target = None
    FSM_vars.loot_items.reset()

def GetEnergyAgentCost(skill_id, agent_id):
    """Retrieve the actual energy cost of a skill by its ID and effects.
    [... rest of docstring ...]
    """
    # [... entire function implementation ...]

def get_energy_cost(skill_id):
    player_agent_id = Player.GetAgentID()
    return GetEnergyAgentCost(skill_id, player_agent_id)    

def HasEnoughEnergy(skill_id):
    player_agent_id = Player.GetAgentID()
    energy = Agent.GetEnergy(player_agent_id)
    max_energy = Agent.GetMaxEnergy(player_agent_id)
    energy_points = int(energy * max_energy)
    
    # Add error checking for energy cost
    energy_cost = GetEnergyAgentCost(skill_id, player_agent_id)
    if energy_cost is None:
        return False  # If we can't determine energy cost, assume we don't have enough
    
    return energy_cost <= energy_points

def IsSkillReady(skill_id):
    skill = SkillBar.GetSkillData(SkillBar.GetSlotBySkillID(skill_id))
    recharge = skill.recharge
    return recharge == 0

def IsSkillReady2(skill_slot):
    skill = SkillBar.GetSkillData(skill_slot)
    return skill.recharge == 0

def get_called_target():
    """Get the first called target from party members.
    
    Returns:
        int: Agent ID of the called target, or 0 if no called targets exist
    """
    players = Party.GetPlayers()
    for player in players:
        if player.called_target_id != 0:
            return player.called_target_id
    return 0

# Configure State Machine
FSM_vars.state_machine.AddState(name="Check Map",
    execute_fn=lambda: Routines.Transition.TravelToOutpost(OUTPOST_ID) if Map.GetMapID() != OUTPOST_ID else None,
    exit_condition=lambda: Map.GetMapID() == OUTPOST_ID,
    run_once=False)

FSM_vars.state_machine.AddState(name="Leave Outpost",
    execute_fn=lambda: Routines.Movement.FollowPath(FSM_vars.outpost_pathing, FSM_vars.movement_handler),
    exit_condition=lambda: Routines.Movement.IsFollowPathFinished(FSM_vars.outpost_pathing, FSM_vars.movement_handler),
    run_once=False)

FSM_vars.state_machine.AddState(name="Wait For Map Load",
    exit_condition=lambda: Routines.Transition.IsExplorableLoaded(),
    transition_delay_ms=1500)

FSM_vars.state_machine.AddState(name="Go To Blessing",
    execute_fn=lambda: Routines.Movement.FollowPath(FSM_vars.blessing_pathing, FSM_vars.movement_handler),
    exit_condition=lambda: Routines.Movement.IsFollowPathFinished(FSM_vars.blessing_pathing, FSM_vars.movement_handler),
    run_once=False)

FSM_vars.state_machine.AddState(name="Take Blessing",
    execute_fn=lambda: Player.SendChatCommand("target Luxon Priest"),
    transition_delay_ms=1000)

FSM_vars.state_machine.AddState(name="Interact NPC",
    execute_fn=lambda: Routines.Targeting.InteractTarget(),
    transition_delay_ms=1000)

FSM_vars.state_machine.AddState(name="Get Blessing",
    execute_fn=lambda: Take_Bounty(),
    transition_delay_ms=1500)

FSM_vars.state_machine.AddState(name="Follow Map Path",
    execute_fn=lambda: handle_map_path(),
    exit_condition=lambda: Routines.Movement.IsFollowPathFinished(FSM_vars.map_pathing, FSM_vars.movement_handler),
    run_once=False)

FSM_vars.loot_items.AddState(name="Select Item",
                    execute_fn=lambda: FSM_vars.current_loot_target is not None and Agent.IsItem(FSM_vars.current_loot_target) and Player.ChangeTarget(FSM_vars.current_loot_target),
                    transition_delay_ms=1000)
FSM_vars.loot_items.AddState(name="PickUpItem",
                    execute_fn=lambda: FSM_vars.current_loot_target is not None and Agent.IsItem(FSM_vars.current_loot_target) and Routines.Targeting.InteractTarget(),
                    transition_delay_ms=1000)
FSM_vars.loot_items.AddState(name="Wait for Loot to Finish",
                    exit_condition=lambda: WaitForLoot(),
                    run_once=False)

# Add new combat state
FSM_vars.state_machine.AddState(name="Combat",
    execute_fn=lambda: handle_combat(),
    exit_condition=lambda: not is_in_combat(),
    run_once=False)

def is_in_combat():
    """Check if we should be in combat state"""
    try:
        # If we're currently looting, don't enter combat
        if FSM_vars.current_loot_target is not None:
            return False
            
        my_id = Player.GetAgentID()
        my_x, my_y = Agent.GetXY(my_id)
        
        # Check for called target
        called_target = get_called_target()
        
        # Get nearby enemies
        enemy_array = AgentArray.GetEnemyArray()
        enemy_array = AgentArray.Filter.ByDistance(enemy_array, (my_x, my_y), 3000)
        enemy_array = AgentArray.Filter.ByAttribute(enemy_array, 'IsAlive')
        
        return called_target or len(enemy_array) > 0
    except Exception as e:
        Py4GW.Console.Log(module_name, f"Error in is_in_combat: {str(e)}", Py4GW.Console.MessageType.Error)
        return False

def handle_combat():
    """Handle combat interactions"""
    global FSM_vars
    try:
        # Check for loot first
        if LootFound():
            FSM_vars.state_machine.set_state("Follow Map Path")
            return

        my_id = Player.GetAgentID()
        my_x, my_y = Agent.GetXY(my_id)
        current_time = time.time()
        
        # Check for called target
        called_target = get_called_target()
        
        # Get nearby enemies
        enemy_array = AgentArray.GetEnemyArray()
        enemy_array = AgentArray.Filter.ByDistance(enemy_array, (my_x, my_y), 3000)
        enemy_array = AgentArray.Filter.ByAttribute(enemy_array, 'IsAlive')
        
        target_id = None
        
        # Handle enemy targeting
        if called_target and called_target in enemy_array:
            target_id = called_target
        else:
            not_hexed_array = AgentArray.Filter.ByAttribute(enemy_array, 'IsHexed', negate=True)
            target_id = not_hexed_array[0] if len(not_hexed_array) > 0 else enemy_array[0]
        
        if target_id:
            Player.ChangeTarget(target_id)
            target_x, target_y = Agent.GetXY(target_id)
            distance_to_target = ((my_x - target_x) ** 2 + (my_y - target_y) ** 2) ** 0.5
            
            # If target is too far, interact to move closer
            if distance_to_target > 1200:  # Spell range
                Routines.Targeting.InteractTarget()
                return
            
            # Only use skills when in range
            if current_time - FSM_vars.last_skill_time >= 2.0:
                if IsSkillReady2(FSM_vars.current_skill_index):
                    SkillBar.UseSkill(FSM_vars.current_skill_index)
                    Py4GW.Console.Log("Follower", f"Using skill {FSM_vars.current_skill_index} at distance {distance_to_target:.0f}", Py4GW.Console.MessageType.Info)
                    FSM_vars.last_skill_time = current_time
                    FSM_vars.current_skill_index = FSM_vars.current_skill_index % 8 + 1
                    
    except Exception as e:
        Py4GW.Console.Log(module_name, f"Error in handle_combat: {str(e)}", Py4GW.Console.MessageType.Error)

def handle_map_path():
    """Handle movement and check for combat triggers during map path traversal"""
    global FSM_vars
    try:
        # Check for loot first
        if LootFound():
            if (FSM_vars.current_loot_target is not None and 
                Agent.Exists(FSM_vars.current_loot_target)):
                FSM_vars.loot_items.set_state("Select Item")
                return
        
        # Check if we should enter combat state
        if is_in_combat():
            FSM_vars.state_machine.set_state("Combat")
            return
        
        # Continue path following if no combat or loot
        Routines.Movement.FollowPath(FSM_vars.map_pathing, FSM_vars.movement_handler)
                        
        # Check if we need to reset to initial state
        if not FSM_vars.state_machine.current_state:
            FSM_vars.state_machine.set_state("Check Map")
        
    except Exception as e:
        Py4GW.Console.Log(module_name, f"Error in handle_map_path: {str(e)}", Py4GW.Console.MessageType.Error)

def UpdateLootTarget(max_distance=1250):
    global FSM_vars
    try:
        if IfActionIsPending():
            return None

        # Reset loot target if it's no longer valid
        if FSM_vars.current_loot_target is not None:
            try:
                if not Agent.IsItem(FSM_vars.current_loot_target) or not Agent.Exists(FSM_vars.current_loot_target):
                    FSM_vars.current_loot_target = None
            except:
                FSM_vars.current_loot_target = None
            return None

        # Only look for a new loot target if we don't have one
        xy = Player.GetXY()
        if xy is None:
            return None

        try:
            item_array = AgentArray.GetItemArray()
            if not item_array:
                return None
            
            for item in item_array:
                if (item is not None and 
                    Agent.Exists(item) and 
                    Agent.IsItem(item) and 
                    Utils.Distance(xy, Agent.GetXY(item)) <= max_distance):
                    FSM_vars.current_loot_target = item
                    return item
        except:
            return None

    except Exception as e:
        Py4GW.Console.Log(module_name, f"Error in UpdateLootTarget: {str(e)}", Py4GW.Console.MessageType.Error)
        FSM_vars.current_loot_target = None
    
    return None

def LootFound():
    try:
        if not Agent.IsAlive(Player.GetAgentID()):
            return False
        
        UpdateLootTarget(max_distance=1250)
        return (FSM_vars.current_loot_target is not None and 
                Agent.Exists(FSM_vars.current_loot_target) and 
                Agent.IsItem(FSM_vars.current_loot_target))
    except:
        return False

def WaitForLoot():
    try:
        if IfActionIsPending():
            return False
        
        if not LootFound():
            return True
        else:
            SetPendingAction(2000)
            return False
    except Exception as e:
        Py4GW.Console.Log(module_name, f"Error in WaitForLoot: {str(e)}", Py4GW.Console.MessageType.Error)
        return True

def DrawWindow():
    global bot_vars, FSM_vars
    try:
        if bot_vars.window_module.first_run:
            PyImGui.set_next_window_size(bot_vars.window_module.window_size[0], bot_vars.window_module.window_size[1])     
            PyImGui.set_next_window_pos(bot_vars.window_module.window_pos[0], bot_vars.window_module.window_pos[1])
            bot_vars.window_module.first_run = False

        if PyImGui.begin(bot_vars.window_module.window_name, bot_vars.window_module.window_flags):
            if IsBotStarted():
                if PyImGui.button("Stop Bot"):
                    StopBot()
            else:
                if PyImGui.button("Start Bot"):
                    StartBot()
                if PyImGui.button("Reset"):
                    ResetEnvironment()
                    bot_vars.has_env_reset = False

            # Display current state
            PyImGui.text(f"Current State: {FSM_vars.state_machine.get_current_step_name()}")
            PyImGui.text(f"Current Map: {Map.GetMapID()}")

            PyImGui.end()

    except Exception as e:
        Py4GW.Console.Log(bot_vars.window_module.module_name, f"Error in DrawWindow: {str(e)}", Py4GW.Console.MessageType.Error)

def main():
    global bot_vars, FSM_vars
    try:
        DrawWindow()

        if IsBotStarted():
            if FSM_vars.state_machine.is_finished():
                ResetEnvironment()
            else:
                FSM_vars.state_machine.update()

    except Exception as e:
        Py4GW.Console.Log(bot_vars.window_module.module_name, f"Error in main: {str(e)}", Py4GW.Console.MessageType.Error)

if __name__ == "__main__":
    main() 