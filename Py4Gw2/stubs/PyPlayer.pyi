# PyPlayer.pyi - Auto-generated .pyi file for PyPlayer module

from typing import Any, List

# Class PyPlayer
class PyPlayer:
    id: int
    agent: Any
    target_id: int
    mouse_over_id: int
    amount_of_players_in_instance: int

    def __init__(self) -> None: ...

    def GetContext(self) -> None: ...
    def GetAgentArray(self) -> List[Any]: ...
    def GetAllyArray(self) -> List[Any]: ...
    def GetNeutralArray(self) -> List[Any]: ...
    def GetEnemyArray(self) -> List[Any]: ...
    def GetSpiritPetArray(self) -> List[Any]: ...
    def GetMinionArray(self) -> List[Any]: ...
    def GetNPCMinipetArray(self) -> List[Any]: ...
    def GetItemArray(self) -> List[Any]: ...
    def GetGadgetArray(self) -> List[Any]: ...
    def SendChatCommand(self, msg: str) -> None: ...
    def ChangeTarget(self, target_id: int) -> None: ...
    def Move(self, x: float, y: float, zplane: int) -> None: ...
    def Move(self, x: float, y: float) -> None: ...
    def InteractAgent(self, agent_id: int, call_target: bool) -> None: ...
    def OpenLockedChest(self, use_key: bool) -> None: ...
