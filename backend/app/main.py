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
    Step 1: Analyze ALL input videos and generate clip summaries.
    Step 2: Feed ALL summaries to the LLM with the user story prompt.
    Step 3: Cut ONLY the chosen clips, move them into a 'chosen' folder,
            and splice ONLY those clips into the final processed video.
    """
    all_instructions = {}  # {video_id: [instructions]}
    llm = CohereLLM()

    # --- Cleanup chosen clips folder ---
    CHOSEN_DIR = Path("./videos/chosen")
    CHOSEN_DIR.mkdir(parents=True, exist_ok=True)

    # --- Phase 1: Analyze all videos ---
    for vid in request.video_ids:
        video_files = list(VIDEO_DIR.glob(f"{vid}_*"))
        if not video_files:
            print(f"⚠️ No video found for video_id={vid}")
            continue

        video_path = str(video_files[0])
        print(f"📹 Analyzing video: {video_path}")

        frames_dir = Path(f"./videos/temp_frames/{vid}")
        frames_dir.mkdir(parents=True, exist_ok=True)

        # Extract frames (every 300 frames ~ every 10s for 30fps)
        frame_files = extract_frames(video_path, str(frames_dir), frame_interval=300)
        print(f"✅ Extracted {len(frame_files)} frames for {vid}")

        instructions = []
        for i, (frame_path, timestamp) in enumerate(frame_files):
            try:
                desc_list = llm.generate_video_instructions(str(frame_path))
                summary = desc_list[0]["summary"] if desc_list else "No description"
            except Exception as e:
                print(f"❌ Error generating description for {vid}, frame {i}: {e}")
                summary = "Error generating description"

            instructions.append({
                "video_id": vid,
                "frame_index": i,
                "start": timestamp,
                "end": timestamp + 5,  # configurable
                "summary": summary,
                "caption": summary
            })

        save_instructions(vid, instructions)
        all_instructions[vid] = instructions

    if not all_instructions:
        return {"error": "No videos analyzed."}

    # --- Phase 2: LLM selects across ALL videos ---
    all_clips_info = []
    for vid, instrs in all_instructions.items():
        all_clips_info.extend(instrs)

    print(f"📝 Sending {len(all_clips_info)} summaries to LLM for story matching...")
    print(all_clips_info)
    chosen_indices = llm.select_and_order_clips(all_clips_info, request.prompt)

    print(f"🎯 LLM chose {len(chosen_indices)} clips (global indices).")

    # --- Phase 3: Cut + move chosen clips ---
    chosen_clip_paths = []
    for idx in chosen_indices:
        if idx < 0 or idx >= len(all_clips_info):
            print(f"⚠️ Skipping invalid global index {idx}")
            continue

        instr = all_clips_info[idx]
        vid = instr["video_id"]

        video_files = list(VIDEO_DIR.glob(f"{vid}_*"))
        if not video_files:
            continue
        video_path = str(video_files[0])

        clip_path = CHOSEN_DIR / f"{vid}_clip_{instr['frame_index']}.mp4"

        print(f"✂️ Cutting chosen clip {instr['frame_index']} from {vid} "
              f"({instr['start']}s → {instr['end']}s)")
        cut_video(video_path, str(clip_path), start=instr["start"], end=instr["end"])

        chosen_clip_paths.append(str(clip_path))

    if not chosen_clip_paths:
        return {"error": "No clips chosen for final edit."}

    # --- Splice ONLY chosen clips ---
    output_path = PROCESSED_DIR / f"{uuid.uuid4()}.mp4"
    print(f"📀 Splicing {len(chosen_clip_paths)} chosen clips into final video...")
    splice_videos(chosen_clip_paths, str(output_path))

    return {"output_video": f"videos/processed/{output_path.name}"}
