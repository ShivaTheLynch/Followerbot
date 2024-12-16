from Py4GWCoreLib import *

module_name = "HeroAI"

class window_control_class:
    def __init__(self):
        self.is_active = False
        self.Following = False
        self.Collision = False
        self.Looting = False
        self.Targetting = False
        self.Combat = False
        self.skills = [False,False,False,False,False,False,False,False,False]

    def Update(self, own_party_pos):
        self.is_active = Py4GW.HeroAI.IsActive(own_party_pos)
        self.Following = Py4GW.HeroAI.GetFollowing(own_party_pos)
        self.Collision = Py4GW.HeroAI.GetCollision(own_party_pos)
        self.Looting = Py4GW.HeroAI.GetLooting(own_party_pos)
        self.Targetting = Py4GW.HeroAI.GetTargetting(own_party_pos)
        self.Combat = Py4GW.HeroAI.GetCombat(own_party_pos)
        
        for i in range(9):
            self.skills[i-1] = Py4GW.HeroAI.GetSkill(own_party_pos, i)

class HeroAI_contrainer_class:
    def __init__(self):
        self.AI_state = False
        self.own_party_pos = None
        self.window_module = None
        self.window_control = window_control_class()

    def Update(self):
        self.AI_state = Py4GW.HeroAI.GetAIStatus()
        self.own_party_pos = Py4GW.HeroAI.GetMyPartyPos()
        self.window_control.Update(self.own_party_pos)



hero_ai = HeroAI_contrainer_class()
hero_ai.window_module = ImGui.WindowModule(module_name, window_name="HeroAI", window_size=(300, 300), window_flags=PyImGui.WindowFlags.AlwaysAutoResize)


def DrawWindow():
    global hero_ai

    if PyImGui.begin("HeroAI"):

        PyImGui.text("Party Position: " + str(hero_ai.own_party_pos))
       
        if PyImGui.begin_table("##HeroAIStatus", 7):
            PyImGui.table_setup_column("Party #", PyImGui.TableColumnFlags.WidthFixed)
            PyImGui.table_setup_column("Active", PyImGui.TableColumnFlags.WidthFixed)
            PyImGui.table_setup_column("Following", PyImGui.TableColumnFlags.WidthFixed)
            PyImGui.table_setup_column("Collision", PyImGui.TableColumnFlags.WidthFixed)
            PyImGui.table_setup_column("Looting", PyImGui.TableColumnFlags.WidthFixed)
            PyImGui.table_setup_column("Targetting", PyImGui.TableColumnFlags.WidthFixed)
            PyImGui.table_setup_column("Combat", PyImGui.TableColumnFlags.WidthFixed)
            PyImGui.table_headers_row()


            for i in range(1,9):
                PyImGui.table_next_row()
                PyImGui.table_next_column()  
                PyImGui.text(f"{i}")
                PyImGui.table_next_column()
                PyImGui.text(f"{Py4GW.HeroAI.IsActive(i)}")
                PyImGui.table_next_column()
                PyImGui.text(f"{Py4GW.HeroAI.GetFollowing(i)}")
                PyImGui.table_next_column()
                PyImGui.text(f"{Py4GW.HeroAI.GetCollision(i)}")
                PyImGui.table_next_column()
                PyImGui.text(f"{Py4GW.HeroAI.GetLooting(i)}")
                PyImGui.table_next_column()
                PyImGui.text(f"{Py4GW.HeroAI.GetTargetting(i)}")
                PyImGui.table_next_column()
                PyImGui.text(f"{Py4GW.HeroAI.GetCombat(i)}")
    

            PyImGui.end_table()
       
        following = ImGui.toggle_button(IconsFontAwesome5.ICON_RUNNING + "##FollowingStatus", hero_ai.window_control.Following)

        if following != hero_ai.window_control.Following:
            Py4GW.HeroAI.SetFollowing(hero_ai.own_party_pos,following)
        
    PyImGui.end()

def DrawActivateWindow():
    global hero_ai

    if PyImGui.begin("HeroAI Global Config"):

        checkbox_state = PyImGui.checkbox("Toggle AI", hero_ai.AI_state)

        if checkbox_state != hero_ai.AI_state:
            Py4GW.HeroAI.SetAIStatus(checkbox_state)


    PyImGui.end()

def main():
    global hero_ai

    if Map.IsMapReady() and Map.IsMapLoading() == False and Party.IsPartyLoaded():
        hero_ai.Update()
        DrawActivateWindow()

        if hero_ai.AI_state:
            DrawWindow()

if __name__ == "__main__":
    main()

