import boto3
import json
import os
import time

# Create Bedrock Runtime client
client = boto3.client("bedrock-runtime", region_name="eu-west-1")

def call_bedrock(prompt: str, max_tokens: int = 512, temperature: float = 0.7, retries: int = 3):
    """Call Claude 3 Haiku on Bedrock with retry + clean JSON output."""
    payload = {
        "messages": [
            {"role": "user", "content": [{"type": "text", "text": prompt}]}
        ],
        "temperature": temperature,
        "max_tokens": max_tokens,
        "anthropic_version": "bedrock-2023-05-31"
    }

    for attempt in range(retries):
        try:
            response = client.invoke_model(
                modelId="anthropic.claude-3-haiku-20240307-v1:0",
                body=json.dumps(payload),
                contentType="application/json",
                accept="application/json"
            )

            result = json.loads(response["body"].read())
            return result

        except client.exceptions.ThrottlingException:
            wait_time = 2 ** attempt
            print(f"⚠️ Throttled, retrying in {wait_time}s...")
            time.sleep(wait_time)

    raise RuntimeError("❌ Failed to get response from Bedrock after retries.")

def save_output(result, filename="outputs/bedrock_output.json"):
    """Save raw JSON output to local file."""
    os.makedirs("outputs", exist_ok=True)
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"✅ Output saved to {filename}")
