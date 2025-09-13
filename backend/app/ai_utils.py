from pathlib import Path
import json

def save_instructions(video_id: str, instructions: list):
    Path("./videos/metadata").mkdir(exist_ok=True)
    with open(f"./videos/metadata/{video_id}_instructions.json", "w") as f:
        json.dump(instructions, f, indent=2)

def load_instructions(video_id: str):
    try:
        with open(f"./videos/metadata/{video_id}_instructions.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []
