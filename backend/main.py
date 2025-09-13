from fastapi import FastAPI, UploadFile, File
from pathlib import Path
import uuid
from typing import List
from .models import UploadVideoResponse, VideoMarker, VideoSummaryResponse, EditRequest
from .video_utils import cut_video, splice_videos, add_text_overlay
from .ai_utils import analyze_video, select_clips_based_on_prompt

app = FastAPI()

VIDEO_DIR = Path("./videos/raw")
PROCESSED_DIR = Path("./videos/processed")
METADATA_DIR = Path("./videos/metadata")

VIDEO_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
METADATA_DIR.mkdir(parents=True, exist_ok=True)

@app.post("/upload-video", response_model=UploadVideoResponse)
async def upload_video(file: UploadFile = File(...)):
    video_id = str(uuid.uuid4())
    filename = file.filename or "unknown.mp4"  # fallback if None
    file_path = VIDEO_DIR / f"{video_id}_{filename}"
    with open(file_path, "wb") as f:
        f.write(await file.read())
    return UploadVideoResponse(video_id=video_id, filename=filename)

@app.get("/analyze-video/{video_id}", response_model=VideoSummaryResponse)
def analyze(video_id: str):
    # Find video file
    video_files = list(VIDEO_DIR.glob(f"{video_id}_*"))
    if not video_files:
        return {"video_id": video_id, "markers": []}
    
    video_path = video_files[0]
    markers = analyze_video(str(video_path))
    
    # Optionally save markers to JSON for later
    import json
    with open(METADATA_DIR / f"{video_id}.json", "w") as f:
        json.dump([marker.dict() for marker in markers], f)
    
    return VideoSummaryResponse(video_id=video_id, markers=markers)

@app.post("/edit-video")
def edit_video(request: EditRequest):
    # Load markers for all videos
    video_markers = {}
    import json
    for vid in request.video_ids:
        metadata_file = METADATA_DIR / f"{vid}.json"
        if metadata_file.exists():
            with open(metadata_file, "r") as f:
                markers_json = json.load(f)
                video_markers[vid] = [VideoMarker(**m) for m in markers_json]
        else:
            video_markers[vid] = []
    
    # AI selects clips based on prompt
    selected_clips = select_clips_based_on_prompt(video_markers, request.prompt)
    
    # Cut selected clips into separate files
    cut_clip_paths = []
    for idx, clip_path in enumerate(selected_clips):
        cut_path = PROCESSED_DIR / f"clip_{idx}.mp4"
        cut_video(clip_path, str(cut_path), start=0, end=5)  # Placeholder 5-second cuts
        cut_clip_paths.append(str(cut_path))
    
    # Splice clips together
    output_video_path = PROCESSED_DIR / f"{uuid.uuid4()}.mp4"
    splice_videos(cut_clip_paths, str(output_video_path))
    
    # Add captions if requested
    if request.add_captions:
        add_text_overlay(str(output_video_path), str(output_video_path), "Sample Caption", 0, 5)
    
    return {"output_video": str(output_video_path)}
