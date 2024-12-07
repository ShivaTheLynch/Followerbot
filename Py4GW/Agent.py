
import stat
from tkinter.filedialog import dialogstates
import Py4GW
import PyAgent
import PyPlayer

# Agent
class Agent:
    @staticmethod
    def agent_instance(agent_id):
        """
        Helper method to create and return a PyAgent instance.
        Args:
            agent_id (int): The ID of the agent to retrieve.
        Returns:
            PyAgent: The PyAgent instance for the given ID.
        """
        return PyAgent.PyAgent(agent_id)

    @staticmethod
    def GetIdFromAgent(agent_instance):
        """
        Purpose: Retrieve the ID of an agent.
        Args:
            agent_instance (PyAgent): The agent instance.
        Returns: int
        """
        return agent_instance.id

    @staticmethod
    def GetAgentByID(agent_id):
        """
        Purpose: Retrieve an agent by its ID.
        Args:
            agent_id (int): The ID of the agent to retrieve.
        Returns: PyAgent
        """
        return Agent.agent_instance(agent_id)

    @staticmethod
    def GetAttributes(agent_id):
        """
        Purpose: Retrieve the attributes of an agent.
        Args: agent_id (int): The ID of the agent.
        Returns: tuple
        """
        agent = Agent.agent_instance(agent_id)
        return agent.attributes

    @staticmethod
    def GetModelID(agent_id):
        """Retrieve the model of an agent."""
        return Agent.agent_instance(agent_id).model_id

    @staticmethod
    def IsLiving(agent_id):
        """Check if the agent is living."""
        return Agent.agent_instance(agent_id).is_living

    @staticmethod
    def IsItem(agent_id):
        """Check if the agent is an item."""
        return Agent.agent_instance(agent_id).is_item

    @staticmethod
    def IsGadget(agent_id):
        """Check if the agent is a gadget."""
        return Agent.agent_instance(agent_id).is_gadget

    @staticmethod
    def GetPlayerNumber(agent_id):
        """Retrieve the player number of an agent."""
        return Agent.agent_instance(agent_id).living_agent.player_number

    @staticmethod
    def GetLoginNumber(agent_id):
        """Retrieve the login number of an agent."""
        return Agent.agent_instance(agent_id).living_agent.login_number

    @staticmethod
    def IsSpirit(agent_id):
        """Check if the agent is a spirit."""
        return Agent.agent_instance(agent_id).living_agent.allegiance.GetName() == "Spirit/Pet"

    @staticmethod
    def IsMinion(agent_id):
        """Check if the agent is a minion."""
        return Agent.agent_instance(agent_id).living_agent.allegiance.GetName() == "Minion"

    @staticmethod
    def GetOwnerID(agent_id):
        """Retrieve the owner ID of an agent."""
        return Agent.agent_instance(agent_id).living_agent.owner_id

    @staticmethod
    def GetXY(agent_id):
        """
        Purpose: Retrieve the X and Y coordinates of an agent.
        Args: agent_id (int): The ID of the agent.
        Returns: tuple
        """
        agent = Agent.agent_instance(agent_id)
        return agent.x, agent.y

    @staticmethod
    def GetXYZ(agent_id):
        """
        Purpose: Retrieve the X, Y, and Z coordinates of an agent.
        Args: agent_id (int): The ID of the agent.
        Returns: tuple
        """
        agent = Agent.agent_instance(agent_id)
        return agent.x, agent.y, agent.z

    @staticmethod
    def GetZPlane(agent_id):
        """
        Purpose: Retrieve the Z plane of an agent.
        Args: agent_id (int): The ID of the agent.
        Returns: float
        """
        return Agent.agent_instance(agent_id).zplane

    @staticmethod
    def GetRotationAngle(agent_id):
        """
        Purpose: Retrieve the rotation angle of an agent.
        Args: agent_id (int): The ID of the agent.
        Returns: float
        """
        return Agent.agent_instance(agent_id).rotation_angle

    @staticmethod
    def GetRotationCos(agent_id):
        """
        Purpose: Retrieve the cosine of the rotation angle of an agent.
        Args: agent_id (int): The ID of the agent.
        Returns: float
        """
        return Agent.agent_instance(agent_id).rotation_cos

    @staticmethod
    def GetRotationSin(agent_id):
        """
        Purpose: Retrieve the sine of the rotation angle of an agent.
        Args: agent_id (int): The ID of the agent.
        Returns: float
        """
        return Agent.agent_instance(agent_id).rotation_sin

    @staticmethod
    def GetVelocityXY(agent_id):
        """
        Purpose: Retrieve the X and Y velocity of an agent.
        Args: agent_id (int): The ID of the agent.
        Returns: tuple
        """
        agent = Agent.agent_instance(agent_id)
        return agent.velocity_x, agent.velocity_y

    @staticmethod
    def GetName(agent_id):
        """Purpose: Get the name of an agent by its ID."""
        return Agent.agent_instance(agent_id).living_agent.name

    @staticmethod
    def GetProfessions(agent_id):
        """
        Purpose: Retrieve the player's primary and secondary professions.
        Args: agent_id (int): The ID of the agent.
        Returns: tuple
        """
        agent = Agent.agent_instance(agent_id)
        return agent.living_agent.profession, agent.living_agent.secondary_profession

    @staticmethod
    def GetProfessionNames(agent_id):
        """
        Purpose: Retrieve the names of the player's primary and secondary professions.
        Args: agent_id (int): The ID of the agent.
        Returns: tuple
        """
        agent = Agent.agent_instance(agent_id)
        return agent.living_agent.profession.GetName(), agent.living_agent.secondary_profession.GetName()

    @staticmethod
    def GetProfessionShortNames(agent_id):
        """
        Purpose: Retrieve the short names of the player's primary and secondary professions.
        Args: agent_id (int): The ID of the agent.
        Returns: tuple
        """
        agent = Agent.agent_instance(agent_id)
        return agent.living_agent.profession.GetShortName(), agent.living_agent.secondary_profession.GetShortName()

    @staticmethod
    def GetProfessionIDs(agent_id):
        """
        Purpose: Retrieve the IDs of the player's primary and secondary professions.
        Args: agent_id (int): The ID of the agent.
        Returns: tuple
        """
        agent = Agent.agent_instance(agent_id)
        return agent.living_agent.profession.ToInt(), agent.living_agent.secondary_profession.ToInt()

    @staticmethod
    def GetLevel(agent_id):
        """
        Purpose: Retrieve the level of the agent.
        Args: agent_id (int): The ID of the agent.
        Returns: int
        """
        return Agent.agent_instance(agent_id).living_agent.level

    @staticmethod
    def GetEnergy(agent_id):
        """
        Purpose: Retrieve the energy of the agent, only works for players and their heroes.
        Args: agent_id (int): The ID of the agent.
        Returns: float
        """
        return Agent.agent_instance(agent_id).living_agent.energy

    @staticmethod
    def GetMaxEnergy(agent_id):
        """
        Purpose: Retrieve the maximum energy of the agent, only works for players and heroes.
        Args: agent_id (int): The ID of the agent.
        Returns: int
        """
        return Agent.agent_instance(agent_id).living_agent.max_energy

    @staticmethod
    def GetEnergyRegen(agent_id):
        """
        Purpose: Retrieve the energy regeneration of the agent, only works for players and heroes.
        Args: agent_id (int): The ID of the agent.
        Returns: float
        """
        return Agent.agent_instance(agent_id).living_agent.energy_regen

    @staticmethod
    def GetHealth(agent_id):
        """
        Purpose: Retrieve the health of the agent.
        Args: agent_id (int): The ID of the agent.
        Returns: float
        """
        return Agent.agent_instance(agent_id).living_agent.hp

    @staticmethod
    def GetMaxHealth(agent_id):
        """
        Purpose: Retrieve the maximum health of the agent.
        Args: agent_id (int): The ID of the agent.
        Returns: int
        """
        return Agent.agent_instance(agent_id).living_agent.max_hp

    @staticmethod
    def GetHealthRegen(agent_id):
        """
        Purpose: Retrieve the health regeneration of the agent.
        Args: agent_id (int): The ID of the agent.
        Returns: float
        """
        return Agent.agent_instance(agent_id).living_agent.hp_regen

    @staticmethod
    def IsMoving(agent_id):
        """Purpose: Check if the agent is moving."""
        return Agent.agent_instance(agent_id).living_agent.is_moving

    @staticmethod
    def IsKnockedDown(agent_id):
        """Check if the agent is knocked down."""
        return Agent.agent_instance(agent_id).living_agent.is_knocked_down

    @staticmethod
    def IsBleeding(agent_id):
        """Check if the agent is bleeding."""
        return Agent.agent_instance(agent_id).living_agent.is_bleeding

    @staticmethod
    def IsCrippled(agent_id):
        """Check if the agent is crippled."""
        return Agent.agent_instance(agent_id).living_agent.is_crippled

    @staticmethod
    def IsDeepWounded(agent_id):
        """Check if the agent is deep wounded."""
        return Agent.agent_instance(agent_id).living_agent.is_deep_wounded

    @staticmethod
    def IsPoisoned(agent_id):
        """Check if the agent is poisoned."""
        return Agent.agent_instance(agent_id).living_agent.is_poisoned

    @staticmethod
    def IsConditioned(agent_id):
        """Check if the agent is conditioned."""
        return Agent.agent_instance(agent_id).living_agent.is_conditioned

    @staticmethod
    def IsEnchanted(agent_id):
        """Check if the agent is enchanted."""
        return Agent.agent_instance(agent_id).living_agent.is_enchanted

    @staticmethod
    def IsHexed(agent_id):
        """Check if the agent is hexed."""
        return Agent.agent_instance(agent_id).living_agent.is_hexed

    @staticmethod
    def IsDegenHexed(agent_id):
        """Check if the agent is degen hexed."""
        return Agent.agent_instance(agent_id).living_agent.is_degen_hexed

    @staticmethod
    def IsDead(agent_id):
        """Check if the agent is dead."""
        return Agent.agent_instance(agent_id).living_agent.is_dead

    @staticmethod
    def IsAlive(agent_id):
        """Check if the agent is alive."""
        return not Agent.IsDead(agent_id)

    @staticmethod
    def IsWeaponSpelled(agent_id):
        """Check if the agent's weapon is spelled."""
        return Agent.agent_instance(agent_id).living_agent.is_weapon_spelled

    @staticmethod
    def IsInCombatStance(agent_id):
        """Check if the agent is in combat stance."""
        return Agent.agent_instance(agent_id).living_agent.in_combat_stance

    @staticmethod
    def IsAttacking(agent_id):
        """Check if the agent is attacking."""
        return Agent.agent_instance(agent_id).living_agent.is_attacking

    @staticmethod
    def IsCasting(agent_id):
        """Check if the agent is casting."""
        return Agent.agent_instance(agent_id).living_agent.is_casting

    @staticmethod
    def IsIdle(agent_id):
        """Check if the agent is idle."""
        return Agent.agent_instance(agent_id).living_agent.is_idle

    @staticmethod
    def HasBossGlow(agent_id):
        """Check if the agent has a boss glow."""
        return Agent.agent_instance(agent_id).living_agent.has_boss_glow


    @staticmethod
    def GetWeaponType(agent_id):
        """Purpose: Retrieve the weapon type of the agent."""
        return Agent.agent_instance(agent_id).living_agent.weapon_type.ToInt(), Agent.agent_instance(agent_id).living_agent.weapon_type.GetName()

    @staticmethod
    def GetWeaponExtraData(agent_id):
        """
        Purpose: Retrieve the weapon extra data of the agent.
        Args: agent_id (int): The ID of the agent.
        Returns: tuple
        """
        agent = Agent.agent_instance(agent_id)
        return agent.living_agent.weapon_item_id, agent.living_agent.weapon_item_type,  agent.living_agent.offhand_item_id, agent.living_agent.offhand_item_type

    @staticmethod
    def IsMartial(agent_id):
        """
        Purpose: Check if the agent is martial.
        Args: agent_id (int): The ID of the agent.
        Returns: bool
        """
        martial_weapon_types = ["Bow", "Axe", "Hammer", "Daggers", "Scythe", "Spear", "Sword"]
        return Agent.agent_instance(agent_id).living_agent.weapon_type.GetName() in martial_weapon_types

    @staticmethod
    def IsCaster(agent_id):
        """
        Purpose: Check if the agent is a caster.
        Args: agent_id (int): The ID of the agent.
        Returns: bool
        """
        return not Agent.IsMartial(agent_id)

    @staticmethod
    def IsMelee(agent_id):
        """
        Purpose: Check if the agent is melee.
        Args: agent_id (int): The ID of the agent.
        Returns: bool
        """
        melee_weapon_types = ["Axe", "Hammer", "Daggers", "Scythe", "Sword"]
        return Agent.agent_instance(agent_id).living_agent.weapon_type.GetName() in melee_weapon_types

    @staticmethod
    def IsRanged(agent_id):
        """
        Purpose: Check if the agent is ranged.
        Args: agent_id (int): The ID of the agent.
        Returns: bool
        """
        return not Agent.IsMelee(agent_id)

    @staticmethod
    def GetCastingSkill(agent_id):
        """ Purpose: Retrieve the casting skill of the agent."""
        return Agent.agent_instance(agent_id).living_agent.casting_skill_id

    @staticmethod
    def GetDaggerStatus(agent_id):
        """Purpose: Retrieve the dagger status of the agent."""
        return Agent.agent_instance(agent_id).living_agent.dagger_status

    @staticmethod
    def GetAlliegance(agent_id):
        """Purpose: Retrieve the allegiance of the agent."""
        return  Agent.agent_instance(agent_id).living_agent.allegiance.ToInt(), Agent.agent_instance(agent_id).living_agent.allegiance.GetName()

    @staticmethod
    def IsPlayer(agent_id):
        """Check if the agent is a player."""
        return Agent.agent_instance(agent_id).living_agent.is_player

    @staticmethod
    def IsNPC(agent_id):
        """Check if the agent is an NPC."""
        return Agent.agent_instance(agent_id).living_agent.is_npc

    @staticmethod
    def HasQuest(agent_id):
        """Check if the agent has a quest."""
        return Agent.agent_instance(agent_id).living_agent.has_quest

    @staticmethod
    def IsDeadByTypeMap(agent_id):
        """Check if the agent is dead by type map."""
        return Agent.agent_instance(agent_id).living_agent.is_dead_by_typemap

    @staticmethod
    def IsFemale(agent_id):
        """Check if the agent is female."""
        return Agent.agent_instance(agent_id).living_agent.is_female

    @staticmethod
    def IsHidingCape(agent_id):
        """Check if the agent is hiding the cape."""
        return Agent.agent_instance(agent_id).living_agent.is_hiding_cape

    @staticmethod
    def CanBeViewedInPartyWindow(agent_id):
        """Check if the agent can be viewed in the party window."""
        return Agent.agent_instance(agent_id).living_agent.can_be_viewed_in_party_window

    @staticmethod
    def IsSpawned(agent_id):
        """Check if the agent is spawned."""
        return Agent.agent_instance(agent_id).living_agent.is_spawned

    @staticmethod
    def IsBeingObserved(agent_id):
        """Check if the agent is being observed."""
        return Agent.agent_instance(agent_id).living_agent.is_being_observed

    @staticmethod
    def GetOvercast(agent_id):
        """Retrieve the overcast of the agent."""
        return Agent.agent_instance(agent_id).living_agent.overcast

    @staticmethod
    def GetItemAgent(agent_id):
        """Retrieve the item agent of the agent."""
        return Agent.agent_instance(agent_id).item_agent

    @staticmethod
    def GetGadgetAgent(agent_id):
        """Retrieve the gadget agent of the agent."""
        return Agent.agent_instance(agent_id).gadget_agent

    @staticmethod
    def GetGadgetID(agent_id):
        """Retrieve the gadget ID of the agent."""
        gadget_agent = Agent.GetGadgetAgent(agent_id)
        return gadget_agent.gadget_id














