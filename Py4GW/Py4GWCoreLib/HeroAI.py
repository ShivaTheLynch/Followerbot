import PyHeroAI

class HeroAI:
    def __init__(self):
        self.hero_ai_instance = PyHeroAI.PyHeroAI()

    def GetAIEnabled(self):
        """
        Purpose: gets the status of the AI motor.
        Args:
            None
        Returns: Boolean
        """
        return self.hero_ai_instance.GetAIEnabled()

    def SetAIEnabled(self,value):
        """
        Purpose: sets the status of the AI motor.
        Args:
            value: Boolean
        Returns: None
        """
        self.hero_ai_instance.SetAIEnabled(value)

    def GetMyPartyPos(self):
        """
        Purpose: gets the party position of the AI player.
        Args:
            None
        Returns: int
        """
        return self.hero_ai_instance.GetMyPartyPos()

    def IsActive(self, party_pos):
        """
        Purpose: gets the status of the AI player in party position.
        Args:
            party_pos: int
        Returns: Boolean
        """
        return self.hero_ai_instance.IsActive(party_pos)

    def GetLootingStatus(self, party_pos):
        """
        Purpose: gets the looting status of the party member
        Args:
            None
        Returns: Boolean
        """
        return self.hero_ai_instance.GetLooting(party_pos)

    def SetLootingStatus(self, party_pos, value):
        """
        Purpose: sets the looting status of the party member
        Args:
            party_pos: int
            value: Boolean
        Returns: None
        """
        self.hero_ai_instance.SetLooting(party_pos, value)

    def GetFollowingStatus(self, party_pos):
        """
        Purpose: gets the following status of the party member
        Args:
            None
        Returns: Boolean
        """
        return self.hero_ai_instance.GetFollowing(party_pos)

    def SetFollowingStatus(self,party_pos, value):
        """
        Purpose: sets the folowing status of the party member
        Args:
            party_pos: int
            value: Boolean
        Returns: None
        """
        self.hero_ai_instance.SetFollowing(party_pos, value)

    def GetCombatStatus(self,party_pos):
        """
        Purpose: gets the combat status of the party member
        Args:
            None
        Returns: Boolean
        """
        return self.hero_ai_instance.GetCombat(party_pos)

    def SetCombatStatus(self, party_pos, value):
        """
        Purpose: sets the combat status of the party member
        Args:
            party_pos: int
            value: Boolean
        Returns: None
        """
        self.hero_ai_instance.SetCombat(party_pos, value)

    def GetCollisionStatus(self,party_pos):
        """
        Purpose: gets the collision status of the party member
        Args:
            None
        Returns: Boolean
        """
        return self.hero_ai_instance.GetCollision(party_pos)

    def SetCollisionStatus(self, party_pos, value):
        """
        Purpose: sets the collision status of the party member
        Args:
            party_pos: int
            value: Boolean
        Returns: None
        """
        HeroAI.hero_ai_instance.SetCollision(party_pos, value)

    def GetTargettingStatus(self, party_pos):
        """
        Purpose: gets the targetting status of the party member
        Args:
            None
        Returns: Boolean
        """
        return self.hero_ai_instance.GetTargetting(party_pos)

    def GetSkillStatus(self, party_pos,skill_pos):
        """
        Purpose: gets the skill status of the party member
        Args:
            None
        Returns: Boolean
        """
        return self.hero_ai_instance.GetSkill(party_pos,skill_pos)

    def SetSkillStatus(self, party_pos,skill_pos, value):
        """
        Purpose: sets the skill status of the party member
        Args:
            party_pos: int
            value: Boolean
        Returns: None
        """
        self.hero_ai_instance.SetSkill(party_pos,skill_pos, value)

    def FlagAIHero(self, party_pos, x:float, y:float):
        """
        Args:
            party_pos: int
            x: float
            y: float
        Returns: None
        """
        self.hero_ai_instance.FlagAIHero(party_pos, x, y)

    def UnFlagAIHero(self,party_pos):
        """
        Args:
            party_pos: int
        Returns: None
        """
        self.hero_ai_instance.UnFlagAIHero(party_pos)

    def GetEnergy(self, party_pos):
        """
        Purpose: gets the energy status of the party member
        Args:
            None
        Returns: Float
        """
        return self.hero_ai_instance.GetEnergy(party_pos)

    def GetEnergyRegen(self, party_pos):
        """
        Purpose: gets the status of energy regen of the party member
        Args:
            None
        Returns: Float
        """
        return self.hero_ai_instance.GetEnergyRegen(party_pos)

    def GetAgentID(self, party_pos):
        """
        Purpose: gets the status of the party member
        Args:
            None
        Returns: int
        """
        return self.hero_ai_instance.GetAgentID(party_pos)

    def Resign(self, party_pos):
        """
        Purpose: send resign command to the party member
        Args:
            None
        Returns: None
        """
        self.hero_ai_instance.Resign(party_pos)
        
    def TakeQuest(self, party_pos, dialog=0):
        """
        Purpose: talks with an npc and gets a dialog
        Args:
            None
        Returns: None
        """
        self.hero_ai_instance.TakeQuest(party_pos, dialog)

    def Identify(self, party_pos):
        """
        Purpose: seld identify command to the party member
        Args:
            None
        Returns: None
        """
        self.hero_ai_instance.Identify(party_pos)

    def Salvage(self,party_pos):
        """
        Purpose: send salvage command to the party member
        Args:
            None
        Returns: None
        """
        self.hero_ai_instance.Salvage(party_pos)