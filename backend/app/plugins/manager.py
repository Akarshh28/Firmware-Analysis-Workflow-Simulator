import importlib
import os
from typing import Dict, Optional
from app.plugins.base import BaseToolPlugin, ToolInput, ToolOutput

class PluginManager:
    def __init__(self):
        self.plugins: Dict[str, BaseToolPlugin] = {}
        self.load_plugins()

    def load_plugins(self):
        plugin_dir = os.path.dirname(__file__)
        for file in os.listdir(plugin_dir):
            if file.endswith('.py') and file not in ('__init__.py', 'base.py', 'manager.py'):
                module_name = f"app.plugins.{file[:-3]}"
                try:
                    module = importlib.import_module(module_name)
                    # Find all classes that inherit from BaseToolPlugin and instantiate them
                    for attr_name in dir(module):
                        attr = getattr(module, attr_name)
                        if isinstance(attr, type) and issubclass(attr, BaseToolPlugin) and attr is not BaseToolPlugin:
                            plugin_instance = attr()
                            self.plugins[plugin_instance.name] = plugin_instance
                except Exception as e:
                    print(f"Error loading plugin from {file}: {e}")

    def get_plugin(self, tool_name: str) -> Optional[BaseToolPlugin]:
        return self.plugins.get(tool_name)

    async def execute_tool(self, tool_name: str, tool_input: ToolInput, mode: str = "simulation") -> ToolOutput:
        plugin = self.get_plugin(tool_name)
        if not plugin:
            raise ValueError(f"Plugin '{tool_name}' is not registered.")
        
        # Check validation
        if not plugin.validate_inputs(tool_input):
            raise ValueError(f"Input validation failed for tool '{tool_name}' and file '{tool_input.target_filepath}'.")
            
        if mode == "real":
            return await plugin.execute_real(tool_input)
        else:
            return await plugin.execute_simulated(tool_input)

# Singleton manager
plugin_manager = PluginManager()
