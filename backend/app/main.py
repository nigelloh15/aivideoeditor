from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import uuid
from fastapi import APIRouter
from fastapi.responses import JSONResponse

from .models import UploadVideoResponse, EditRequest, AnalyzeRequest
from .video_utils import cut_video, splice_videos, extract_frames
from .ai_utils import save_instructions, load_instructions
from .cohere import CohereLLM

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
    frame_files = extract_frames(video_path, str(frames_dir), frame_interval=300)
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
    Analyze videos with Cohere AI, select only the clips that match the story,
    and splice ONLY those chosen clips into the final processed video.
    """
    all_clips = []

    llm = CohereLLM()

    for vid in request.video_ids:
        video_files = list(VIDEO_DIR.glob(f"{vid}_*"))
        if not video_files:
            print(f"⚠️ No video found for video_id={vid}")
            continue

        video_path = str(video_files[0])
        print(f"Analyzing + Editing video: {video_path} with prompt: {request.prompt}")

        # --- Step 1: Extract frames ---
        frames_dir = Path(f"./videos/temp_frames/{vid}")
        frames_dir.mkdir(parents=True, exist_ok=True)

        frame_files = extract_frames(video_path, str(frames_dir), frame_interval=300)
        print(f"✅ Extracted {len(frame_files)} frames for video {vid}")

        # --- Step 2: Generate AI instructions for each frame ---
        instructions = []
        for i, (frame_path, timestamp) in enumerate(frame_files):
            try:
                desc_list = llm.generate_video_instructions(str(frame_path))
                summary = desc_list[0]["summary"] if desc_list else "No description"
            except Exception as e:
                print(f"❌ Error in CohereLLM.generate_video_instructions: {e}")
                summary = "Error generating description"

            print(f"[Frame {i}] Timestamp: {timestamp:.2f}s -> AI sees: {summary}")

            instructions.append({
                "start": timestamp,
                "end": timestamp + 5,  # configurable duration
                "summary": summary,
                "caption": summary
            })

        # Save instructions (debugging / auditing)
        save_instructions(vid, instructions)

        # --- Step 3: Use LLM to EXPLICITLY choose clips ---
        chosen_indices = llm.select_and_order_clips(instructions, request.prompt)
        print(f"🎯 LLM explicitly chose clip indices for {vid}: {chosen_indices}")

        # --- Step 4: ONLY cut the explicitly chosen clips ---
        for idx in chosen_indices:
            if idx < 0 or idx >= len(instructions):
                print(f"⚠️ Skipping invalid index {idx} (out of bounds for {vid})")
                continue

            instr = instructions[idx]
            clip_path = PROCESSED_DIR / f"{vid}_clip_{idx}.mp4"

            print(f"✂️ Cutting clip {idx} from {instr['start']}s to {instr['end']}s for {vid}")
            cut_video(video_path, str(clip_path), start=instr["start"], end=instr["end"])

            # ✅ ONLY append clips that were chosen
            all_clips.append(str(clip_path))

    if not all_clips:
        print("❌ No clips chosen by the LLM, nothing to splice.")
        return {"error": "No clips matched the story."}

    # --- Step 5: Splice ONLY the chosen clips ---
    output_path = PROCESSED_DIR / f"{uuid.uuid4()}.mp4"
    print(f"📀 Splicing {len(all_clips)} explicitly chosen clips into final video...")
    splice_videos(all_clips, str(output_path))

    return {"output_video": f"videos/processed/{output_path.name}"}
