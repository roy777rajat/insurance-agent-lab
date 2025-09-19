"""
Dynamic LLM-driven insurance agent.
Orchestration, retries, tool selection is handled by the LLM.
Python only collects user input, passes system prompt, and returns JSON output.
"""

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))  # add project root to path

from datetime import datetime
import logging
import json
from strands import Agent
from tools.tool_registry import list_tools


# Show rich UI for tools in CLI
os.environ["STRANDS_TOOL_CONSOLE_MODE"] = "enabled"

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

S3_BUCKET = "my-insurance-agent-bucket"

INTENT_KEYWORDS = ["insurance", "policy", "annuity", "retirement", "inflation", "pension", "income", "protection"]

def simple_intent_check(text: str) -> bool:
    t = (text or "").lower()
    return any(k in t for k in INTENT_KEYWORDS)


def run_agent(query: str) -> dict:
    """Main entry point so router can call this agent dynamically."""
    if not query:
        return {"status": "failed", "error": "No user input provided"}

    if not simple_intent_check(query):
        return {"status": "ignored", "error": "Query not related to insurance/products.I am here to help you with insurance products, policies, annuities, and retirement plans."
        " Please ask me anything about these topics."
        " For example, you can say: 'Recommend an annuity product for retirement income'."
        " I will always provide structured JSON output for easy integration."
        " Feel free to ask me about insurance products, policies, annuities, and retirement plans."
        }

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    s3_prefix = f"runs/run_{ts}"

    # Minimal Agent, fully LLM-driven orchestration
    agent = Agent(
        tools=list_tools(),
        model="anthropic.claude-3-haiku-20240307-v1:0"
    )

    system_prompt = f"""
You are a dynamic orchestrator for insurance and media workflows.

Rules:
1) Decide which tools to call, in what order, based on the user query.
2) Handle retries, missing inputs, and logical flow yourself.
3) Use only the tools from the registry: {list_tools()}
4) Store all outputs in S3: bucket {S3_BUCKET}, prefix {s3_prefix}
5) Return a single JSON at the end with:
{{
  "recommended_product": <product dict>,
  "narration_script_s3_uri": "<S3 URI>",
  "narration_audio_s3_uri": "<S3 URI>",
  "slides_s3_uri": "<S3 URI>",
  "video_s3_uri": "<S3 URI>",
  "status": "success" or "partial_success" or "failed",
  "error": "<error message if any>",
  "steps": [
    {{
      "tool": "<tool name>",
      "input": {{ ... }},
      "output": {{ ... }},
      "status": "success" or "failed",
      "error": "<error message if any>"
    }}
  ]
}}

User query: {query}
"""

    logger.info("Dispatching user query to LLM agent...")
    result = agent(system_prompt)
    #logger.info("Raw agent response: %s", result)

    # Parse final JSON
    try:
        if hasattr(result, "to_dict"):
            final_json = result.to_dict()
        elif isinstance(result, dict):
            final_json = result
        else:
            final_json = json.loads(result)
    except Exception as e:
        logger.error(f"❌ Failed to parse LLM output: {e}")
        final_json = {"status": "failed", "error": str(e)}

    return final_json


if __name__ == "__main__":

    print("=" * 70)
    print("🤝  WELCOME TO YOUR INSURANCE PRODUCT MEDIA MAKER ASSISTANT  🤝")
    print("=" * 70)
    print("✨ I can assist you with:")
    print("   🛡️  Exploring different Insurance products (Life, Pension, Annuities)")
    print("   📋 Showing available product options tailored for you")
    print("   🔊 Creating an AUDIO transcript for your selected product")
    print("   📑 Designing SLIDES for your chosen product")
    print("   🎬 Producing a VIDEO presentation of your favorite product")
    print("   🕒 Checking the current time")
    print()
    print("💡 Tips:")
    print("   • Ask me about insurance products, policies, annuities, and retirement plans")
    print("   • I will always provide structured JSON output for easy integration")
    print("   • Example:   'Recommend an annuity product for retirement income'")
    print()
    print("🚪 Type 'exit' anytime to quit")
    print("=" * 70)
    print()

    # Run the agent in a loop for interactive conversation
    while True:
        try:
            query = input("👤 You: ").strip()

            if not query:
                print("💭 Please enter a message or type 'exit' to quit")
                continue

            if query.lower() in ["exit", "quit", "bye", "goodbye"]:
                print()
                print("=======================================")
                print("👋 Thanks for using Insurance Product Media Maker Assistant!")
                print("🎉 Have a wonderful day ahead! Stay insured, stay secure!")
                print("=======================================")
                break

            print("🤖 MediaBot: ", end="")
            output = run_agent(query)
            print("\n✅ Final JSON output:")
            print(json.dumps(output, indent=2))
        except KeyboardInterrupt:
            print()
            print("=======================================")
            print("⚠️  Assistant interrupted by user")
            print("👋 See you next time!")
            print("=======================================")
            break
        except Exception as e:
            print(f"❌ An error occurred: {str(e)}")
            print("💡 Please try again or type 'exit' to quit")
            print()
