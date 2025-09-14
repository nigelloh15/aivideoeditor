import subprocess
import os
from pathlib import Path

def cut_video(input_path: str, output_path: str, start: float, end: float):
    subprocess.run([
        "ffmpeg", "-y", "-i", input_path,
        "-ss", str(start), "-to", str(end),
        "-c", "copy", output_path
    ])

def splice_videos(input_paths: list, output_path: str):
    # Create a temporary file for FFmpeg concat
    with open("inputs.txt", "w") as f:
        for path in input_paths:
            f.write(f"file '{path}'\n")
    subprocess.run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", "inputs.txt", "-c", "copy", output_path
    ])

def add_text_overlay(input_path: str, output_path: str, text: str, start: float, end: float):
    subprocess.run([
        "ffmpeg", "-y", "-i", input_path,
        "-vf", f"drawtext=text='{text}':x=10:y=H-th-10:enable='between(t,{start},{end})'",
        "-c:a", "copy", output_path
    ])


def extract_frames(input_path: str, output_dir: str, frame_interval: int = 240):
    """
    Extract one frame every `frame_interval` frames and return timestamps.
    Returns a list of (frame_path, timestamp_in_seconds).
    """
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    output_pattern = os.path.join(output_dir, "frame_%06d.jpg")

    # Run FFmpeg with select and showinfo to get timestamps
    process = subprocess.Popen([
        "ffmpeg", "-y", "-i", input_path,
        "-vf", f"select='not(mod(n\\,{frame_interval}))',showinfo",
        "-vsync", "vfr", output_pattern
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    _, stderr = process.communicate()

    if process.returncode != 0:
        raise RuntimeError(f"Frame extraction failed:\n{stderr}")

    # Parse timestamps from FFmpeg logs
    timestamps = []
    for line in stderr.splitlines():
        if "pts_time:" in line:
            try:
                ts = float(line.split("pts_time:")[-1].split()[0])
                timestamps.append(ts)
            except Exception:
                continue

    images = sorted(Path(output_dir).glob("frame_*.jpg"))
    
    # Return list of tuples: (frame_path, timestamp)
    return list(zip(images, timestamps))



def detect_scenes(input_path: str, output_dir: str, threshold: float = 0.4):
    """
    Detect scene changes using FFmpeg and save keyframes.
    Returns a list of (frame_path, timestamp).
    """
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    output_pattern = os.path.join(output_dir, "scene_%06d.jpg")

    # Run ffmpeg with scene detection
    process = subprocess.Popen([
        "ffmpeg", "-y", "-i", input_path,
        "-vf", f"select='gt(scene,{threshold})',showinfo",
        "-vsync", "vfr", output_pattern
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    _, stderr = process.communicate()

    if process.returncode != 0:
        raise RuntimeError(f"Scene detection failed:\n{stderr}")

    # Parse timestamps from stderr logs
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