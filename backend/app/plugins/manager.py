import importlib
import os
import inspect
from typing import Dict
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
                        if inspect.isclass(attr) and issubclass(attr, BaseToolPlugin) and attr is not BaseToolPlugin:
                            plugin_instance = attr()
                            self.plugins[plugin_instance.name] = plugin_instance
                            print(f"[+] Loaded plugin: {plugin_instance.name}")
                except Exception as e:
                    print(f"[-] Failed to load plugin {module_name}: {e}")

    async def execute_tool(self, tool_name: str, tool_input: ToolInput, mode: str = "simulation") -> ToolOutput:
        plugin = self.plugins.get(tool_name)
        if not plugin:
            raise ValueError(f"Plugin '{tool_name}' is not registered.")
        
        if not plugin.validate_inputs(tool_input):
            raise ValueError(f"Input validation failed for tool '{tool_name}'.")
            
        if mode == "real":
            return await plugin.execute_real(tool_input)
        else:
            return await plugin.execute_simulated(tool_input)
