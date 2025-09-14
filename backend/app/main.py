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
    Extract 1 frame every 240 frames and generate editing instructions.
    Skips frames/clips containing blacklisted words.
    """
    video_files = list(VIDEO_DIR.glob(f"{video_id}_*"))
    if not video_files:
        print(f"No video found for video_id={video_id}")
        return {"video_id": video_id, "instructions": []}

    video_path = str(video_files[0])
    print(f"Analyzing video: {video_path} with prompt: {request.prompt}")
    print(f"Using blacklist: {request.blacklist}")

    # Create temporary frames directory
    frames_dir = Path(f"./videos/temp_frames/{video_id}")
    frames_dir.mkdir(parents=True, exist_ok=True)

    # Extract frames every 240 frames
    frame_files = extract_frames(video_path, str(frames_dir), frame_interval=30)
    print(f"Extracted {len(frame_files)} frames for video {video_id}")

    instructions = []

    for i, (frame_path, timestamp) in enumerate(frame_files):
        try:
            desc_list = llm.generate_video_instructions(str(frame_path))
            summary = desc_list[0]["summary"] if desc_list else "No description"
        except Exception as e:
            print(f"Error in CohereLLM.generate_video_instructions: {e}")
            summary = "Error generating description"

        # Check against blacklist
        if any(black_word.lower() in summary.lower() for black_word in request.blacklist):
            print(f"[Frame {i}] Skipped due to blacklist match: {summary}")
            continue

        print(f"[Frame {i}] Timestamp: {timestamp:.2f}s -> AI sees: {summary}")

        next_timestamp = frame_files[i+1][1] if i+1 < len(frame_files) else timestamp + 2
        instructions.append({
            "start": timestamp,
            "end": next_timestamp,
            "summary": summary,
            "caption": summary
        })
    # Save instructions
    save_instructions(video_id, instructions)
    print(f"Saved {len(instructions)} instructions for video {video_id}")

    return {"video_id": video_id, "instructions": instructions}

@app.post("/edit-video")
def edit_video(request: EditRequest):
    """
    Cut, splice, and optionally add captions to videos based on LLM instructions.
    Uses 1-second sub-chunks to detect blacklisted words and trims 3 seconds
    if blacklisted content appears mid-chunk. Returns the path to the final video.
    """
    import uuid
    all_clips = []

    for vid in request.video_ids:
        video_files = list(VIDEO_DIR.glob(f"{vid}_*"))
        if not video_files:
            print(f"No video file found for {vid}, skipping.")
            continue
        video_path = str(video_files[0])
        instructions = load_instructions(vid)
        if not instructions:
            print(f"No instructions found for {vid}, skipping.")
            continue

        # Prepare blacklist words
        blacklist_words = [word.strip().lower() for word in request.prompt.split(",") if word.strip()]

        # 1️⃣ Split into 1-second sub-chunks
        mini_chunk_length = 1.0
        processed_chunks = []

        for instr in instructions:
            start = instr["start"]
            while start < instr["end"]:
                end = min(start + mini_chunk_length, instr["end"])

                # Here, generate per-second summary if possible
                # For now we assume instr['summary'] applies to all sub-chunks
                chunk_text = (instr.get("summary", "") + " " + instr.get("caption", "")).lower()

                # 2️⃣ Check blacklist per sub-chunk
                if any(word in chunk_text for word in blacklist_words):
                    # Trim 3 seconds before the blacklisted word
                    print(f"Blacklisted word detected at {start}-{end}, trimming 3 seconds")
                    end = max(start, end - 3.0)
                    if end <= start:
                        start += mini_chunk_length
                        continue

                processed_chunks.append({
                    "start": start,
                    "end": end,
                    "summary": instr["summary"],
                    "caption": instr["caption"]
                })
                start = end

        if not processed_chunks:
            print(f"All clips were removed due to blacklisted words for video {vid}.")
            continue

        # 3️⃣ Merge consecutive safe sub-chunks
        merged_chunks = []
        for chunk in processed_chunks:
            if not merged_chunks:
                merged_chunks.append(chunk.copy())
            else:
                last = merged_chunks[-1]
                if chunk["start"] <= last["end"]:  # overlapping or consecutive
                    last["end"] = chunk["end"]
                    last["summary"] += " " + chunk["summary"]
                    last["caption"] += " " + chunk["caption"]
                else:
                    merged_chunks.append(chunk.copy())

        # 4️⃣ Cut clips and optionally add captions
        for idx, instr in enumerate(merged_chunks):
            clip_path = PROCESSED_DIR / f"{vid}_clip_{idx}.mp4"
            try:
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
                print(f"Clip added: {clip_path}")
            except Exception as e:
                print(f"Failed to process clip {idx} for video {vid}: {e}")
                continue

    if not all_clips:
        return {"error": "No clips found to splice."}

    # 5️⃣ Splice all clips together
    output_path = PROCESSED_DIR / f"{uuid.uuid4()}.mp4"
    splice_videos([str(Path(c).resolve()) for c in all_clips], str(output_path))
    print(f"Final video created: {output_path}")

    return {"output_video": f"videos/processed/{output_path.name}"}
