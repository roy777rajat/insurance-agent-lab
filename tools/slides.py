# tools/slides.py
import json, boto3, logging
from strands import tool

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

s3 = boto3.client("s3", region_name="eu-west-1")

@tool
def create_slides(product: dict, s3_bucket: str, s3_prefix: str) -> dict:
    """
    Save simple JSON slide deck into S3.
    """
    if not isinstance(product, dict):
        return {"error": "Product must be a dict"}
    if not s3_bucket or not s3_prefix:
        return {"error": "s3_bucket and s3_prefix are required"}

    try:
        slides = [
            {"title": product.get("name", "Unknown"), "content": product.get("short_description", "")},
            {"title": "Benefits", "content": ", ".join(product.get("benefits", []))},
        ]
        key = f"{s3_prefix}/slides.json"
        s3.put_object(Bucket=s3_bucket, Key=key, Body=json.dumps(slides))
        return {"slides_s3_uri": f"s3://{s3_bucket}/{key}"}
    except Exception as e:
        logger.error(f"❌ create_slides failed: {e}")
        return {"error": str(e)}
