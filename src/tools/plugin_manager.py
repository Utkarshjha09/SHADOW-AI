# src/tools/plugin_manager.py
"""
Plugin manager for SHADOW's tool system
"""
import os
import importlib
from typing import Dict, Any, List
from .system_tools import SystemTools

class PluginManager:
    def __init__(self):
        self.plugins = {}
        self.load_core_plugins()
    
    def load_core_plugins(self):
        """Load the core system tools plugin."""
        self.plugins['system'] = SystemTools()
    
    def register_plugin(self, name: str, plugin_instance):
        """Register a new plugin."""
        self.plugins[name] = plugin_instance
        print(f"✅ Plugin '{name}' registered")
    
    def get_plugin(self, name: str):
        """Get a plugin by name."""
        return self.plugins.get(name)
    
    def list_plugins(self) -> List[str]:
        """List all available plugins."""
        return list(self.plugins.keys())
    
    def execute_tool(self, plugin_name: str, method_name: str, *args, **kwargs) -> Dict[str, Any]:
        """Execute a tool method from a specific plugin."""
        plugin = self.get_plugin(plugin_name)
        if not plugin:
            return {"error": f"Plugin '{plugin_name}' not found"}
        
        if not hasattr(plugin, method_name):
            return {"error": f"Method '{method_name}' not found in plugin '{plugin_name}'"}
        
        try:
            method = getattr(plugin, method_name)
            result = method(*args, **kwargs)
            return {"success": True, "result": result}
        except Exception as e:
            return {"error": f"Error executing {plugin_name}.{method_name}: {str(e)}"}

# Global plugin manager instance
plugin_manager = PluginManager()
