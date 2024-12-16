# ExtendedCoreLib.py
from Py4GWCoreLib import *  # Import everything from the core library
from Py4GWCoreLib import Routines, Utils  # Import the specific parts of Routines

# Utils
class ExtendedUtils(Utils):
    class Filters:
        @staticmethod
        def FilterSelfFromAgentArray(agent_array):
            """
            Purpose: Filter the player from an agent array.
            Args:
                agent_array (list): The list of agent IDs.
            Returns: list
            """
            player_instance = PyPlayer.PyPlayer()
            return [agent_id for agent_id in agent_array if agent_id != player_instance.id]

        @staticmethod
        def FilterAgentArrayByRange(agent_pos,agent_array, area=5000):
            """
            Purpose: Filter an agent array by range.
            Args:
                agent_array (list): The list of agent IDs.
                area (int, optional): The area to search for the nearest agent. Default is 5000.
            Returns: list
            """
            x, y = Player.GetXY()

            filtered_agent_array = []
            for agent_id in agent_array:
                agent_instance = PyAgent.PyAgent(agent_id)
                if Utils.Distance(agent_pos, (agent_instance.x, agent_instance.y)) <= area:
                    filtered_agent_array.append(agent_id)
            return filtered_agent_array

        @staticmethod
        def FilterAgentArrayByMoving(agent_pos, agent_array, area=5000):
            """
            Purpose: Filter an agent array by moving.
            Args:
                agent_array (list): The list of agent IDs.
                area (int, optional): The area to search for the nearest agent. Default is 5000.
            Returns: list
            """
            range_array = Utils.Filters.FilterAgentArrayByRange(agent_pos, agent_array, area)
            filtered_agent_array = []
            for agent_id in range_array:
                if Agent.IsMoving(agent_id):
                    filtered_agent_array.append(agent_id)
            return filtered_agent_array

        @staticmethod
        def FilterAgentArrayByDead(agent_pos, agent_array, area=5000):
            """
            Purpose: Filter an agent array by dead.
            Args:
                agent_array (list): The list of agent IDs.
                area (int, optional): The area to search for the nearest agent. Default is 5000.
            Returns: list
            """
            range_array = Utils.Filters.FilterAgentArrayByRange(agent_pos, agent_array, area)
            filtered_agent_array = []
            for agent_id in range_array:
                if Agent.IsDead(agent_id):
                    filtered_agent_array.append(agent_id)
            return filtered_agent_array

        @staticmethod
        def FilterAgentArrayByAlive(agent_pos, agent_array, area=5000):
            """
            Purpose: Filter an agent array by alive.
            Args:
                agent_array (list): The list of agent IDs.
                area (int, optional): The area to search for the nearest agent. Default is 5000.
            Returns: list
            """
            range_array = Utils.Filters.FilterAgentArrayByRange(agent_pos, agent_array, area)
            filtered_agent_array = []
            for agent_id in range_array:
                if Agent.IsAlive(agent_id):
                    filtered_agent_array.append(agent_id)
            return filtered_agent_array

        @staticmethod
        def FilterAgentArrayByIsConditioned(agent_pos, agent_array, area=5000):
            """
            Purpose: Filter an agent array by conditioned.
            Args:
                agent_array (list): The list of agent IDs.
                area (int, optional): The area to search for the nearest agent. Default is 5000.
            Returns: list
            """
            range_array = Utils.Filters.FilterAgentArrayByRange(agent_pos, agent_array, area)
            filtered_agent_array = []
            for agent_id in range_array:
                if Agent.IsConditioned(agent_id):
                    filtered_agent_array.append(agent_id)
            return filtered_agent_array

        @staticmethod
        def FilterAgentArrayByIsBleeding(agent_pos, agent_array, area=5000):
            """
            Purpose: Filter an agent array by bleeding.
            Args:
                agent_array (list): The list of agent IDs.
                area (int, optional): The area to search for the nearest agent. Default is 5000.
            Returns: list
            """
            range_array = Utils.Filters.FilterAgentArrayByRange(agent_pos, agent_array, area)
            filtered_agent_array = []
            for agent_id in range_array:
                if Agent.IsBleeding(agent_id):
                    filtered_agent_array.append(agent_id)
            return filtered_agent_array

        @staticmethod
        def FilterAgentArrayByIsPoisoned(agent_pos, agent_array, area=5000):
            """
            Purpose: Filter an agent array by poisoned.
            Args:
                agent_array (list): The list of agent IDs.
                area (int, optional): The area to search for the nearest agent. Default is 5000.
            Returns: list
            """
            range_array = Utils.Filters.FilterAgentArrayByRange(agent_pos, agent_array, area)
            filtered_agent_array = []
            for agent_id in range_array:
                if Agent.IsPoisoned(agent_id):
                    filtered_agent_array.append(agent_id)
            return filtered_agent_array

        @staticmethod
        def FilterAgentByIsDeepWounded(agent_pos, agent_array, area=5000):
            """
            Purpose: Filter an agent array by deep wounded.
            Args:
                agent_array (list): The list of agent IDs.
                area (int, optional): The area to search for the nearest agent. Default is 5000.
            Returns: list
            """
            range_array = Utils.Filters.FilterAgentArrayByRange(agent_pos, agent_array, area)
            filtered_agent_array = []
            for agent_id in range_array:
                if Agent.IsDeepWounded(agent_id):
                    filtered_agent_array.append(agent_id)
            return filtered_agent_array

        @staticmethod
        def FilterAgentArrayByIsCrippled(agent_pos, agent_array, area=5000):
            """
            Purpose: Filter an agent array by crippled.
            Args:
                agent_array (list): The list of agent IDs.
                area (int, optional): The area to search for the nearest agent. Default is 5000.
            Returns: list
            """
            range_array = Utils.Filters.FilterAgentArrayByRange(agent_pos, agent_array, area)
            filtered_agent_array = []
            for agent_id in range_array:
                if Agent.IsCrippled(agent_id):
                    filtered_agent_array.append(agent_id)
            return filtered_agent_array

        @staticmethod
        def FilterArrayByOwnerID(agent_pos, agent_array, owner_id, area=5000):
            """
            Purpose: Filter an agent array by owner ID.
            Args:
                agent_array (list): The list of agent IDs.
                owner_id (int): The ID of the owner.
                area (int, optional): The area to search for the nearest agent. Default is 5000.
            Returns: list
            """
            range_array = Utils.Filters.FilterAgentArrayByRange(agent_pos, agent_array, area)
            filtered_agent_array = []
            for agent_id in range_array:
                if Agent.GetOwnerID(agent_id) == owner_id:
                    filtered_agent_array.append(agent_id)
            return filtered_agent_array

        @staticmethod
        def FilterArrayByNotOwnerID(agent_pos, agent_array, owner_id, area=5000):
            """
            Purpose: Filter an agent array by not owner ID.
            Args:
                agent_array (list): The list of agent IDs.
                owner_id (int): The ID of the owner.
                area (int, optional): The area to search for the nearest agent. Default is 5000.
            Returns: list
            """
            range_array = Utils.Filters.FilterAgentArrayByRange(agent_pos, agent_array, area)
            filtered_agent_array = []
            for agent_id in range_array:
                if Agent.GetOwnerID(agent_id) != owner_id:
                    filtered_agent_array.append(agent_id)
            return filtered_agent_array

        @staticmethod
        def FilterArrayByHasBossGlow(agent_pos, agent_array, area=5000):
            """
            Purpose: Filter an agent array by boss glow.
            Args:
                agent_array (list): The list of agent IDs.
                area (int, optional): The area to search for the nearest agent. Default is 5000.
            Returns: list
            """
            range_array = Utils.Filters.FilterAgentArrayByRange(agent_pos, agent_array, area)
            filtered_agent_array = []
            for agent_id in range_array:
                if Agent.HasBossGlow(agent_id):
                    filtered_agent_array.append(agent_id)
            return filtered_agent_array

        @staticmethod
        def FilterArrayByHasEnchantment(agent_pos, agent_array, area=5000):
            """
            Purpose: Filter an agent array by enchantment.
            Args:
                agent_array (list): The list of agent IDs.
                area (int, optional): The area to search for the nearest agent. Default is 5000.
            Returns: list
            """
            range_array = Utils.Filters.FilterAgentArrayByRange(agent_pos, agent_array, area)
            filtered_agent_array = []
            for agent_id in range_array:
                if Agent.HasEnchantment(agent_id):
                    filtered_agent_array.append(agent_id)
            return filtered_agent_array

        @staticmethod
        def FilterArrayByNotHasEnchantment(agent_pos, agent_array, area=5000):
            """
            Purpose: Filter an agent array by not having an enchantment.
            Args:
                agent_array (list): The list of agent IDs.
                area (int, optional): The area to search for the nearest agent. Default is 5000.
            Returns: list
            """
            range_array = Utils.Filters.FilterAgentArrayByRange(agent_pos, agent_array, area)
            filtered_agent_array = []
            for agent_id in range_array:
                if not Agent.HasEnchantment(agent_id):
                    filtered_agent_array.append(agent_id)
            return filtered_agent_array

        @staticmethod
        def FilterArrayByHasHex(agent_pos, agent_array, area=5000):
            """
            Purpose: Filter an agent array by hex.
            Args:
                agent_array (list): The list of agent IDs.
                area (int, optional): The area to search for the nearest agent. Default is 5000.
            Returns: list
            """
            range_array = Utils.Filters.FilterAgentArrayByRange(agent_pos, agent_array, area)
            filtered_agent_array = []
            for agent_id in range_array:
                if Agent.HasHex(agent_id):
                    filtered_agent_array.append(agent_id)
            return filtered_agent_array

        @staticmethod
        def FilterArrayByNotHasHex(agent_pos, agent_array, area=5000):
            """
            Purpose: Filter an agent array by not having a hex.
            Args:
                agent_array (list): The list of agent IDs.
                area (int, optional): The area to search for the nearest agent. Default is 5000.
            Returns: list
            """
            range_array = Utils.Filters.FilterAgentArrayByRange(agent_pos, agent_array, area)
            filtered_agent_array = []
            for agent_id in range_array:
                if not Agent.HasHex(agent_id):
                    filtered_agent_array.append(agent_id)
            return filtered_agent_array

        @staticmethod
        def FilterArrayByIsCasting(agent_pos, agent_array, area=5000):
            """
            Purpose: Filter an agent array by casting.
            Args:
                agent_array (list): The list of agent IDs.
                area (int, optional): The area to search for the nearest agent. Default is 5000.
            Returns: list
            """
            range_array = Utils.Filters.FilterAgentArrayByRange(agent_pos, agent_array, area)
            filtered_agent_array = []
            for agent_id in range_array:
                if Agent.IsCasting(agent_id):
                    filtered_agent_array.append(agent_id)
            return filtered_agent_array

        @staticmethod
        def FilterArrayByNotCasting(agent_pos, agent_array, area=5000):
            """
            Purpose: Filter an agent array by not casting.
            Args:
                agent_array (list): The list of agent IDs.
                area (int, optional): The area to search for the nearest agent. Default is 5000.
            Returns: list
            """
            range_array = Utils.Filters.FilterAgentArrayByRange(agent_pos, agent_array, area)
            filtered_agent_array = []
            for agent_id in range_array:
                if not Agent.IsCasting(agent_id):
                    filtered_agent_array.append(agent_id)
            return filtered_agent_array

        @staticmethod
        def FilterAgentArrayByIsMartial(agent_pos, agent_array, area=5000):
            """
            Purpose: Filter an agent array by martial.
            Args:
                agent_array (list): The list of agent IDs.
                area (int, optional): The area to search for the nearest agent. Default is 5000.
            Returns: list
            """
            range_array = Utils.Filters.FilterAgentArrayByRange(agent_pos, agent_array, area)
            filtered_agent_array = []
            for agent_id in range_array:
                if Agent.IsMartial(agent_id):
                    filtered_agent_array.append(agent_id)
            return filtered_agent_array

        @staticmethod
        def FilterAgentArrayByIsCaster(agent_pos, agent_array, area=5000):
            """
            Purpose: Filter an agent array by caster.
            Args:
                agent_array (list): The list of agent IDs.
                area (int, optional): The area to search for the nearest agent. Default is 5000.
            Returns: list
            """
            range_array = Utils.Filters.FilterAgentArrayByRange(agent_pos, agent_array, area)
            filtered_agent_array = []
            for agent_id in range_array:
                if Agent.IsCaster(agent_id):
                    filtered_agent_array.append(agent_id)
            return filtered_agent_array

        @staticmethod
        def FilterAgentArrayByIsRanged(agent_pos, agent_array, area=5000):
            """
            Purpose: Filter an agent array by ranged.
            Args:
                agent_array (list): The list of agent IDs.
                area (int, optional): The area to search for the nearest agent. Default is 5000.
            Returns: list
            """
            range_array = Utils.Filters.FilterAgentArrayByRange(agent_pos, agent_array, area)
            filtered_agent_array = []
            for agent_id in range_array:
                if Agent.IsRanged(agent_id):
                    filtered_agent_array.append(agent_id)
            return filtered_agent_array

        @staticmethod
        def FilterAgentArrayByIsMelee(agent_pos, agent_array, area=5000):
            """
            Purpose: Filter an agent array by melee.
            Args:
                agent_array (list): The list of agent IDs.
                area (int, optional): The area to search for the nearest agent. Default is 5000.
            Returns: list
            """
            range_array = Utils.Filters.FilterAgentArrayByRange(agent_pos, agent_array, area)
            filtered_agent_array = []
            for agent_id in range_array:
                if Agent.IsMelee(agent_id):
                    filtered_agent_array.append(agent_id)
            return filtered_agent_array

