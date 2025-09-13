# router/agent_registry.py
import importlib
import os

AGENT_FOLDER = "agents"

def list_agents():
    """Return all available agents as dict: name -> callable"""
    agents = {}
    for f in os.listdir(AGENT_FOLDER):
        if f.startswith("agent_") and f.endswith(".py") and f != "__init__.py" and f != "agent_media_control.py":
            name = f.replace(".py", "")
            module = importlib.import_module(f"agents.{name}")
            if hasattr(module, "run_agent"):
                agents[name] = module.run_agent
    return agents
