from Py4GWCoreLib import *
from Py4GWCoreLib.Skillbar import SkillBar
from Py4GWCoreLib.Agent import Agent
import time

module_name = "Spiker Follower"

# Add this near the top with other global variables
is_following = False
is_attacking = False
start_time = 0
map_entry_time = time.time()  # New variable to track map time
last_map_id = Map.GetMapID()  # Track map changes
global current_skill_slot
current_skill_slot = 0

class GameAreas:
    def __init__(self):
        self.Touch = 144
        self.Adjacent = 166
        self.Nearby = 252
        self.Area = 322
        self.Earshot = 1012  #aggro bubble
        self.Spellcast = 1248
        self.Spirit = 2500
        self.Compass = 5000

follow_distance = GameAreas().Area

checkbox_state = True

def DisplaySkillInfo():
    """Display skill information in a separate tab."""
    if PyImGui.begin_tab_item("Skills"):
        PyImGui.text("Current Skillbar:")
        PyImGui.separator()
        
        for slot in range(1, 9):  # Skills 1-8
            skill_id = SkillBar.GetSkillIDBySlot(slot)
            if skill_id:
                skill_name = Skill.GetName(skill_id)
                energy_cost = get_energy_cost(skill_id)
                PyImGui.text(f"Skill {slot}: [{skill_id}] {skill_name} (Energy: {energy_cost})")
            else:
                PyImGui.text(f"Skill {slot}: Empty")
        
        PyImGui.end_tab_item()

