from typing import List
from .models import VideoMarker
from .video_utils import detect_scenes
from pathlib import Path

def analyze_video(video_path: str) -> List[VideoMarker]:
    """
    Placeholder function: In production, call an LLM or video analysis model.
    Here, we return dummy markers.
    """
    temp_frame_dir = Path("./temp_frames")
    temp_frame_dir.mkdir(exist_ok=True)

    # Step 1: Detect scene changes → returns list of (frame_path, timestamp)
    scenes = detect_scenes(video_path, str(temp_frame_dir), threshold=0.3)

    markers = []
    for idx, (frame_path, timestamp) in enumerate(scenes):
        # Step 2: Generate a caption for each keyframe
        with open(frame_path, "rb") as f:
            frame_bytes = f.read()

        description = call_llm_image_caption(frame_bytes)

        # Step 3: Determine end time
        end_time = scenes[idx + 1][1] if idx + 1 < len(scenes) else timestamp + 5.0

        markers.append(VideoMarker(
            start_time=timestamp,
            end_time=end_time,
            summary=description
        ))

    return markers

def select_clips_based_on_prompt(video_markers: dict, prompt: str) -> List[str]:
    """
    Placeholder AI function: choose clips based on prompt.
    Returns list of paths to selected clips.
    """
    selected_clips = []

    for video_id, markers in video_markers.items():
        for marker in markers:
           
            # keep if prompt words appear in summary
            if any(word.lower() in marker.summary.lower() for word in prompt.split()):
                selected_clips.append({
                    "video_id": video_id,
                    "start": marker.start_time,
                    "end": marker.end_time,
                    "summary": marker.summary
                })

    return selected_clips


def call_llm_image_caption(image_bytes: bytes) -> str:
    """
    cohere
    Returns a short textual description of the image.
    """
    try:
        response = "cohere response"(
            model="cohere model",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant that describes the content of images in concise sentences."
                },
                {
                    "role": "user",
                    "content": "Describe this image in one short sentence."
                }
            ],
            input_images=[image_bytes],
            temperature=0.5
        )
        description = response.choices[0].message.content.strip()
        return description

    except Exception as e:
        print(f"Error calling LLM for image caption: {e}")
        return "Unable to describe frame"