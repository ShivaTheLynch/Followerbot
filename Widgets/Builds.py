from Py4GWCoreLib import *
import os

module_name = "Skillbar Manager"

class config:
    def __init__(self):
        self.skillbars = {}  # Dictionary to store skillbar codes
        self.new_name = ""   # For new skillbar input
        self.new_code = ""   # For new skillbar code input
        self.skills_folder = "skills"  # Folder name for skillbar files
        self.selected = None  # Currently selected skillbar
        self.build_tree = {}  # Tree structure for builds
        self.load_skillbars()  # Load saved skillbars on init
        self.visible = True
        self.new_build_name = ""
        self.selected_build = None

    def save_skillbar(self, name, code):
        try:
            if not os.path.exists(self.skills_folder):
                os.makedirs(self.skills_folder)
            
            # Extract profession from build code or default to "Other"
            profession = "Other"
            # Add logic here to detect profession from build code
            
            # Prepend profession to name if not already present
            if not any(name.startswith(p) for p in ["Warrior", "Ranger", "Monk", "Necromancer", "Mesmer", 
                                                   "Elementalist", "Assassin", "Ritualist", "Paragon", "Dervish"]):
                name = f"{profession}/{name}"
            
            file_path = os.path.join(self.skills_folder, f"{name}.txt")
            with open(file_path, 'w') as f:
                f.write(code)
            self.skillbars[name] = code
            Py4GW.Console.Log(module_name, f"Saved skillbar to {file_path}", Py4GW.Console.MessageType.Debug)
        except Exception as e:
            Py4GW.Console.Log(module_name, f"Error saving skillbar: {str(e)}", Py4GW.Console.MessageType.Debug)

    def delete_skillbar(self, name):
        try:
            file_path = os.path.join(self.skills_folder, f"{name}.txt")
            if os.path.exists(file_path):
                os.remove(file_path)
                del self.skillbars[name]
                Py4GW.Console.Log(module_name, f"Deleted skillbar: {file_path}", Py4GW.Console.MessageType.Debug)
        except Exception as e:
            Py4GW.Console.Log(module_name, f"Error deleting skillbar: {str(e)}", Py4GW.Console.MessageType.Debug)

    def load_selected(self):
        try:
            if self.selected in self.skillbars:
                code = self.skillbars[self.selected]
                SkillBar.LoadSkillTemplate(code)
                Py4GW.Console.Log(module_name, f"Loaded skillbar: {self.selected}", Py4GW.Console.MessageType.Debug)
        except Exception as e:
            Py4GW.Console.Log(module_name, f"Error loading skillbar: {str(e)}", Py4GW.Console.MessageType.Debug)

    def organize_builds_tree(self):
        self.build_tree = {}
        # Sort the skillbars by path to ensure consistent ordering
        sorted_builds = sorted(self.skillbars.items(), key=lambda x: x[0])
        
        for path, code in sorted_builds:
            current_dict = self.build_tree
            parts = path.split('/')
            
            # Handle all parts of the path including the final file
            for i, part in enumerate(parts):
                if i == len(parts) - 1:  # If this is the last part (file)
                    current_dict[part] = code
                else:  # This is a directory
                    if part not in current_dict:
                        current_dict[part] = {}
                    current_dict = current_dict[part]

    def draw_build_tree(self, tree, path=""):
        for name, content in sorted(tree.items()):
            if isinstance(content, dict):  # This is a folder
                if PyImGui.tree_node(name):
                    new_path = f"{path}/{name}" if path else name
                    self.draw_build_tree(content, new_path)
                    PyImGui.tree_pop()
            else:  # This is a build file
                if PyImGui.begin_table(f"build_{name}", 3, PyImGui.TableFlags.SizingFixedFit):
                    PyImGui.table_next_row()
                    
                    # Build name column
                    PyImGui.table_next_column()
                    full_path = f"{path}/{name}" if path else name
                    if PyImGui.selectable(name, self.selected == full_path)[0]:
                        self.load_build(full_path)
                    
                    # Load button column
                    PyImGui.table_next_column()
                    if PyImGui.button(f"Load##load_{name}"):
                        self.load_build(full_path)
                    
                    # Delete button column
                    PyImGui.table_next_column()
                    if PyImGui.button(f"X##delete_{name}"):
                        self.delete_skillbar(full_path)
                        self.load_skillbars()
                    
                    PyImGui.end_table()

    def load_skillbars(self):
        try:
            self.skillbars.clear()
            if not os.path.exists(self.skills_folder):
                os.makedirs(self.skills_folder)
                return

            # Walk through all directories and subdirectories
            for root, dirs, files in os.walk(self.skills_folder):
                for filename in files:
                    if filename.endswith(".txt"):
                        file_path = os.path.join(root, filename)
                        try:
                            rel_path = os.path.relpath(file_path, self.skills_folder)
                            name = os.path.splitext(rel_path)[0]
                            
                            with open(file_path, 'r') as f:
                                code = f.read().strip()
                                self.skillbars[name] = code
                        except Exception as e:
                            Py4GW.Console.Log(module_name, f"Error loading {file_path}: {str(e)}", Py4GW.Console.MessageType.Debug)
            
            self.organize_builds_tree()  # Organize builds into tree structure
            Py4GW.Console.Log(module_name, f"Loaded {len(self.skillbars)} skillbars", Py4GW.Console.MessageType.Debug)
        except Exception as e:
            Py4GW.Console.Log(module_name, f"Error loading skillbars: {str(e)}", Py4GW.Console.MessageType.Debug)

    def load_build(self, path):
        try:
            if path in self.skillbars:
                self.selected = path
                code = self.skillbars[path]
                # Make sure we have a valid template code
                if code and isinstance(code, str):
                    # Strip any whitespace and validate code format
                    code = code.strip()
                    SkillBar.LoadSkillTemplate(code)
                    Py4GW.Console.Log(module_name, f"Loading skillbar: {path} with code: {code}", Py4GW.Console.MessageType.Debug)
                else:
                    Py4GW.Console.Log(module_name, f"Invalid template code for: {path}", Py4GW.Console.MessageType.Debug)
            else:
                Py4GW.Console.Log(module_name, f"Build not found: {path}", Py4GW.Console.MessageType.Debug)
        except Exception as e:
            Py4GW.Console.Log(module_name, f"Error loading skillbar: {str(e)}", Py4GW.Console.MessageType.Debug)

