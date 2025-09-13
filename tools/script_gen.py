# tools/script_gen.py
import boto3
import logging
from strands import tool
from bedrock_helper import call_bedrock

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

s3 = boto3.client("s3", region_name="eu-west-1")

@tool
def generate_script(product, s3_bucket: str, s3_prefix: str) -> dict:
    """
    Generate narration script using Bedrock LLM and save directly to S3.
    Returns dict with S3 URI or error.
    Supports product as dict OR string.
    """

    # 🔥 Input validation
    if not s3_bucket or not s3_prefix:
        return {"error": "s3_bucket and s3_prefix are required."}

    try:
        # 🔥 Normalize input (dict OR string)
        if isinstance(product, dict):
            product_name = product.get("name", "Unknown Product")
            product_desc = product.get("short_description") or "This product offers valuable benefits."
            product_benefits = ", ".join(product.get("benefits", []))
            product_text = f"{product_name} - {product_desc}\nBenefits: {product_benefits}"
        elif isinstance(product, str):
            product_text = product
        else:
            return {"error": "Product parameter must be a dictionary or string."}

        # 🔥 Construct robust LLM prompt
        prompt = f"""
You are a helpful AI assistant specialized in insurance product narration.
Generate a concise, clear, and engaging product description suitable for narration in under 500 characters.
Always produce non-empty, human-readable text, even if the description is missing.

Product info:
{product_text}

Return ONLY plain text.
"""

        logger.info("🤖 Calling Bedrock LLM for script generation...")
        logger.info(f"📝 Prompt: {prompt}")

        # 🔥 Call Bedrock with exception handling
        try:
            result = call_bedrock(prompt)
        except Exception as e:
            logger.error(f"❌ Bedrock call failed: {e}")
            return {"error": f"Bedrock call failed: {e}"}

        logger.info("✅ Bedrock response received.")
        logger.info(f"Bedrock full response: {result}")

        # 🔥 Extract text safely from Bedrock response
        narration_text = ""

        # Case 1: output -> content
        try:
            narration_text = (
                result.get("output", {}).get("content", [{}])[0].get("text", "").strip()
            )
        except Exception:
            pass

        # Case 2: direct content
        if not narration_text:
            try:
                narration_text = result.get("content", [{}])[0].get("text", "").strip()
            except Exception:
                pass

        # 🔥 Fallback if still empty
        if not narration_text:
            narration_text = f"{product_name}: A great insurance product designed to meet your needs."

        logger.info(f"✅ Narration text extracted ({len(narration_text)} chars).")

        # 🔥 Upload to S3
        try:
            key = f"{s3_prefix}/narration_script.txt"
            s3.put_object(Bucket=s3_bucket, Key=key, Body=narration_text.encode("utf-8"))
            s3_uri = f"s3://{s3_bucket}/{key}"
        except Exception as e:
            logger.error(f"❌ Failed to upload narration to S3: {e}")
            return {"error": f"S3 upload failed: {e}"}

        return {"narration_script_s3_uri": s3_uri}

    except Exception as e:
        logger.error(f"❌ generate_script failed: {e}")
        return {"error": str(e)}
