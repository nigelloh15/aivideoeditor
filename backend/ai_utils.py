from typing import List
from .models import VideoMarker
import random

def analyze_video(video_path: str) -> List[VideoMarker]:
    """
    Placeholder function: In production, call an LLM or video analysis model.
    Here, we return dummy markers.
    """
    # For example purposes, generate 2-3 random markers
    markers = []
    for i in range(random.randint(2, 4)):
        start = i * 5
        end = start + 5
        markers.append(VideoMarker(start_time=start, end_time=end, summary=f"Scene {i+1}"))
    return markers

def select_clips_based_on_prompt(video_markers: dict, prompt: str) -> List[str]:
    """
    Placeholder AI function: choose clips based on prompt.
    Returns list of paths to selected clips.
    """
    selected_clips = []
    for video_id, markers in video_markers.items():
        for idx, marker in enumerate(markers):
            if "Scene" in marker.summary:  # dummy selection
                selected_clips.append(f"./videos/raw/{video_id}_{idx}.mp4")
    return selected_clips