widget_config = config()
window_module = ImGui.WindowModule(
    module_name,
    window_name="Skillbar Manager",
    window_size=(400, 300),
    window_flags=PyImGui.WindowFlags.AlwaysAutoResize
)

def configure():
    """Required configuration function for the widget"""
    if PyImGui.begin("Skillbar Manager Configuration"):
        PyImGui.text("Manage your saved skillbars")
        PyImGui.end()

def DrawWindow():
    global widget_config

    window_open = PyImGui.begin(window_module.window_name, window_module.window_flags)
    
    try:
        if window_open:
            # Input fields for new skillbar
            PyImGui.text("Add New Skillbar:")
            widget_config.new_name = PyImGui.input_text("Name##new", widget_config.new_name, 100)
            widget_config.new_code = PyImGui.input_text("Code##new", widget_config.new_code, 100)

            # Save button
            if PyImGui.button("Save Skillbar") and widget_config.new_name and widget_config.new_code:
                widget_config.save_skillbar(widget_config.new_name, widget_config.new_code)
                widget_config.new_name = ""
                widget_config.new_code = ""
                widget_config.load_skillbars()

            PyImGui.separator()
            PyImGui.text("Saved Skillbars:")

            # Refresh button
            if PyImGui.button("Refresh List"):
                widget_config.load_skillbars()

            PyImGui.separator()

            # Draw the build tree starting from the root
            if PyImGui.tree_node("Builds"):
                widget_config.draw_build_tree(widget_config.build_tree)
                PyImGui.tree_pop()

    except Exception as e:
        Py4GW.Console.Log(module_name, f"Error in DrawWindow: {str(e)}", Py4GW.Console.MessageType.Debug)
    
    PyImGui.end()

def main():
    """Required main function for the widget"""
    try:
        if Map.IsMapReady() and Party.IsPartyLoaded():
            DrawWindow()
    except Exception as e:
        Py4GW.Console.Log(module_name, f"Error in main: {str(e)}", Py4GW.Console.MessageType.Debug)
        return False
    return True

# These functions need to be available at module level
__all__ = ['main', 'configure']

if __name__ == "__main__":
    main()
