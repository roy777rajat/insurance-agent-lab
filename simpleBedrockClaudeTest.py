import boto3
import json

# Use bedrock-runtime for invocation
client = boto3.client("bedrock-runtime", region_name="eu-west-1")

prompt = "Write a haiku about insurance claims."

response = client.invoke_model(
    modelId="anthropic.claude-3-haiku-20240307-v1:0",
    contentType="application/json",
    accept="application/json",
    body=json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 500
    })
)

# The response body is a streaming object → decode it
result = json.loads(response["body"].read().decode("utf-8"))
print(result)
