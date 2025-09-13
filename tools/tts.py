# tools/tts.py
import boto3
import logging
from strands import tool

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

polly = boto3.client("polly", region_name="us-east-1")
s3 = boto3.client("s3", region_name="eu-west-1")

@tool
def synthesize_speech(script_s3_uri: str, s3_bucket: str, s3_prefix: str) -> dict:
    """
    Convert script text (from S3) into speech using Polly.
    Save directly to S3 as MP3.
    """
    if not script_s3_uri or not script_s3_uri.startswith("s3://"):
        return {"error": "Invalid script_s3_uri"}
    if not s3_bucket or not s3_prefix:
        return {"error": "s3_bucket and s3_prefix are required"}

    try:
        bucket, key = script_s3_uri.replace("s3://", "").split("/", 1)
        obj = s3.get_object(Bucket=bucket, Key=key)
        text = obj["Body"].read().decode("utf-8")

        resp = polly.synthesize_speech(Text=text, OutputFormat="mp3", VoiceId="Joanna")

        audio_key = f"{s3_prefix}/narration_audio.mp3"
        s3.upload_fileobj(resp["AudioStream"], s3_bucket, audio_key)
        return {"narration_audio_s3_uri": f"s3://{s3_bucket}/{audio_key}"}

    except Exception as e:
        logger.error(f"❌ synthesize_speech failed: {e}")
        return {"error": str(e)}
