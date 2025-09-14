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
    # Always re-encode for iPhone MOV
    temp_path = str(Path(output_path).with_suffix(".tmp.mp4"))
    subprocess.run([
        "ffmpeg", "-y", "-i", input_path,
        "-ss", str(start), "-to", str(end),
        "-c:v", "libx264", "-preset", "fast", "-crf", "23",
        "-c:a", "aac", temp_path
    ], check=True)
    os.replace(temp_path, output_path)

def splice_videos(input_paths: list, output_path: str):
    # Cleanup any leftover temp files before starting
    for f in Path(".").glob("*_tmp.mp4"):
        f.unlink()

    temp_files = []
    for idx, path in enumerate(input_paths):
        tmp = f"{Path(path).stem}_tmp.mp4"
        subprocess.run([
            "ffmpeg", "-y", "-i", path,
            "-c:v", "libx264", "-preset", "fast", "-crf", "23",
            "-c:a", "aac", tmp
        ], check=True)
        temp_files.append(tmp)

    concat_file = "concat_list.txt"
    with open(concat_file, "w") as f:
        for file in temp_files:
            f.write(f"file '{os.path.abspath(file)}'\n")

    subprocess.run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", concat_file,
        "-c", "copy", output_path
    ], check=True)

    os.remove(concat_file)
    for f in temp_files:
        os.remove(f)

def extract_frames(input_path: str, output_dir: str, frame_interval: int = 240):
    temp_path = safe_output_path(output_path)
    subprocess.run([
        "ffmpeg", "-y", "-i", input_path,
        "-ss", str(start), "-to", str(end),
        "-c", "copy", temp_path
    ], check=True)
    replace_with_temp(temp_path, output_path)

def splice_videos(input_paths: list, output_path: str):
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