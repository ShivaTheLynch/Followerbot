from Py4GWCoreLib import *

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

bot_vars = BotVars()
bot_vars.window_module = ImGui.WindowModule(module_name, window_name="Simple Movement", window_size=(300, 200))
FSM_vars = StateMachineVars()

# Helper Functions
def StartBot():
    global bot_vars
    if not bot_vars.has_env_reset:
        ResetEnvironment()
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
    execute_fn=lambda: Routines.Movement.FollowPath(FSM_vars.map_pathing, FSM_vars.movement_handler),
    exit_condition=lambda: Routines.Movement.IsFollowPathFinished(FSM_vars.map_pathing, FSM_vars.movement_handler),
    run_once=False)

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