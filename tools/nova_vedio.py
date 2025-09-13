import boto3
import time
import random
import logging
import json
import ast
import os
from strands import tool

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

s3 = boto3.client("s3")


def extract_narration_text(script_s3_path: str) -> str:
    """
    Reads narration JSON/dict text from S3 and extracts only the 'text' content.
    Cleans up newlines and extra spaces.
    """
    bucket, key = script_s3_path.replace("s3://", "").split("/", 1)
    logger.info(f"📄 (Good) Reading narration script from s3://{bucket}/{key}")
    script_obj = s3.get_object(Bucket=bucket, Key=key)
    logger.info(f"✅ Successfully read narration script from S3")
    script_content = script_obj["Body"].read().decode("utf-8")
    logger.info(f"📜 Script content length: {len(script_content)} chars and text is :{script_content}")
    return script_content
    # try:
    #     script_json = json.loads(script_content)
    # except json.JSONDecodeError:
    #     script_json = ast.literal_eval(script_content)

    # text_parts = [msg["text"] for msg in script_json.get("content", []) if msg.get("type") == "text"]
    # full_text = " ".join(text_parts)
    # cleaned_text = " ".join(full_text.split())
    # logger.info(f"✅ Extracted narration ({len(cleaned_text)} chars): {cleaned_text}")

    # return cleaned_text


@tool
def generate_nova_video(
    narration_script_s3_uri: str,
    narration_audio_s3_uri: str = None,
    s3_bucket: str = None,
    s3_prefix: str = None,
    region: str = "eu-west-1",
):
    """
    Generate a video with Amazon Nova Reel using async API.
    - Reads narration text from S3 (JSON or dict-like file).
    - Cleans and truncates narration to 512 chars max.
    - Saves video to s3://{s3_bucket}/{s3_prefix}/nova_video/output.mp4
    """

    bedrock_runtime = boto3.client("bedrock-runtime", region_name=region)
    logger.info(f"🌍 Using Bedrock region: {region}")
    if not s3_bucket or not s3_prefix:
        logger.info(f" The s3_bucket is {s3_bucket}, s3_prefix is {s3_prefix}")
        return {"video_s3_uri": None, "error": "s3_bucket and s3_prefix are required"}
    
    logger.info(f"🏦 Using S3 bucket: {s3_bucket}, prefix: {s3_prefix}")
    
    
    if not narration_script_s3_uri or not narration_script_s3_uri.startswith("s3://"):
        logger.info(f" The narration_script_s3_uri is {narration_script_s3_uri}")
        return {"video_s3_uri": None, "error": "Valid narration_script_s3_uri (S3 path) is required"}
    logger.info(f"📝 Using narration script: {narration_script_s3_uri}")


    # --- Resolve narration text ---
    if narration_script_s3_uri and narration_script_s3_uri.startswith("s3://"):
        narration_text = extract_narration_text(narration_script_s3_uri)
    else:
        narration_text = str(narration_script_s3_uri or "")

    if not narration_text:
        return {"video_s3_uri": None, "error": "Narration text missing"}

    if len(narration_text) > 512:
        narration_text = narration_text[:512]
        logger.info("⚠️ Narration truncated to 512 chars.")

    # --- Prepare Nova input ---
    model_id = "amazon.nova-reel-v1:0"
    seed = random.randint(0, 2147483646)
    logger.info(f"-------- before calling nova api -------")
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
    logger.info(f"-------- after calling nova api -------")
    # Always output to nova_video/ under run prefix
    video_prefix = f"{s3_prefix}/nova_video"  # simple forward slash
    output_s3_uri = f"s3://{s3_bucket}/{video_prefix}/"
    output_config = {"s3OutputDataConfig": {"s3Uri": output_s3_uri}}
    logger.info(f"🎥 Video will be saved to: {output_s3_uri}" )


    logger.info("🎬 Submitting Nova Reel async job...")
    try:
        response = bedrock_runtime.start_async_invoke(
            modelId=model_id, modelInput=model_input, outputDataConfig=output_config
        )
    except Exception as e:
        logger.error(f"❌ Failed to start Nova job: {e}")
        return {"video_s3_uri": None, "error": str(e)}

    invocation_arn = response["invocationArn"]
    logger.info(f"Nova job started: {invocation_arn}")

    # --- Poll job status ---
    while True:
        try:
            job = bedrock_runtime.get_async_invoke(invocationArn=invocation_arn)
            status = job["status"]
        except Exception as e:
            logger.error(f"❌ Failed to poll Nova job: {e}")
            return {"video_s3_uri": None, "error": str(e)}

        if status == "Completed":
            bucket_uri = job["outputDataConfig"]["s3OutputDataConfig"]["s3Uri"]
            video_uri = f"{bucket_uri}/output.mp4"
            logger.info(f"✅ Video generated: {video_uri}")
            return {"video_s3_uri": video_uri}
        elif status == "Failed":
            msg = job.get("failureMessage", "Unknown error")
            logger.error(f"❌ Nova job failed: {msg}")
            return {"video_s3_uri": None, "error": msg}
        else:
            logger.info("⏳ Job in progress... waiting 15s")
            time.sleep(15)
