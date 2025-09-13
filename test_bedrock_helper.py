from bedrock_helper import call_bedrock, save_output
import json

prompt = """
Generate 2 slides for a new Vehicle Insurance Product.
Each slide should have:
- A clear title
- 2-3 short bullet points
Also provide a narration script for each slide.
Return JSON with keys: slides (list) and narration (list).
"""

result = call_bedrock(prompt)

print("=== Clean Result ===")
print(json.dumps(result, indent=2))

save_output(result, "outputs/insurance_slides.json")
