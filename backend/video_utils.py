import subprocess

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

