import boto3
import time
import random
import logging
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Hard-coded inputs for unit test ---
S3_BUCKET = "my-insurance-agent-bucket"
RUN_PREFIX = "runs/run_20250912_112614"
SCRIPT_FILE = f"s3://{S3_BUCKET}/{RUN_PREFIX}/narration_script.txt"
OUTPUT_VIDEO_S3_URI = f"s3://{S3_BUCKET}/{RUN_PREFIX}/nova_test_video/"

# --- Initialize Bedrock client for Ireland (eu-west-1) ---
bedrock = boto3.client("bedrock-runtime", region_name="eu-west-1")
s3 = boto3.client("s3", region_name="eu-west-1")


import ast  # safer than eval for Python dict text

def extract_narration_text(script_s3_path):
    """
    Reads narration JSON/dict text from S3 and extracts only the 'text' content.
    Cleans up newlines and extra spaces.
    """
    bucket, key = script_s3_path.replace("s3://", "").split("/", 1)
    script_obj = s3.get_object(Bucket=bucket, Key=key)
    script_content = script_obj["Body"].read().decode("utf-8")

    try:
        # Try strict JSON first
        script_json = json.loads(script_content)
    except json.JSONDecodeError:
        # Fall back to parsing Python dict-style string
        script_json = ast.literal_eval(script_content)

    # Extract only "text" fields
    text_parts = [msg["text"] for msg in script_json.get("content", []) if msg.get("type") == "text"]
    full_text = " ".join(text_parts)

    # Clean up \n, \n\n, extra spaces
    cleaned_text = " ".join(full_text.split())
    logger.info(f"✅ Extracted Narration Text ({len(cleaned_text)} chars): {cleaned_text}")
    return cleaned_text



def generate_nova_video(script_file, output_s3_uri):
    """
    Unit test for Nova Reel video generation using narration from S3.
    """
    # Extract cleaned narration text
    narration_text = extract_narration_text(script_file)
    # Truncate to 512 chars if needed
    if len(narration_text) > 512:
        narration_text = narration_text[:512]
        logger.info(f"⚠️ Narration text truncated to 512 chars.")
        


   # --- Prepare Nova Reel async job ---
    model_id = "amazon.nova-reel-v1:0"
    seed = random.randint(0, 2147483646)

    model_input = {
        "taskType": "TEXT_VIDEO",
        "textToVideoParams": {"text": narration_text},
        "videoGenerationConfig": {
            "fps": 24,
            "durationSeconds": 6,
            "dimension": "1280x720",
            "seed": seed,
        },
    }

    output_config = {"s3OutputDataConfig": {"s3Uri": output_s3_uri}}

    # Submit async job
    try:
        response = bedrock.start_async_invoke(
            modelId=model_id,
            modelInput=model_input,
            outputDataConfig=output_config,
        )
        invocation_arn = response["invocationArn"]
        logger.info(f"Nova job started: {invocation_arn}")
    except Exception as e:
        logger.error(f"Failed to start Nova job: {e}")
        return None

    # --- Poll until job completion ---
    retries = 0
    max_retries = 40
    while retries < max_retries:
        job = bedrock.get_async_invoke(invocationArn=invocation_arn)
        status = job["status"]

        if status == "Completed":
            video_s3_path = f"{output_s3_uri}/output.mp4"
            logger.info(f"✅ Video generated: {video_s3_path}")
            return video_s3_path
        elif status == "Failed":
            logger.error(f"❌ Nova job failed: {job.get('failureMessage', 'Unknown')}")
            return None
        else:
            logger.info(f"⏳ Job in progress... waiting 15s ({retries+1}/{max_retries})")
            time.sleep(15)
            retries += 1

    logger.error("❌ Nova job did not complete in expected time.")
    return None


if __name__ == "__main__":
    print("Starting Nova video unit test...")
    video_uri = generate_nova_video(SCRIPT_FILE, OUTPUT_VIDEO_S3_URI)
    if video_uri:
        print("\n🎬 Video successfully generated at:", video_uri)
    else:
        print("\n❌ Video generation failed.")
