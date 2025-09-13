import os
from PIL import Image, ImageDraw
import subprocess

# ==== Simulated LLM output ====
product_name = "SuperSafe Annuity Plan"
product_features = [
    "Guaranteed lifetime income",
    "Flexible premium options",
    "Tax-deferred growth",
    "Optional death benefit"
]
narration_text = (
    "Introducing the SuperSafe Annuity Plan. "
    "It provides guaranteed lifetime income with flexible premium options. "
    "Your savings grow tax-deferred and include an optional death benefit."
)

# ==== Prepare outputs folder ====
os.makedirs("outputs", exist_ok=True)

# ==== 1️⃣ Create slides from features ====
slides = []
for i, feature in enumerate(product_features):
    img_path = os.path.abspath(os.path.join("outputs", f"slide_{i}.png"))
    img = Image.new("RGB", (640, 480), "white")
    d = ImageDraw.Draw(img)
    d.text((50, 200), feature, fill="black")
    img.save(img_path)
    slides.append(img_path)
    print(f"Created {img_path}")

# ==== 2️⃣ Save narration text to file (optional) ====
narration_path = os.path.abspath(os.path.join("outputs", "narration.txt"))
with open(narration_path, "w", encoding="utf-8") as f:
    f.write(narration_text)
print(f"Saved narration to {narration_path}")

# ==== 3️⃣ Create dummy audio for testing (2 sec silence) ====
audio_path = os.path.abspath(os.path.join("outputs", "test_audio.mp3"))
subprocess.run([
    "ffmpeg", "-y", "-f", "lavfi", "-i", "aevalsrc=0", "-t", "2", audio_path
], check=True)
print(f"Created {audio_path}")

# ==== 4️⃣ Create slides.txt for ffmpeg concat ====
list_file = os.path.abspath(os.path.join("outputs", "slides.txt"))
with open(list_file, "w") as f:
    for img in slides:
        f.write(f"file '{img}'\n")
        f.write("duration 2\n")
    f.write(f"file '{slides[-1]}'\n")  # repeat last frame

# ==== 5️⃣ Combine slides + audio into video ====
video_path = os.path.abspath(os.path.join("outputs", "test_video.mp4"))
subprocess.run([
    "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", list_file,
    "-i", audio_path, "-c:v", "libx264", "-pix_fmt", "yuv420p",
    "-c:a", "aac", "-shortest", video_path
], check=True)
print(f"Created {video_path}")

print("\n✅ Test completed! Check the outputs folder for slides, audio, and video.")
