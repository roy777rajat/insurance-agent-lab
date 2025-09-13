# router/router_agent.py
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import logging
from bedrock_helper import call_bedrock
from agent_registry import list_agents
import json

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Load all available agents dynamically
AGENTS = list_agents()

SYSTEM_PROMPT = """
You are an intelligent Router Agent. Your job is:
1. Analyze user input and detect which agent(s) to call.
2. Select only from the available agents in the registry: {agents_list}
3. Return strictly parseable JSON in this format:
{{
  "agents_to_invoke": [
    {{"name": "<agent_name>", "reason": "<why this agent is chosen>"}}
  ],
  "error": null
}}

4. If the user input does NOT match any agent context:
   - Return an empty "agents_to_invoke" array
   - Provide a friendly human-style message in "error", e.g.:
     "Sorry, I cannot assist with this request. You can ask me anything about the existing agents: {agents_list}."
5. Do NOT include any extra text outside the JSON.
6. ALWAYS produce parseable JSON.

User input: {user_input}
"""



def run_router(query: str) -> dict:
    """Main function to route user queries to relevant agents dynamically."""
    prompt = SYSTEM_PROMPT.format(
        user_input=query,
        agents_list=list(AGENTS.keys())   # <-- Added this
    )
    result = call_bedrock(prompt)
    logger.info(f"Router LLM full response: {result}")

    
    # Extract LLM text
    llm_content = result.get("content", [])
    llm_text = ""
    for item in llm_content:
        if item.get("type") == "text" and item.get("text"):
            llm_text += item["text"]

    llm_text = llm_text.strip()

    # Remove leading/trailing quotes if LLM wraps JSON in quotes
    if llm_text.startswith('"') and llm_text.endswith('"'):
        llm_text = llm_text[1:-1].replace('\\"', '"')

    if not llm_text:
        return {
            "agents_to_invoke": [],
            "error": f"LLM returned empty response. Available agents: {list(AGENTS.keys())}"
        }

    # Parse JSON
    try:
        instructions = json.loads(llm_text)
    except Exception as e:
        return {
            "agents_to_invoke": [],
            "error": f"Failed to parse LLM output: {e}. Raw text: {llm_text}"
        }





    # If no suitable agents, politely inform the user
    if not instructions.get("agents_to_invoke"):
        error_msg = instructions.get("error") or f"Sorry, I cannot assist with this request. You can ask anything about the existing agents: {list(AGENTS.keys())}."
        return {"agents_to_invoke": [], "error": error_msg}

    # Call selected agents
    outputs = {}
    for agent_info in instructions.get("agents_to_invoke", []):
        name = agent_info.get("name")
        if name in AGENTS:
            try:
                outputs[name] = AGENTS[name](query)
            except Exception as e:
                outputs[name] = {"error": str(e)}
        else:
            outputs[name] = {"error": "Agent not found"}

    return outputs


if __name__ == "__main__":
    query = input("User prompt: ").strip()
    output = run_router(query)
    print(json.dumps(output, indent=2))
