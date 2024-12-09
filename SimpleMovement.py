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

bot_vars = BotVars()
bot_vars.window_module = ImGui.WindowModule(module_name, window_name="Simple Movement", window_size=(300, 200))
FSM_vars = StateMachineVars()

# Helper Functions
def StartBot():
    global bot_vars, FSM_vars
    if not bot_vars.has_env_reset:
        ResetEnvironment()
        # If we're already in the farm map, find nearest coordinate
        if Map.GetMapID() == 200:  # Assuming 200 is your farm map ID
            try:
                my_id = Player.GetAgentID()
                if my_id:  # Make sure we have a valid player ID
                    my_x, my_y = Agent.GetXY(my_id)
                    
                    # Find the nearest point in the path with error handling
                    min_distance = float('inf')
                    nearest_index = 0
                    
                    for i, coord in enumerate(map_path):
                        try:
                            distance = ((my_x - coord[0]) ** 2 + (my_y - coord[1]) ** 2) ** 0.5
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
                        FSM_vars.state_machine.force_state("Follow Map Path")
                    
            except Exception as e:
                Py4GW.Console.Log("SimpleMovement", f"Error finding nearest coordinate: {str(e)}", Py4GW.Console.MessageType.Error)
                # Fallback to starting from the beginning
                FSM_vars.map_pathing.reset()
                FSM_vars.state_machine.reset()
        
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

def handle_map_path():
    """Handle both movement and combat during map path traversal"""
    global FSM_vars
    my_id = Player.GetAgentID()
    my_x, my_y = Agent.GetXY(my_id)
    current_time = time.time()
    
    # Check for called target first
    called_target = get_called_target()
    
    # Get nearby enemies
    enemy_array = AgentArray.GetEnemyArray()
    enemy_array = AgentArray.Filter.ByDistance(enemy_array, (my_x, my_y), 3000)
    enemy_array = AgentArray.Filter.ByAttribute(enemy_array, 'IsAlive')
    
    # If there's a called target or nearby enemy, handle combat
    if called_target or len(enemy_array) > 0:
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
    else:
        # Only continue path following if no enemies are nearby
        Routines.Movement.FollowPath(FSM_vars.map_pathing, FSM_vars.movement_handler)

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