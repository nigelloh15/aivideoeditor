import json
import re
import tempfile
import os
from pathlib import Path
from typing import List, Dict

import cv2
import google.generativeai as genai
from .llminterface import LLMInterface


class GeminiLLM(LLMInterface):
    def __init__(self, api_key: str, model: str = "gemini-1.5-flash"):
        self.api_key = api_key
        genai.configure(api_key=self.api_key)
        self.model = model

    def _extract_frames(self, video_path: str, step: int = 5) -> List[str]:
        """
        Extract every 1/step-th frame from video and save to temp files.
        Returns list of image file paths.
        """
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError(f"Cannot open video: {video_path}")

        idx = 0
        saved = 0
        tmpdir = tempfile.mkdtemp()
        img_paths = []

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            if idx % step == 0:
                frame_path = os.path.join(tmpdir, f"frame_{saved}.jpg")
                cv2.imwrite(frame_path, frame)
                img_paths.append(frame_path)
                saved += 1

            idx += 1

        cap.release()
        return img_paths

    def generate_video_instructions(
        self, video_path: str, user_prompt: str, max_clips: int = 10
    ) -> List[Dict]:
        """
        Generates detailed key moment instructions from a video using Gemini.
        """
        # Extract frames
        frame_paths = self._extract_frames(video_path, step=5)

        # Build prompt text
        prompt_text = f"""
        You are a video editing assistant.
        The user wants: {user_prompt}.
        The frames below are sampled from the video ({len(frame_paths)} total).
        Identify up to {max_clips} key moments.
        For each key moment, give:
          - start: number (seconds, approximate)
          - end: number (seconds, approximate)
          - summary: detailed description of what happens
          - caption: optional short caption text

        Output only a JSON array like:
        [
          {{"start":0, "end":5, "summary":"...", "caption":"..."}},
          ...
        ]
        """

        # Gemini expects a list of file paths for images directly
        images_to_send = frame_paths[:20]  # limit to first 20 frames

        model = genai.GenerativeModel(self.model)
        response = model.generate_content(
            text=[prompt_text],
            images=images_to_send
        )

        # Extract text output
        text_output = ""
        if hasattr(response, "text") and response.text:
            text_output = response.text.strip()
        elif hasattr(response, "candidates") and response.candidates:
            parts = response.candidates[0].content.parts
            if parts and hasattr(parts[0], "text"):
                text_output = parts[0].text.strip()

        if not text_output:
            print("⚠️ Gemini returned no text response")
            return []

        # Strip Markdown fences (```json ... ```)
        if text_output.startswith("```"):
            text_output = re.sub(r"^```[a-zA-Z]*\n?", "", text_output)
            text_output = re.sub(r"\n?```$", "", text_output)

        # Parse JSON
        try:
            instructions = json.loads(text_output)
        except json.JSONDecodeError:
            print("⚠️ Gemini output was not valid JSON, raw:", repr(text_output))
            instructions = []

        return instructions