class ExtendedRoutines(Routines):
    class Movement:
        def FollowPath(path_handler, follow_handler, log_actions=False):
            """
            Purpose: Follow a path using the path handler and follow handler objects.
            Args:
                path_handler (PathHandler): The PathHandler object containing the path coordinates.
                follow_handler (FollowXY): The FollowXY object for moving to waypoints.
            Returns: None
            """
            if follow_handler.is_following():
                follow_handler.update()
                return

            current_position = Player.GetXY()
            point = path_handler.advance(current_position)
            if point is not None:
                follow_handler.move_to_waypoint(point[0], point[1])
                if log_actions:
                    Py4GW.Console.Log("FollowPath", f"Moving to {point}", Py4GW.Console.MessageType.Info)

        def IsFollowPathFinished(path_handler, follow_handler):
            return path_handler.is_finished() and follow_handler.has_arrived()


        class FollowXY:
            def __init__(self, tolerance=100):
                """
                Initialize the FollowXY object with default values.
                Routine for following a waypoint.
                """
                self.waypoint = (0, 0)
                self.tolerance = tolerance
                self.player_instance = PyPlayer.PyPlayer()
                self.following = False
                self.arrived = False
                self.timer = Py4GW.Timer()  # Timer to track movement start time
                self.wait_timer = Py4GW.Timer()  # Timer to track waiting after issuing move command
                self.wait_timer_run_once = True

            def calculate_distance(self, pos1, pos2):
                """
                Calculate the Euclidean distance between two points.
                """
                return math.sqrt((pos1[0] - pos2[0]) ** 2 + (pos1[1] - pos2[1]) ** 2)

            def move_to_waypoint(self, x, y, tolerance=None):
                """
                Move the player to the specified coordinates.
                Args:
                    x (float): X coordinate of the waypoint.
                    y (float): Y coordinate of the waypoint.
                    tolerance (int, optional): The distance threshold to consider arrival. Defaults to the initialized value.
                """
                self.reset()
                self.waypoint = (x, y)
                self.tolerance = tolerance if tolerance is not None else self.tolerance
                self.following = True
                self.arrived = False
                self.player_instance.Move(x, y)
                self.timer.start()

            def reset(self):
                """
                Cancel the current move command and reset the waypoint following state.
                """
                self.following = False
                self.arrived = False
                self.timer.reset()
                self.wait_timer.reset()

            def update(self):
                """
                Update the FollowXY object's state, check if the player has reached the waypoint,
                and issue new move commands if necessary.
                """
                if self.following:
                    current_position = Player.GetXY()
                    is_casting = Agent.IsCasting(Player.GetAgentID())
                    is_moving = Agent.IsMoving(Player.GetAgentID())
                    is_knocked_down = Agent.IsKnockedDown(Player.GetAgentID())

                    # Check if the wait timer has elapsed and re-enable movement checks
                    if self.wait_timer.has_elapsed(1500):
                        self.wait_timer.reset()
                        self.wait_timer_run_once = True

                    # Check if the player has arrived at the waypoint
                    if self.calculate_distance(current_position, self.waypoint) <= self.tolerance:
                        self.arrived = True
                        self.following = False
                        return

                    if is_casting or is_moving or is_knocked_down:
                        return 

                    # Re-issue the move command if the player is not moving and not casting
                    if self.wait_timer_run_once:
                        # Use the move_to_waypoint function to reissue movement
                        Player.Move(0,0) #reset movement pointer?
                        Player.Move(self.waypoint[0], self.waypoint[1])
                        self.wait_timer_run_once  = False  # Disable immediate re-issue
                        self.wait_timer.start()  # Start the wait timer to prevent spamming movement
                        Py4GW.Console.Log("FollowXY", f"stopped, reissue move", Py4GW.Console.MessageType.Info)

            def get_time_elapsed(self):
                """
                Get the elapsed time since the player started moving.
                """
                return self.timer.get_elapsed_time()

            def get_distance_to_waypoint(self):
                """
                Get the distance between the player and the current waypoint.
                """
                current_position = Player.GetXY()
                return self.calculate_distance(current_position, self.waypoint)

            def is_following(self):
                """
                Check if the player is currently following a waypoint.
                """
                return self.following

            def has_arrived(self):
                """
                Check if the player has arrived at the current waypoint.
                """
                return self.arrived


        class PathHandler:
            def __init__(self, coordinates, tolerance=100):
                """
                Purpose: Initialize the PathHandler with a list of coordinates.
                Args:
                    coordinates (list): A list of tuples representing the points (x, y).
                Returns: None
                """
                self.coordinates = coordinates
                self.tolerance = tolerance
                self.visited = [False] * len(coordinates)  # Track visited points
                self.index = 0
                self.reverse = False  # By default, move forward
                self.finished = False

            def get_current_point(self):
                """
                Purpose: Get the current point in the list of coordinates.
                Args: None
                Returns: tuple or None
                """
                if not self.coordinates or self.finished:
                    return None
                return self.coordinates[self.index]

            # Helper function to calculate distance
            def calculate_distance(self, pos1, pos2):
                return ((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)**0.5
            
            def advance(self, current_position):
                """
                Returns the next target point based on the path and updates the visited status.
                If the current point is reached within tolerance, it marks it as visited and advances.
                """
                if self.index >= len(self.coordinates):
                    return None  # All points have been visited

                # If we are at the start (index 0), find the closest point
                if self.index == 0:
                    closest_index = 0
                    closest_distance = self.calculate_distance(current_position, self.coordinates[0])
                    
                    for i in range(1, len(self.coordinates)):
                        distance = self.calculate_distance(current_position, self.coordinates[i])
                        if distance < closest_distance:
                            closest_distance = distance
                            closest_index = i

                    self.index = closest_index  # Set index to the closest point

                current_point = self.coordinates[self.index]
                
                # Check if we've reached the current point
                if self.calculate_distance(current_position, current_point) <= self.tolerance:
                    self.visited[self.index] = True

                    if self.index < len(self.coordinates) - 1:
                        self.index += 1
                    else:
                        self.finished = True

                    # If there's a next point, return it; otherwise, return None
                    if self.index < len(self.coordinates):
                        return self.coordinates[self.index]
                
                return current_point  # Still need to move to the current point

            def toggle_direction(self):
                """
                Purpose: Manually reverse the current direction of traversal.
                Args: None
                Returns: None
                """
                self.reverse = not self.reverse

            def reset(self):
                """
                Purpose: Reset the path traversal to the start or end depending on direction.
                Args: None
                Returns: None
                """
                self.index = 0 if not self.reverse else len(self.coordinates) - 1
                self.finished = False

            def is_finished(self):
                """
                Purpose: Check if the traversal has finished.
                Args: None
                Returns: bool
                """
                return self.finished

            def set_position(self, index):
                """
                Purpose: Set the current index in the list of coordinates.
                Args:
                    index (int): The index to set the position to.
                Returns: None
                """
                if 0 <= index < len(self.coordinates):
                    self.index = index
                    self.finished = False
                else:
                    raise IndexError(f"Index {index} out of bounds for coordinates list")

            def get_position(self):
                """
                Purpose: Get the current index in the list of coordinates.
                Args: None
                Returns: int
                """
                return self.index
 

class FSM:
    def __init__(self, name, log_actions=False):
        """
        Initialize the FSM with a name and track its states and transitions.
        :param name: The name of the FSM (for logging and identification purposes).
        """
        self.name = name  # Store the FSM name
        self.states = []  # List to store all states in order
        self.current_state = None  # Track the current state
        self.state_counter = 0  # Internal counter for state IDs
        self.log_actions = log_actions  # Whether to log state transitions and actions
        self.finished = False  # Track whether the FSM has completed all states


    class State:
        def __init__(self, id, name=None, execute_fn=None, exit_condition=None, transition_delay_ms=0, run_once=True):
            """
            :param id: Internal ID of the state.
            :param name: Optional name of the state (for debugging purposes).
            :param execute_fn: A function representing the block of code to be executed in this state.
            :param exit_condition: A function that returns True/False to determine if it can transition to the next state.
            :param run_once: Whether the execution function should run only once (default: True).
            :param transition_delay_ms: Delay in milliseconds before checking the exit condition (default: 0).
            """
            self.id = id
            self.name = name or f"State-{id}"  # If no name is provided, use "State-ID"
            self.execute_fn = execute_fn or (lambda: None)  # Default to no action if not provided
            self.exit_condition = exit_condition or (lambda: True)  # Default to False if not provided
            self.run_once = run_once  # Flag to control whether the action runs once or repeatedly
            self.executed = False  # Track whether the state's execute function has been run
            self.transition_delay_ms = transition_delay_ms  # Delay before transitioning to the next state
            self.transition_timer = Timer()  # Timer to manage the delay

        def execute(self):
            """Run the state's block of code. If `run_once` is True, run it only once."""
            if not self.run_once or not self.executed:
                self.execute_fn()
                self.executed = True  # Mark execution as complete if run_once is True
                self.transition_timer.Reset()  # Reset the timer

        def can_exit(self):
            """
            Check if the exit condition is met and if the transition delay has passed.
            """
            if self.transition_timer.HasElapsed(self.transition_delay_ms):
                if self.exit_condition():
                    # If the exit condition is true and the delay has passed, return True
                    return True
                else:
                    # Reset the timer if the exit condition is not yet met
                    self.transition_timer.Reset()
            return False

        def reset(self):
            """Reset the state so it can be re-entered, if needed."""
            self.executed = False
            self.transition_timer.Stop()  # Reset timer when resetting the state

        def set_next_state(self, next_state):
            """Set the next state for transitions."""
            self.next_state = next_state

    class ConditionState(State):
        def __init__(self, id, name=None, condition_fn=None, sub_fsm=None):
            """
            A state that evaluates a condition and decides whether to continue or run a sub-FSM.

            :param condition_fn: Function that returns True/False. If True, it transitions to the next state. If False,
                                 it runs the sub_fsm and waits for it to finish before transitioning.
            :param sub_fsm: An optional sub-FSM that will be run if condition_fn returns False.
            """
            super().__init__(id, name)
            self.condition_fn = condition_fn if condition_fn is not None else (lambda: True)  # Default to True if no condition provided
            self.sub_fsm = sub_fsm
            self.sub_fsm_active = False

        def execute(self):
            # Py4GW.Console.Log("FSM", f"Executing State: {self.name}", Py4GW.Console.MessageType.Debug)

            if self.sub_fsm_active:
                # If the sub-FSM is running, update it and check if it is finished
                # Py4GW.Console.Log("FSM", f"Updating Sub-FSM: {self.sub_fsm.name}", Py4GW.Console.MessageType.Debug)

                if not self.sub_fsm.is_finished():
                    self.sub_fsm.update()
                else:
                    # Py4GW.Console.Log("FSM", f"Sub-FSM Finished: {self.sub_fsm.name}", Py4GW.Console.MessageType.Success)

                    # Re-evaluate condition after sub-FSM completion
                    if not self.condition_fn():
                        # Py4GW.Console.Log("FSM", "Restarting Sub-FSM", Py4GW.Console.MessageType.Info)
                        self.sub_fsm.reset()
                        self.sub_fsm.start()
                        self.sub_fsm_active = True
                    else:
                        self.sub_fsm_active = False  # Sub-FSM finished, can continue execution
                        self.executed = True

            else:
                # Evaluate the condition initially
                if not self.condition_fn():
                    # Py4GW.Console.Log("FSM", "Condition Not Met: Starting Sub-FSM", Py4GW.Console.MessageType.Success)

                    if self.sub_fsm:
                        self.sub_fsm.reset()
                        self.sub_fsm.start()
                        self.sub_fsm_active = True
                else:
                    # Py4GW.Console.Log("FSM", "Condition Met: Moving to Next State", Py4GW.Console.MessageType.Warning)
                    self.executed = True  # Continue to the next state


        def can_exit(self):
            """
            The node can exit only if the condition is met or the sub-FSM has finished running.
            """
            return self.executed and not self.sub_fsm_active

    def SetLogBehavior(self, log_actions=False):
        """
        Set whether to log state transitions and actions.
        :param log_actions: Whether to log state transitions and actions (default: False).
        """
        self.log_actions = log_actions

    def GetLogBehavior(self):
        """Get the current logging behavior setting."""
        return self.log_actions

    def AddState(self, name=None, execute_fn=None, exit_condition=None, transition_delay_ms=0, run_once=True):
        """Add a state with an optional name, execution function, and exit condition."""
        state = FSM.State(
            id=self.state_counter,
            name=name,
            execute_fn=execute_fn,
            exit_condition=exit_condition,
            run_once=run_once,
            transition_delay_ms=transition_delay_ms
        )
        
        if self.states:
            self.states[-1].set_next_state(state)
        
        self.states.append(state)
        self.state_counter += 1


    def AddSubroutine(self, name=None, condition_fn=None, sub_fsm=None):
        """Add a condition node that evaluates a condition and can run a subroutine FSM."""
        condition_node = FSM.ConditionState(
            id=self.state_counter,
            name=name,
            condition_fn=condition_fn,
            sub_fsm=sub_fsm
        )
        if self.states:
            self.states[-1].set_next_state(condition_node)
        self.states.append(condition_node)
        self.state_counter += 1

    def start(self):
        """Start the FSM by setting the initial state."""
        if not self.states:
            raise ValueError(f"{self.name}: No states have been added to the FSM.")
        self.current_state = self.states[0]
        self.finished = False
        Py4GW.Console.Log("FSM", f"{self.name}: Starting FSM with initial state: {self.current_state.name}", Py4GW.Console.MessageType.Success)

    def stop(self):
        """Stop the FSM and mark it as finished."""
        self.current_state = None
        self.finished = True

        if self.log_actions:
            Py4GW.Console.Log("FSM", f"{self.name}: FSM has been stopped by user.", Py4GW.Console.MessageType.Info)

    def reset(self):
        """Reset the FSM to the initial state without starting it."""
        if not self.states:
            raise ValueError(f"{self.name}: No states have been added to the FSM.")
        self.current_state = self.states[0]  # Reset to the first state
        self.finished = False
        for state in self.states:
            state.reset()  # Reset all states

        if self.log_actions:
            Py4GW.Console.Log("FSM", f"{self.name}: FSM has been reset.", Py4GW.Console.MessageType.Info)


    def update(self):
        """Update the FSM: execute the current state and transition if the exit condition is met."""
        if self.current_state is None:
            # FSM has either not started or already finished
            Py4GW.Console.Log("FSM", f"{self.name}: FSM has not been started or has finished.", Py4GW.Console.MessageType.Warning)
            return

        # Execute the current state's logic (runs once or repeatedly based on the run_once flag)
        if self.log_actions:
            Py4GW.Console.Log("FSM", f"{self.name}: Executing state: {self.current_state.name}", Py4GW.Console.MessageType.Info)
        
        self.current_state.execute()

        # Check if the current state's exit condition is met
        if self.current_state.can_exit():
            if hasattr(self.current_state, 'next_state') and self.current_state.next_state is not None:
                # Transition to the next state
                if self.log_actions:
                    Py4GW.Console.Log("FSM", f"{self.name}: Transitioning from state: {self.current_state.name} to state: {self.current_state.next_state.name}", Py4GW.Console.MessageType.Info)
                self.current_state = self.current_state.next_state
                self.current_state.reset()  # Reset the next state for execution
            else:
                if self.log_actions:
                    Py4GW.Console.Log("FSM", f"{self.name}: Reached the final state: {self.current_state.name}. FSM has completed.", Py4GW.Console.MessageType.Success)
                self.current_state = None  # End of the state machine
                self.finished = True  # Set the FSM to finished
        else:
            if self.log_actions:
                Py4GW.Console.Log("FSM", f"{self.name}: Remaining in state: {self.current_state.name}", Py4GW.Console.MessageType.Info)

    def is_started(self):
        """Check whether the FSM has been started."""
        return self.current_state is not None and not self.finished
                
    def is_finished(self):
        """Check whether the FSM has finished executing all states."""
        return self.finished

    def jump_to_state(self, state_id):
        """Jump to a specific state by its ID."""
        if state_id < 0 or state_id >= len(self.states):
            raise ValueError(f"Invalid state ID: {state_id}")
        self.current_state = self.states[state_id]
        if self.log_actions:
            Py4GW.Console.Log("FSM", f"{self.name}: Jumped to state: {self.current_state.name}", Py4GW.Console.MessageType.Info)
        self.current_state.reset()  # Reset the state upon jumping to it

    def jump_to_state_by_name(self, state_name):
        """Jump to a specific state by its name."""
        for state in self.states:
            if state.name == state_name:
                self.current_state = state
                if self.log_actions:
                    Py4GW.Console.Log("FSM", f"{self.name}: Jumped to state: {self.current_state.name}", Py4GW.Console.MessageType.Info)
                self.current_state.reset()  # Reset the state upon jumping to it
                return
        raise ValueError(f"State with name '{state_name}' not found.")

    def get_current_step_name(self):
        """Get the name of the current step (state) in the FSM."""
        if self.current_state is None:
            return f"{self.name}: FSM not started or finished"
        return self.current_state.name


    def get_next_step_name(self):
        """Get the name of the next step (state) in the FSM."""
        if self.current_state is None:
            return f"{self.name}: FSM not started or finished"
        if hasattr(self.current_state, 'next_state') and self.current_state.next_state:
            return self.current_state.next_state.name
        return f"{self.name}: No next state (final state reached)"

    def get_previous_step_name(self):
        """Get the name of the previous step (state) in the FSM."""
        if self.current_state is None:
            return f"{self.name}: FSM not started or finished"
        current_index = self.states.index(self.current_state)
        if current_index > 0:
            return self.states[current_index - 1].name
        return f"{self.name}: No previous state (first state)"

class Combat:
    def CastSkill(skill_slot):
        SkillBar.UseSkill(skill_slot)

    def GetEnergyAgentCost(skill_slot, agent_id):
        """Retrieve the actual energy cost of a skill by its ID and effects.

        Args:
            skill_id (int): ID of the skill.
            agent_id (int): ID of the agent (player or hero).

        Returns:
            float: Final energy cost after applying all effects.
                Values are rounded to integers.
                Minimum cost is 0 unless otherwise specified by an effect.
        """
        skill_id = SkillBar.GetSkillIDBySlot(skill_slot)
        # Get base energy cost for the skill
        cost = Skill.skill_instance(skill_id).energy_cost

        # Adjust base cost for special cases (API inconsistencies)
        if cost == 11:
            cost = 15    # True cost is 15
        elif cost == 12:
            cost = 25    # True cost is 25

        # Get all active effects on the agent
        player_effects = Effects.GetEffects(agent_id)

        # Process each effect in order of application
        # Effects are processed in this specific order to match game mechanics
        for effect in player_effects:
            effect_id = effect.skill_id
            attr = Effects.EffectAttributeLevel(agent_id, effect_id)

            match effect_id:
                case 469:  # Primal Echoes - Forces Signets to cost 10 energy
                    if Skill.Flags.IsSignet(skill_id):
                        cost = 10  # Fixed cost regardless of other effects
                        continue  # Allow other effects to modify this cost

                case 475:  # Quickening Zephyr - Increases energy cost by 30%
                    cost *= 1.30   # Using multiplication instead of addition for better precision
                    continue

                case 1725:  # Roaring Winds - Increases Shout/Chant cost based on attribute level
                    if Skill.Flags.IsChant(skill_id) or Skill.Flags.IsShout(skill_id):
                        match attr:
                            case a if 0 < a <= 1:
                                cost += 1
                            case a if 2 <= a <= 5:
                                cost += 2
                            case a if 6 <= a <= 9:
                                cost += 3
                            case a if 10 <= a <= 13:
                                cost += 4
                            case a if 14 <= a <= 16:
                                cost += 5
                            case a if 17 <= a <= 20:
                                cost += 6
                        continue

                case 1677:  # Veiled Nightmare - Increases all costs by 40%
                    cost *= 1.40
                    continue

                case 856:  # "Kilroy Stonekin" - Reduces all costs by 50%
                    cost *= 0.50
                    continue

                case 1115:  # Air of Enchantment
                    if Skill.Flags.IsEnchantment(skill_id):
                        cost -= 5
                    continue

                case 1223:  # Anguished Was Lingwah
                    if Skill.Flags.IsHex(skill_id) and Skill.GetProfession(skill_id)[0] == 8:
                        match attr:
                            case a if 0 < a <= 1:
                                cost -= 1
                            case a if 2 <= a <= 5:
                                cost -= 2
                            case a if 6 <= a <= 9:
                                cost -= 3
                            case a if 10 <= a <= 13:
                                cost -= 4
                            case a if 14 <= a <= 16:
                                cost -= 5
                            case a if 17 <= a <= 20:
                                cost -= 6
                            case a if a > 20:
                                cost -= 7
                        continue

                case 1220:  # Attuned Was Songkai
                    if Skill.Flags.IsSpell(skill_id) or Skill.Flags.IsRitual(skill_id):
                        percentage = 5 + (attr * 3) if attr <= 20 else 68
                        cost -= cost * (percentage / 100)
                    continue

                case 596:  # Chimera of Intensity
                    cost -= cost * 0.50
                    continue

                case 806:  # Cultist's Fervor
                    if Skill.Flags.IsSpell(skill_id) and Skill.GetProfession(skill_id)[0] == 4:
                        match attr:
                            case a if 0 < a <= 1:
                                cost -= 1
                            case a if 2 <= a <= 4:
                                cost -= 2
                            case a if 5 <= a <= 7:
                                cost -= 3
                            case a if 8 <= a <= 10:
                                cost -= 4
                            case a if 11 <= a <= 13:
                                cost -= 5
                            case a if 14 <= a <= 16:
                                cost -= 6
                            case a if 17 <= a <= 19:
                                cost -= 7
                            case a if a > 19:
                                cost -= 8
                        continue

                case 310:  # Divine Spirit
                    if Skill.Flags.IsSpell(skill_id) and Skill.GetProfession(skill_id)[0] == 3:
                        cost -= 5
                    continue

                case 1569:  # Energizing Chorus
                    if Skill.Flags.IsChant(skill_id) or Skill.Flags.IsShout(skill_id):
                        match attr:
                            case a if 0 < a <= 1:
                                cost -= 3
                            case a if 2 <= a <= 5:
                                cost -= 4
                            case a if 6 <= a <= 9:
                                cost -= 5
                            case a if 10 <= a <= 13:
                                cost -= 6
                            case a if 14 <= a <= 16:
                                cost -= 7
                            case a if 17 <= a <= 20:
                                cost -= 8
                            case a if a > 20:
                                cost -= 9
                        continue

                case 474:  # Energizing Wind
                    if cost >= 15:
                        cost -= 15
                    else:
                        cost = 0
                    continue

                case 2145:  # Expert Focus
                    if Skill.Flags.IsAttack(skill_id) and Skill.Data.GetWeaponReq(skill_id) == 2:
                        match attr:
                            case a if 0 < a <= 7:
                                cost -= 1
                            case a if a > 8:
                                cost -= 2
                            

                case 199:  # Glyph of Energy
                    if Skill.Flags.IsSpell(skill_id):
                        if attr == 0:
                            cost -= 10
                        else:
                            cost -= (10 + attr)

                case 200:  # Glyph of Lesser Energy
                    if Skill.Flags.IsSpell(skill_id):
                        match attr:
                            case 0:
                                cost -= 10
                            case a if 1 <= a <= 2:
                                cost -= 11
                            case a if 3 <= a <= 4:
                                cost -= 12
                            case a if 5 <= a <= 6:
                                cost -= 13
                            case a if 7 <= a <= 8:
                                cost -= 14
                            case a if 9 <= a <= 10:
                                cost -= 15
                            case a if 11 <= a <= 12:
                                cost -= 16
                            case a if 13 <= a <= 14:
                                cost -= 17
                            case 15:
                                cost -= 18
                            case a if 16 <= a <= 16:
                                cost -= 19
                            case a if 17 <= a <= 18:
                                cost -= 20
                            case a if a >= 20:
                                cost -= 21

                case 1394:  # Healer's Covenant
                    if Skill.Flags.IsSpell(skill_id) and Skill.Attribute.GetAttribute(skill_id) == 15:
                        match attr:
                            case a if 0 < a <= 3:
                                cost -= 1
                            case a if 4 <= a <= 11:
                                cost -= 2
                            case a if 12 <= a <= 18:
                                cost -= 3
                            case a if a >= 19:
                                cost -= 4

                case 763:  # Jaundiced Gaze
                    if Skill.Flags.IsEnchantment(skill_id):
                        match attr:
                            case 0:
                                cost -= 1
                            case a if 1 <= a <= 2:
                                cost -= 2
                            case a if 3 <= a <= 4:
                                cost -= 3
                            case 5:
                                cost -= 4
                            case a if 6 <= a <= 7:
                                cost -= 5
                            case a if 8 <= a <= 9:
                                cost -= 6
                            case 10:
                                cost -= 7
                            case a if 11 <= a <= 12:
                                cost -= 8
                            case a if 13 <= a <= 14:
                                cost -= 9
                            case 15:
                                cost -= 10
                            case a if 16 <= a <= 17:
                                cost -= 11
                            case a if 18 <= a <= 19:
                                cost -= 12
                            case 20:
                                cost -= 13
                            case a if a > 20:
                                cost -= 14

                case 1739:  # Renewing Memories
                    if Skill.Flags.IsItemSpell(skill_id) or Skill.Flags.IsWeaponSpell(skill_id):
                        percentage = 5 + (attr * 2) if attr <= 20 else 47
                        cost -= cost * (percentage / 100)

                case 1240:  # Soul Twisting
                    if Skill.Flags.IsRitual(skill_id):
                        cost = 10  # Fixe le coût à 10

                case 987:  # Way of the Empty Palm
                    if Skill.Data.GetCombo(skill_id) == 2 or Skill.Data.GetCombo(skill_id) == 3:  # Attaque double ou secondaire
                        cost = 0

        cost = max(0, cost)
        return cost

    def HasEnoughAdrenaline(skill_slot):
        skill_id = SkillBar.GetSkillIDBySlot(skill_slot)
        player_agent_id = Player.GetAgentID()
        return Routines.Checks.Skills.HasEnoughAdrenaline(player_agent_id, skill_id)

    def HasEnoughEnergy(skill_slot):
        skill_id = SkillBar.GetSkillIDBySlot(skill_slot)
        player_agent_id = Player.GetAgentID()
        energy = Agent.GetEnergy(player_agent_id)
        max_energy = Agent.GetMaxEnergy(player_agent_id)
        energy_points = int(energy * max_energy)

        return Combat.GetEnergyAgentCost(skill_slot, player_agent_id) <= energy_points
    
    def HasEnoughEnergy(skill_slot):
        skill_id = SkillBar.GetSkillIDBySlot(skill_slot)
        player_agent_id = Player.GetAgentID()
        energy = Agent.GetEnergy(player_agent_id)
        max_energy = Agent.GetMaxEnergy(player_agent_id)
        energy_points = int(energy * max_energy)

        return Combat.GetEnergyAgentCost(skill_slot, player_agent_id) <= energy_points
    
    def IsSkillReady(skill_slot):
        skill_id = SkillBar.GetSkillIDBySlot(skill_slot)
        skill = SkillBar.GetSkillData(skill_slot)
        recharge = skill.recharge
        return recharge == 0
    
    def HasBuff(agent_id, skill_slot):
        skill_id = SkillBar.GetSkillIDBySlot(skill_slot)

        if Effects.BuffExists(agent_id, skill_id) or Effects.EffectExists(agent_id, skill_id):
            return True
        return False
    
    def GetAftercast(skill_slot):
        skill_id = SkillBar.GetSkillIDBySlot(skill_slot)

        activation = Skill.Data.GetActivation(skill_id)
        aftercast = Skill.Data.GetAftercast(skill_id)
        Py4GW.Console.Log("GetAftercast", f"Activation: {activation} + Aftercast: {aftercast}", Py4GW.Console.MessageType.Info)       
        return activation + aftercast + 100

# Explicitly expose the modified Movement class as your new class
Routines = ExtendedRoutines
Utils = ExtendedUtils