from pydantic import BaseModel
from typing import List

class AnalyzeRequest(BaseModel):
    prompt: str
    blacklist: List[str] =[]

class UploadVideoResponse(BaseModel):
    video_id: str
    filename: str

class VideoMarker(BaseModel):
    start_time: float
    end_time: float
    summary: str

class VideoSummaryResponse(BaseModel):
    video_id: str
    markers: List[VideoMarker]

class EditRequest(BaseModel):
    video_ids: List[str]
    prompt: str
    add_captions: bool = True
