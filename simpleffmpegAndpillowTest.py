import os
from PIL import Image, ImageDraw
import subprocess

# Make outputs folder
os.makedirs("outputs", exist_ok=True)

# 1️⃣ Create slides
slides = []
for i, text in enumerate(["Slide 1: Hello", "Slide 2: World"]):
    img_path = os.path.abspath(os.path.join("outputs", f"slide_{i}.png"))
    img = Image.new("RGB", (640, 480), "white")
    d = ImageDraw.Draw(img)
    d.text((50, 200), text, fill="black")
    img.save(img_path)
    slides.append(img_path)
    print(f"Created {img_path}")

# 2️⃣ Create dummy audio
audio_path = os.path.abspath(os.path.join("outputs", "test_audio.mp3"))
subprocess.run([
    "ffmpeg", "-y", "-f", "lavfi", "-i", "aevalsrc=0", "-t", "2", audio_path
], check=True)
print(f"Created {audio_path}")

# 3️⃣ Prepare slides.txt with absolute paths
list_file = os.path.abspath(os.path.join("outputs", "slides.txt"))
with open(list_file, "w") as f:
    for img in slides:
        f.write(f"file '{img}'\n")
        f.write("duration 2\n")
    f.write(f"file '{slides[-1]}'\n")  # repeat last frame

# 4️⃣ Combine slides + audio into video
video_path = os.path.abspath(os.path.join("outputs", "test_video.mp4"))
subprocess.run([
    "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", list_file,
    "-i", audio_path, "-c:v", "libx264", "-pix_fmt", "yuv420p",
    "-c:a", "aac", "-shortest", video_path
], check=True)
print(f"Created {video_path}")
