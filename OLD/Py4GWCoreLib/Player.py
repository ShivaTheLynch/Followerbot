import Py4GW
import PyPlayer

from .Map import *
from .Agent import *
# Player
class Player:
    @staticmethod
    @staticmethod
    def player_instance():
        """
        Helper method to create and return a PyPlayer instance.
        Args:
            None
        Returns:
            PyAgent: The PyAgent instance for the given ID.
        """
        return PyPlayer.PyPlayer()

    @staticmethod
    def GetAgentID():
        """
        Purpose: Retrieve the agent ID of the player.
        Args: None
        Returns: int
        """
        return Player.player_instance().id

    @staticmethod
    def GetName():
        """
        Purpose: Retrieve the player's name.
        Args: None
        Returns: str
        """
        return Agent.GetName(Player.GetAgentID())

    @staticmethod
    def GetXY():
        """
        Purpose: Retrieve the player's current X and Y coordinates.
        Args: None
        Returns: tuple (x, y)
        """
        return Agent.GetXY(Player.GetAgentID())

    
    @staticmethod
    def GetTargetID():
        """
        Purpose: Retrieve the ID of the player's target.
        Args: None
        Returns: int
        """
        return Player.player_instance().target_id

    @staticmethod
    def GetAgent():
        """
        Purpose: Retrieve the player's agent.
        Args: None
        Returns: PyAgent
        """
        return Player.player_instance().agent

    @staticmethod
    def GetMouseOverID():
        """
        Purpose: Retrieve the ID of the agent the mouse is currently over.
        Args: None
        Returns: int
        """
        return Player.player_instance().mouse_over_id

    @staticmethod
    def GetObservingID():
        """
        Purpose: Retrieve the ID of the agent the player is observing.
        Args: None
        Returns: int
        """
        return Player.player_instance().observing_id

    @staticmethod
    def SendDialog(dialog_id):
        """
        Purpose: Send a dialog response.
        Args:
            dialog_id (int): The ID of the dialog.
        Returns: None
        """
        Player.player_instance().SendDialog(dialog_id)

    @staticmethod
    def SendChatCommand(command):
        """
        Purpose: Send a '/' chat command.
        Args:
            command (str): The command to send.
        Returns: None
        """
        Player.player_instance().SendChatCommand(command)

    @staticmethod
    def SendChat(channel, message):
        """
        Purpose: Send a chat message to a channel.
        Args:
            channel (char): The channel to send the message to.
            message (str): The message to send.
        Returns: None
        """
        Player.player_instance().SendChat(channel, message)

    @staticmethod
    def SendWhisper(target_name, message):
        """
        Purpose: Send a whisper to a target player.
        Args:
            target_name (str): The name of the target player.
            message (str): The message to send.
        Returns: None
        """
        Player.player_instance().SendWhisper(target_name, message)

    @staticmethod
    def ChangeTarget (agent_id):
        """
        Purpose: Change the player's target.
        Args:
            agent_id (int): The ID of the agent to target.
        Returns: None
        """
        Player.player_instance().ChangeTarget(agent_id)
               
    @staticmethod
    def Interact(agent_id, call_target=False):
        """
        Purpose: Interact with an agent.
        Args:
            agent_id (int): The ID of the agent to interact with.
            call_target (bool, optional): Whether to call the agent as a target.
        Returns: None
        """
        Player.player_instance().InteractAgent(agent_id, call_target)

    @staticmethod
    def OpenLockedChest(use_key=False):
        """
        Purpose: Open a locked chest. This function is no longer available from toolbox!!
        Args:
            use_key (bool): Whether to use a key to open the chest.
        Returns: None
        """
        #This function is no longer available from toolbox!!
        Player.player_instance().OpenLockedChest(use_key)

    @staticmethod
    def Move(x, y):
        """
        Purpose: Move the player to specified X and Y coordinates.
        Args:
            x (float): X coordinate.
            y (float): Y coordinate.
        Returns: None
        """
        Player.player_instance().Move(x, y)

    @staticmethod
    def MoveXYZ(x, y, zindex=1):
        """
        Purpose: Move the player to specified X and Y coordinates.
        Args:
            x (float): X coordinate.
            y (float): Y coordinate.
        Returns: None
        """
        Player.player_instance().Move(x, y, zindex)

    @staticmethod
    def CancelMove():
        """
        Purpose: Cancel the player's current move action.
        Args: None
        Returns: None
        """
        player_agent = Player.GetAgent()
        if Map.IsMapReady():
            Player.player_instance().Move(player_agent.x, player_agent.y)


