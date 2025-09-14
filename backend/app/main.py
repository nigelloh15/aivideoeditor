from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import uuid
from fastapi import APIRouter
from fastapi.responses import JSONResponse

from .models import UploadVideoResponse, EditRequest, AnalyzeRequest
from .video_utils import cut_video, splice_videos, add_text_overlay, detect_scenes, extract_frames
from .ai_utils import save_instructions, load_instructions
from .cohere import CohereLLM
from .gemini import GeminiLLM

# Initialize FastAPI
app = FastAPI()

# Enable CORS for local testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or ["http://localhost:5500"] if serving HTML locally
    allow_methods=["*"],
    allow_headers=["*"],
)

# Video storage directories
VIDEO_DIR = Path("./videos/raw")
PROCESSED_DIR = Path("./videos/processed")
METADATA_DIR = Path("./videos/metadata")

VIDEO_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
METADATA_DIR.mkdir(parents=True, exist_ok=True)

# Serve processed videos for frontend preview/download
app.mount("/videos/processed", StaticFiles(directory=PROCESSED_DIR), name="processed")

# -------------------
# Choose your LLM here
# -------------------
# llm = CohereLLM()
llm = CohereLLM()

# -------------------
# API Endpoints
# -------------------



@app.get("/list-videos")
def list_videos():
    video_files = list(VIDEO_DIR.glob("*_*"))
    videos = []
    for file in video_files:
        video_id, filename = file.name.split("_", 1)
        videos.append({"video_id": video_id, "filename": filename})
    return JSONResponse(videos)



@app.post("/upload-video", response_model=UploadVideoResponse)
async def upload_video(file: UploadFile = File(...)):
    """
    Upload a video file.
    Returns a unique video_id for later processing.
    """
    print("Received file:", file.filename)
    video_id = str(uuid.uuid4())
    filename = file.filename or "unknown.mp4"
    file_path = VIDEO_DIR / f"{video_id}_{filename}"
    with open(file_path, "wb") as f:
        f.write(await file.read())
    return UploadVideoResponse(video_id=video_id, filename=filename)


@app.post("/analyze-video/{video_id}")
def analyze_video(video_id: str, request: AnalyzeRequest):
    """
    Analyze a video using Cohere AI.
    Extract 1 frame every 60 frames and generate editing instructions.
    Returns the instructions as JSON.
    """
    video_files = list(VIDEO_DIR.glob(f"{video_id}_*"))
    if not video_files:
        print(f"No video found for video_id={video_id}")
        return {"video_id": video_id, "instructions": []}

    video_path = str(video_files[0])
    print(f"Analyzing video: {video_path} with prompt: {request.prompt}")

    # 1. Extract frames every 60 frames (instead of scene detection)
    
    frames_dir = Path(f"./videos/temp_frames/{video_id}")
    frames_dir.mkdir(parents=True, exist_ok=True)

    # Extract frames every 60 frames
    frame_files = extract_frames(video_path, str(frames_dir), frame_interval=240)
    print(f"Extracted {len(frame_files)} frames for video {video_id}")

    instructions = []

    for i, (frame_path, timestamp) in enumerate(frame_files):
        try:
            # Convert Path to string
            desc_list = llm.generate_video_instructions(str(frame_path))
            summary = desc_list[0]["summary"] if desc_list else "No description"
        except Exception as e:
            print(f"Error in CohereLLM.generate_video_instructions: {e}")
            summary = "Error generating description"

        print(f"[Frame {i}] Timestamp: {timestamp:.2f}s -> AI sees: {summary}")

        instructions.append({
            "start": timestamp,
            "end": timestamp + 5,  # or any desired duration
            "summary": summary,
            "caption": summary
        })

    # 3. Save instructions
    save_instructions(video_id, instructions)
    print(f"Saved {len(instructions)} instructions for video {video_id}")

    return {"video_id": video_id, "instructions": instructions}





@app.post("/edit-video")
def edit_video(request: EditRequest):
    """
    Cut, splice, and optionally add captions to the videos based on LLM instructions.
    Returns the path to the final processed video.
    """
    all_clips = []

    for vid in request.video_ids:
        video_files = list(VIDEO_DIR.glob(f"{vid}_*"))
        if not video_files:
            continue
        video_path = str(video_files[0])
        instructions = load_instructions(vid)

        for idx, instr in enumerate(instructions):
            clip_path = PROCESSED_DIR / f"{vid}_clip_{idx}.mp4"
            cut_video(video_path, str(clip_path), start=instr["start"], end=instr["end"])

            if request.add_captions and instr.get("caption"):
                add_text_overlay(
                    str(clip_path),
                    str(clip_path),
                    instr["caption"],
                    start=0,
                    end=instr["end"] - instr["start"]
                )

            all_clips.append(str(clip_path))

    if not all_clips:
        return {"error": "No clips found to splice."}

    # Splice all clips together
    output_path = PROCESSED_DIR / f"{uuid.uuid4()}.mp4"
    splice_videos(all_clips, str(output_path))

    return {"output_video": f"videos/processed/{output_path.name}"}