# tools/tool_registry.py
"""
Tool Registry for dynamic LLM-based orchestration.

All tools used in the insurance-media workflow are registered here.
The agent_dynamic.py will load tools from this registry only.
"""

from tools.catalog import recommend_product
from tools.script_gen import generate_script
from tools.tts import synthesize_speech
from tools.slides import create_slides
from tools.nova_vedio import generate_nova_video

def list_tools():
    """
    Return a list of all callable tool functions.
    Do NOT return strings or file paths. Must be imported @tool functions.
    """
    return [
        recommend_product,
        generate_script,
        synthesize_speech,
        create_slides,
        generate_nova_video
    ]
