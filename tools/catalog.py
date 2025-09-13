# tools/catalog.py
import json
import logging
from strands import tool

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

try:
    with open("product_catalog.json") as f:
        CATALOG = json.load(f)
except Exception as e:
    logger.error(f"❌ Failed to load product_catalog.json: {e}")
    CATALOG = []

@tool
def recommend_product(user_text: str) -> dict:
    """
    Recommend a product from catalog based on simple keyword matching.
    """
    if not CATALOG:
        return {"error": "Product catalog not loaded."}

    try:
        q = (user_text or "").lower()
        for p in CATALOG:
            if any(k in q for k in p.get("keywords", [])):
                return p
        return CATALOG[0]
    except Exception as e:
        logger.error(f"❌ recommend_product failed: {e}")
        return {"error": str(e)}
