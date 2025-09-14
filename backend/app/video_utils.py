import subprocess
import os
from pathlib import Path
import uuid
import shutil

def safe_output_path(path: str) -> str:
    """Return a temporary path in the same directory as `path`."""
    directory, filename = os.path.split(path)
    temp_filename = f".tmp_{uuid.uuid4().hex}_{filename}"
    return os.path.join(directory, temp_filename)

def replace_with_temp(temp_path: str, final_path: str):
    """Replace the final path with temp path safely."""
    shutil.move(temp_path, final_path)

def cut_video(input_path: str, output_path: str, start: float, end: float):
    temp_path = safe_output_path(output_path)
    subprocess.run([
        "ffmpeg", "-y", "-i", input_path,
        "-ss", str(start), "-to", str(end),
        "-c", "copy", temp_path
    ], check=True)
    replace_with_temp(temp_path, output_path)

def splice_videos(input_paths: list, output_path: str):
    temp_path = safe_output_path(output_path)
    # Create a temporary concat file
    concat_file = safe_output_path("inputs.txt")
    with open(concat_file, "w") as f:
        for path in input_paths:
            f.write(f"file '{path}'\n")
    subprocess.run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", concat_file, "-c", "copy", temp_path
    ], check=True)
    os.remove(concat_file)
    replace_with_temp(temp_path, output_path)

def add_text_overlay(input_path: str, output_path: str, text: str, start: float, end: float):
    temp_path = safe_output_path(output_path)
    subprocess.run([
        "ffmpeg", "-y", "-i", input_path,
        "-vf", f"drawtext=text='{text}':x=10:y=H-th-10:enable='between(t,{start},{end})'",
        "-c:a", "copy", temp_path
    ], check=True)
    replace_with_temp(temp_path, output_path)

def extract_frames(input_path: str, output_dir: str, frame_interval: int =30):
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    output_pattern = os.path.join(output_dir, "frame_%06d.jpg")

    process = subprocess.Popen([
        "ffmpeg", "-y", "-i", input_path,
        "-vf", f"select='not(mod(n\\,{frame_interval}))',showinfo",
        "-vsync", "vfr", output_pattern
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    _, stderr = process.communicate()
    if process.returncode != 0:
        raise RuntimeError(f"Frame extraction failed:\n{stderr}")

    timestamps = []
    for line in stderr.splitlines():
        if "pts_time:" in line:
            try:
                ts = float(line.split("pts_time:")[-1].split()[0])
                timestamps.append(ts)
            except Exception:
                continue

    images = sorted(Path(output_dir).glob("frame_*.jpg"))
    return list(zip(images, timestamps))

def detect_scenes(input_path: str, output_dir: str, threshold: float = 0.4):
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    output_pattern = os.path.join(output_dir, "scene_%06d.jpg")

    process = subprocess.Popen([
        "ffmpeg", "-y", "-i", input_path,
        "-vf", f"select='gt(scene,{threshold})',showinfo",
        "-vsync", "vfr", output_pattern
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    _, stderr = process.communicate()
    if process.returncode != 0:
        raise RuntimeError(f"Scene detection failed:\n{stderr}")

    timestamps = []
    for line in stderr.splitlines():
        if "pts_time:" in line:
            try:
                ts = float(line.split("pts_time:")[-1].split()[0])
                timestamps.append(ts)
            except Exception:
                continue

    images = sorted(Path(output_dir).glob("scene_*.jpg"))
    return list(zip(images, timestamps))
