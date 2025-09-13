# /tools/video.py
import subprocess, os
from strands import tool

@tool
def render_video(images: list, audio: str, out_path: str) -> str:
    """
    Combine slides + narration into a video using ffmpeg.
    """
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    out_dir = os.path.dirname(out_path)
    listf = os.path.join(out_dir, "slides.txt")

    with open(listf, "w", encoding="utf-8") as f:
        for img in images:
            f.write(f"file '{os.path.abspath(img)}'\n")
            f.write("duration 5\n")
        f.write(f"file '{os.path.abspath(images[-1])}'\n")

    cmd = [
        "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", listf,
        "-i", os.path.abspath(audio), "-c:v", "libx264", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-shortest", os.path.abspath(out_path)
    ]
    subprocess.run(cmd, check=True)
    return out_path