def DisplayInfoTab():
    """Display general information in a separate tab."""
    global map_entry_time, last_map_id
    
    # Check if map changed
    current_map = Map.GetMapID()
    if current_map != last_map_id:
        map_entry_time = time.time()
        last_map_id = current_map
    
    if PyImGui.begin_tab_item("Info"):
        # Time Information Section
        PyImGui.text("=== Time Information ===")
        PyImGui.indent(10)
        
        # Bot Runtime
        if is_following or is_attacking:
            bot_time = time.time() - start_time
            bot_hours = int(bot_time // 3600)
            bot_minutes = int((bot_time % 3600) // 60)
            bot_seconds = int(bot_time % 60)
            PyImGui.text(f"Bot Runtime: {bot_hours:02d}:{bot_minutes:02d}:{bot_seconds:02d}")
        else:
            PyImGui.text("Bot Runtime: Not Running")
            
        # Map Time
        map_time = time.time() - map_entry_time
        map_hours = int(map_time // 3600)
        map_minutes = int((map_time % 3600) // 60)
        map_seconds = int(map_time % 60)
        PyImGui.text(f"Time in Map: {map_hours:02d}:{map_minutes:02d}:{map_seconds:02d}")
        PyImGui.unindent(10)
        
        PyImGui.spacing()
        PyImGui.separator()
        PyImGui.spacing()
        
        # Map Information Section
        PyImGui.text("=== Map Information ===")
        PyImGui.indent(10)
        map_name = Map.GetMapName(current_map)
        PyImGui.text(f"Map ID: {current_map}")
        PyImGui.text(f"Name:   {map_name}")
        PyImGui.unindent(10)
        
        PyImGui.spacing()
        PyImGui.separator()
        PyImGui.spacing()
        
        # Player Information Section
        PyImGui.text("=== Player Information ===")
        PyImGui.indent(10)
        player_id = Player.GetAgentID()
        x, y = Agent.GetXY(player_id)
        PyImGui.text(f"Position:")
        PyImGui.indent(20)
        PyImGui.text(f"X: {x:.2f}")
        PyImGui.text(f"Y: {y:.2f}")
        PyImGui.unindent(20)
        PyImGui.unindent(10)
        
        PyImGui.spacing()
        PyImGui.separator()
        PyImGui.spacing()
        
        # Called Targets Section
        PyImGui.text("=== Called Targets ===")
        PyImGui.indent(10)
        players = Party.GetPlayers()
        has_called_targets = False
        for player in players:
            if player.called_target_id != 0:
                has_called_targets = True
                PyImGui.text(f"Player {player.login_number} → Target {player.called_target_id}")
        if not has_called_targets:
            PyImGui.text("No active called targets")
        PyImGui.unindent(10)
        
        PyImGui.end_tab_item()

def DisplayTeamStats():
    """Display team statistics in a separate tab."""
    if PyImGui.begin_tab_item("Team Stats"):
        PyImGui.text("=== Team Members ===")
        PyImGui.indent(10)
        
        # Get all allies from the agent array
        try:
            agent_array = AgentArray.GetAllyArray()  # Updated to use GetAllyArray()
            if not agent_array:
                Py4GW.Console.Log("Follower", "GetAllyArray returned an empty or invalid result.", Py4GW.Console.MessageType.Warning)
            else:
                for agent_id in agent_array:
                    name = Agent.GetName(agent_id)
                    hp = Agent.GetHealth(agent_id)
                    max_hp = Agent.GetMaxHealth(agent_id)
                    energy = Agent.GetEnergy(agent_id)
                    max_energy = Agent.GetMaxEnergy(agent_id)
                    
                    # Determine if the agent is a player or hero
                    if Party.Players.GetLoginNumberByAgentID(agent_id) != 0:
                        agent_type = "Player"
                    elif Party.Heroes.GetHeroIDByAgentID(agent_id) != 0:
                        agent_type = "Hero"
                        hero_id = Party.Heroes.GetHeroIDByAgentID(agent_id)
                        name = Party.Heroes.GetHeroNameById(hero_id)  # Get hero name
                    else:
                        agent_type = "Unknown"
                    
                    # Calculate actual HP and energy values
                    current_hp = int(hp * max_hp)
                    max_hp_value = int(max_hp)
                    current_energy = int(energy * max_energy)
                    max_energy_value = int(max_energy)
                    
                    PyImGui.text(f"{agent_type}: {name}")
                    PyImGui.indent(20)
                    PyImGui.text(f"HP: {current_hp}/{max_hp_value}")
                    PyImGui.text(f"Energy: {current_energy}/{max_energy_value}")
                    PyImGui.unindent(20)
                    PyImGui.spacing()
        except Exception as e:
            Py4GW.Console.Log("Follower", f"Error retrieving ally array: {str(e)}", Py4GW.Console.MessageType.Error)
        
        PyImGui.unindent(10)
        PyImGui.end_tab_item()

def DisplayPlayerStats():
    """Display player statistics in a separate tab."""
    global current_skill_slot
    
    if PyImGui.begin_tab_item("Player Stats"):
        PyImGui.text("=== Player Statistics ===")
        PyImGui.indent(10)
        
        # Get player information
        player_id = Player.GetAgentID()
        name = Agent.GetName(player_id)
        hp = Agent.GetHealth(player_id)
        max_hp = Agent.GetMaxHealth(player_id)
        energy = Agent.GetEnergy(player_id)
        max_energy = Agent.GetMaxEnergy(player_id)
        
        # Calculate actual HP and energy values
        current_hp = int(hp * max_hp)
        max_hp_value = int(max_hp)
        current_energy = int(energy * max_energy)
        max_energy_value = int(max_energy)
        
        # Display player stats
        PyImGui.text(f"Name: {name}")
        PyImGui.text(f"HP: {current_hp}/{max_hp_value}")
        PyImGui.text(f"Energy: {current_energy}/{max_energy_value}")
        
        # Debug output
        PyImGui.text(f"Debug - Current Skill Slot: {current_skill_slot}")
        
        # Display actual current/last used skill
        if current_skill_slot > 0 and current_skill_slot <= 8:
            skill_id = SkillBar.GetSkillIDBySlot(current_skill_slot)
            if skill_id:
                skill_name = Skill.GetName(skill_id)
                PyImGui.text(f"Current/Last Used Skill:")
                PyImGui.indent(20)
                PyImGui.text(f"Slot: {current_skill_slot}")
                PyImGui.text(f"ID: {skill_id}")
                PyImGui.text(f"Name: {skill_name}")
                PyImGui.unindent(20)
        else:
            PyImGui.text("No skill currently active")
        
        PyImGui.unindent(10)
        PyImGui.end_tab_item()

def DrawWindow():
    global checkbox_state, is_following, is_attacking, start_time

    if PyImGui.begin("Following/Fighting bot"):
        if PyImGui.begin_tab_bar("TabBar"):
            if PyImGui.begin_tab_item("Main"):
                # Title and Credits Section
                PyImGui.text("=== Follow/Fight Bot ===")
                PyImGui.text("Credits: Shiva,Apo and Disasterus")
                PyImGui.separator()

                # Status Section
                PyImGui.text("Status:")
                if is_following:
                    elapsed_time = time.time() - start_time
                    hours = int(elapsed_time // 3600)
                    minutes = int((elapsed_time % 3600) // 60)
                    seconds = int(elapsed_time % 60)
                    PyImGui.text(f"Following time: {hours:02d}:{minutes:02d}:{seconds:02d}")
                    PyImGui.text("Follower Status: Active")
                else:
                    PyImGui.text("Follower Status: Inactive")
                
                if is_attacking:
                    PyImGui.text("Attack Status: Active")
                else:
                    PyImGui.text("Attack Status: Inactive")
                PyImGui.separator()

                # Control Buttons
                if not is_following:
                    if PyImGui.button("Start Following"):
                        is_following = True
                        start_time = time.time()
                        runfollower()
                        Py4GW.Console.Log("Follower", "Follow the leader!", Py4GW.Console.MessageType.Info)
                else:
                    if PyImGui.button("Stop Following"):
                        is_following = False
                        Py4GW.Console.Log("Follower", "Stopped following.", Py4GW.Console.MessageType.Info)

                PyImGui.separator()

                if not is_attacking:
                    if PyImGui.button("Start Attacking"):
                        is_attacking = True
                        start_time = time.time()
                        runbot()
                        Py4GW.Console.Log("Follower", "Started attacking!", Py4GW.Console.MessageType.Info)
                else:
                    if PyImGui.button("Stop Attacking"):
                        is_attacking = False
                        Py4GW.Console.Log("Follower", "Stopped attacking.", Py4GW.Console.MessageType.Info)

                PyImGui.end_tab_item()
            
            DisplaySkillInfo()   # Skills tab
            DisplayInfoTab()     # Info tab
            DisplayTeamStats()   # Team stats tab
            DisplayPlayerStats() # Player stats tab
            
            PyImGui.end_tab_bar()
    PyImGui.end()


def GetEnergyAgentCost(skill_id, agent_id):
    """Retrieve the actual energy cost of a skill by its ID and effects.

    Args:
        skill_id (int): ID of the skill.
        agent_id (int): ID of the agent (player or hero).

    Returns:
        float: Final energy cost after applying all effects.
              Values are rounded to integers.
              Minimum cost is 0 unless otherwise specified by an effect.
    """
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

def get_energy_cost(skill_id):
    player_agent_id = Player.GetAgentID()
    return GetEnergyAgentCost(skill_id, player_agent_id)    

def HasEnoughEnergy(skill_id):
    player_agent_id = Player.GetAgentID()
    energy = Agent.GetEnergy(player_agent_id)
    max_energy = Agent.GetMaxEnergy(player_agent_id)
    energy_points = int(energy * max_energy)

    return GetEnergyAgentCost(skill_id, player_agent_id) <= energy_points

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

def runbot():
    global module_name, follow_distance, is_following, current_skill_slot
    try:
            if Party.IsPartyLoaded():
                leader_id = Party.GetPartyLeaderID()
                my_id = Player.GetAgentID()

                if my_id != leader_id:
                    leader_x, leader_y = Agent.GetXY(leader_id)
                    my_x, my_y = Agent.GetXY(my_id)

                    # Check for called target first
                    called_target = get_called_target()
                    
                    # If there's a called target, prioritize it
                    if called_target:
                        Player.ChangeTarget(called_target)
                    else:
                        # Fallback to original enemy targeting logic
                        enemy_array = AgentArray.GetEnemyArray()
                        enemy_array = AgentArray.Filter.ByDistance(enemy_array, (my_x, my_y), GameAreas().Spellcast)
                        enemy_array = AgentArray.Filter.ByAttribute(enemy_array, 'IsAlive')

                        if len(enemy_array) > 0:
                            not_hexed_array = AgentArray.Filter.ByAttribute(enemy_array, 'IsHexed', negate=True)
                            if len(not_hexed_array) > 0:
                                Player.ChangeTarget(not_hexed_array[0])
                            
                            # Use skills with time-based checks
                            current_time = time.time()
                            skill_number = int((current_time % 16) / 2) + 1  # Cycles through skills 1-8 every 2 seconds
                            if skill_number <= 8:  # Safety check
                                skill_id = SkillBar.GetSkillIDBySlot(skill_number)
                                if skill_id and IsSkillReady2(skill_number) and HasEnoughEnergy(skill_id):
                                    Py4GW.Console.Log("Follower", f"Using skill {skill_number} (ID: {skill_id})", Py4GW.Console.MessageType.Info)
                                    current_skill_slot = skill_number
                                    SkillBar.UseSkill(skill_number)
                            return
                    # If no enemies or after combat, follow leader if too far
                    distance = Utils.Distance((leader_x, leader_y), (my_x, my_y))
                    if distance > follow_distance:
                        Player.Interact(leader_id)


    except ImportError as e:
        Py4GW.Console.Log(module_name, f"ImportError encountered: {str(e)}", Py4GW.Console.MessageType.Error)
        Py4GW.Console.Log(module_name, f"Stack trace: {traceback.format_exc()}", Py4GW.Console.MessageType.Error)
    except ValueError as e:
        Py4GW.Console.Log(module_name, f"ValueError encountered: {str(e)}", Py4GW.Console.MessageType.Error)
        Py4GW.Console.Log(module_name, f"Stack trace: {traceback.format_exc()}", Py4GW.Console.MessageType.Error)
    except TypeError as e:
        Py4GW.Console.Log(module_name, f"TypeError encountered: {str(e)}", Py4GW.Console.MessageType.Error)
        Py4GW.Console.Log(module_name, f"Stack trace: {traceback.format_exc()}", Py4GW.Console.MessageType.Error)
    except Exception as e:
        Py4GW.Console.Log(module_name, f"Unexpected error encountered: {str(e)}", Py4GW.Console.MessageType.Error)
        Py4GW.Console.Log(module_name, f"Stack trace: {traceback.format_exc()}", Py4GW.Console.MessageType.Error)
    finally:
        pass

def runfollower():
    global module_name, follow_distance, is_following, is_attacking
    try:
            if Party.IsPartyLoaded():
                leader_id = Party.GetPartyLeaderID()
                my_id = Player.GetAgentID()

                if my_id != leader_id:
                    leader_x, leader_y = Agent.GetXY(leader_id)
                    my_x, my_y = Agent.GetXY(my_id)


                    # Follow leader if too far
                    distance = Utils.Distance((leader_x, leader_y), (my_x, my_y))
                    if distance > follow_distance:
                        Player.Interact(leader_id)
    except ImportError as e:
        Py4GW.Console.Log(module_name, f"ImportError encountered: {str(e)}", Py4GW.Console.MessageType.Error)
        Py4GW.Console.Log(module_name, f"Stack trace: {traceback.format_exc()}", Py4GW.Console.MessageType.Error)
    except ValueError as e:
        Py4GW.Console.Log(module_name, f"ValueError encountered: {str(e)}", Py4GW.Console.MessageType.Error)
        Py4GW.Console.Log(module_name, f"Stack trace: {traceback.format_exc()}", Py4GW.Console.MessageType.Error)
    except TypeError as e:
        Py4GW.Console.Log(module_name, f"TypeError encountered: {str(e)}", Py4GW.Console.MessageType.Error)
        Py4GW.Console.Log(module_name, f"Stack trace: {traceback.format_exc()}", Py4GW.Console.MessageType.Error)
    except Exception as e:
        Py4GW.Console.Log(module_name, f"Unexpected error encountered: {str(e)}", Py4GW.Console.MessageType.Error)
        Py4GW.Console.Log(module_name, f"Stack trace: {traceback.format_exc()}", Py4GW.Console.MessageType.Error)
    finally:
        pass

def main():
    DrawWindow()
    if is_following:
        runfollower()
    if is_attacking:
        runbot()

# This ensures that Main() is called when the script is executed directly.
if __name__ == "__main__":
    main()

