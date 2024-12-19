import os
import sys
import json
import logging
from pathlib import Path
from typing import Optional, Dict, Any

class GWToolBox:
    VERSION = "1.0.0"
    
    def __init__(self, config_path: Optional[str] = None):
        self.logger = logging.getLogger("GWToolBox")
        self.config: Dict[str, Any] = {}
        self.plugins: Dict[str, Any] = {}
        
        # Initialize config
        if config_path:
            self.config_path = Path(config_path)
        else:
            self.config_path = Path.home() / ".gwtoolbox" / "config.json"
            
        self._load_config()
        self._initialize_plugins()

    def _load_config(self) -> None:
        """Load configuration from JSON file"""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r') as f:
                    self.config = json.load(f)
            else:
                # Create default config
                self.config = {
                    "version": self.VERSION,
                    "plugins": {},
                    "settings": {
                        "debug": False,
                        "auto_update": True
                    }
                }
                # Ensure parent directory exists
                self.config_path.parent.mkdir(parents=True, exist_ok=True)
                self._save_config()
                
        except Exception as e:
            self.logger.error(f"Failed to load config: {e}")
            self.config = {}

    def _save_config(self) -> None:
        """Save current configuration to JSON file"""
        try:
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=4)
        except Exception as e:
            self.logger.error(f"Failed to save config: {e}")

    def _initialize_plugins(self) -> None:
        """Initialize enabled plugins"""
        plugin_dir = Path(__file__).parent / "plugins"
        if not plugin_dir.exists():
            return

        for plugin_file in plugin_dir.glob("*.py"):
            if plugin_file.stem.startswith("_"):
                continue
                
            try:
                # Dynamic import of plugin module
                module_name = f"plugins.{plugin_file.stem}"
                plugin_module = __import__(module_name, fromlist=["Plugin"])
                plugin_class = getattr(plugin_module, "Plugin")
                
                # Initialize plugin if enabled in config
                plugin_name = plugin_file.stem
                if self.config.get("plugins", {}).get(plugin_name, {}).get("enabled", False):
                    plugin_instance = plugin_class(self)
                    self.plugins[plugin_name] = plugin_instance
                    self.logger.info(f"Loaded plugin: {plugin_name}")
                    
            except Exception as e:
                self.logger.error(f"Failed to load plugin {plugin_file.stem}: {e}")

    def start(self) -> None:
        """Start GWToolBox and all enabled plugins"""
        self.logger.info(f"Starting GWToolBox v{self.VERSION}")
        
        # Initialize each plugin
        for plugin_name, plugin in self.plugins.items():
            try:
                plugin.start()
            except Exception as e:
                self.logger.error(f"Failed to start plugin {plugin_name}: {e}")

    def stop(self) -> None:
        """Stop GWToolBox and all plugins"""
        self.logger.info("Stopping GWToolBox")
        
        # Stop each plugin
        for plugin_name, plugin in self.plugins.items():
            try:
                plugin.stop()
            except Exception as e:
                self.logger.error(f"Failed to stop plugin {plugin_name}: {e}")
        
        # Save config
        self._save_config()

def main():
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Create and start GWToolBox
    toolbox = GWToolBox()
    
    try:
        toolbox.start()
        
        # Keep running until interrupted
        while True:
            try:
                input()
            except KeyboardInterrupt:
                break
                
    finally:
        toolbox.stop()

if __name__ == "__main__":
    main()
