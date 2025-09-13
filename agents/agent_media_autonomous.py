"""
Thin orchestrator for the insurance-media workflow (prompt-driven).
All workflow sequencing and retries are handled via system prompt instructions.
"""
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))  # add project root to path

from datetime import datetime
import logging
from strands import Agent
from tools.catalog import recommend_product
from tools.script_gen import generate_script
from tools.tts import synthesize_speech
from tools.slides import create_slides
from tools.nova_vedio import generate_nova_video
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# S3 target
S3_BUCKET = "my-insurance-agent-bucket"

# Intent keywords
INTENT_KEYWORDS = ["insurance", "policy", "annuity", "retirement", "inflation", "pension", "income", "protection"]

def simple_intent_check(text: str) -> bool:
    t = (text or "").lower()
    return any(k in t for k in INTENT_KEYWORDS)


def run_agent(query: str) -> dict:
    """Main entry point so router can call this agent dynamically."""
    if not query:
        return {"status": "failed", "error": "No user input provided"}

    if not simple_intent_check(query):
        return {"status": "ignored", "error": "Query not related to insurance/products"}

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    s3_prefix = f"runs/run_{ts}"  # All outputs stored under s3://{S3_BUCKET}/{s3_prefix}/

    # Minimal agent initialization
    agent = Agent(
        tools=[recommend_product, generate_script, synthesize_speech, create_slides, generate_nova_video],
        model="anthropic.claude-3-haiku-20240307-v1:0"
    )

    # Rich system prompt for full orchestration
    system_prompt = f"""
You are an autonomous orchestrator agent for insurance & media workflows.

RULES:
- You have access to the following tools:
  1) recommend_product(user_text: str) -> product dict
  2) generate_script(product: dict, s3_bucket: str, s3_prefix: str) -> {{ "narration_script_s3_uri": "<S3 URI>" }}
  3) synthesize_speech(narration_script_s3_uri: str, s3_bucket: str, s3_prefix: str) -> {{ "narration_audio_s3_uri": "<S3 URI>" }}
  4) create_slides(product: dict, s3_bucket: str, s3_prefix: str) -> {{ "slides_s3_uri": "<S3 URI>" }}
  5) generate_nova_video(narration_script_s3_uri: str, narration_audio_s3_uri: str, s3_bucket: str, s3_prefix: str) -> {{ "video_s3_uri": "<S3 URI>" }}

- Your task is to create an **end-to-end workflow** for the user request below.
- Always validate the output of each tool before calling the next.
- Retry automatically if a tool fails, up to 2 times.
- If a tool fails after retries, continue with remaining steps.
- Return the final JSON containing all URIs, status, and errors.

CONTEXT:
- S3 bucket: {S3_BUCKET}
- S3 prefix: {s3_prefix}
- All outputs must be saved under s3://{S3_BUCKET}/{s3_prefix}/

FINAL OUTPUT FORMAT:
{{
    "recommended_product": <product dict>,
    "narration_script_s3_uri": "<S3 URI or null>",
    "narration_audio_s3_uri": "<S3 URI or null>",
    "slides_s3_uri": "<S3 URI or null>",
    "video_s3_uri": "<S3 URI or null>",
    "status": "success" | "partial_success" | "failed",
    "error": "<error messages if any>"
}}

User request: {query}
"""

    logger.info("Dispatching to autonomous orchestrator agent...")
    result = agent(system_prompt)
    logger.info("Raw agent response: %s", result)

    # Convert result to dict safely
    if hasattr(result, "to_dict"):
        result_dict = result.to_dict()
    elif isinstance(result, dict):
        result_dict = result
    else:
        try:
            result_dict = json.loads(result)
        except Exception:
            result_dict = {}

    # Default final JSON structure
    final = {
        "recommended_product": result_dict.get("recommended_product"),
        "narration_script_s3_uri": result_dict.get("narration_script_s3_uri"),
        "narration_audio_s3_uri": result_dict.get("narration_audio_s3_uri"),
        "slides_s3_uri": result_dict.get("slides_s3_uri"),
        "video_s3_uri": result_dict.get("video_s3_uri"),
        "status": result_dict.get("status") or ("success" if result_dict.get("video_s3_uri") else "partial_success"),
        "error": result_dict.get("error")
    }

    return final


if __name__ == "__main__":
    query = input("User asks: ").strip()
    output = run_agent(query)
    print("\n✅ Final JSON output:")
    print(json.dumps(output, indent=2))
    print(f"\n🎬 Nova Video S3 URL: {output['video_s3_uri'] or 'Nova video not generated'}")
