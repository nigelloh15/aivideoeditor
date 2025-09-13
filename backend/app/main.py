from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import uuid

from .models import UploadVideoResponse, EditRequest, AnalyzeRequest
from .video_utils import cut_video, splice_videos, add_text_overlay
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
llm = GeminiLLM(api_key="AIzaSyCFlkoltYGCpeBKkSEdQ8q-e58LTsGuuw8")

# -------------------
# API Endpoints
# -------------------

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
    video_files = list(VIDEO_DIR.glob(f"{video_id}_*"))
    if not video_files:
        return {"video_id": video_id, "instructions": []}

    video_path = str(video_files[0])
    instructions = llm.generate_video_instructions(video_path, request.prompt)
    save_instructions(video_id, instructions)
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
