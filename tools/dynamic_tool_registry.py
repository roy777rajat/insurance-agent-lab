# tools/tool_registry.py
import importlib
import os
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

TOOLS_DIR = os.path.dirname(__file__)

def list_tools():
    """
    Auto-discover all tools in the tools/ folder that are decorated with @tool.
    Returns a list of tool objects that can be passed directly to the Agent.
    """
    tool_list = []

    for file in os.listdir(TOOLS_DIR):
        if file.endswith(".py") and file != "__init__.py" and file != "tool_registry.py" and file != "dynamic_tool_registry.py":
            module_name = f"tools.{file[:-3]}"  # remove .py
            try:
                module = importlib.import_module(module_name)
                # Add any callable decorated with 'tool' (simplest: attributes ending without _private)
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if callable(attr) and hasattr(attr, "__wrapped__"):  # strands @tool uses __wrapped__
                        tool_list.append(attr)
                        logger.info(f"✅ Tool loaded: {module_name}.{attr_name}")
            except Exception as e:
                logger.warning(f"⚠️ Failed to import {module_name}: {e}")

    return tool_list
