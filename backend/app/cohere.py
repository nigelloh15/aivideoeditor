import cohere
import json
from .llminterface import LLMInterface

COHERE_API_KEY = "YOUR_COHERE_API_KEY"

class CohereLLM(LLMInterface):
    def __init__(self):
        self.client = cohere.Client(COHERE_API_KEY)

    def generate_video_instructions(self, video_path: str, user_prompt: str, max_clips: int = 10):
        prompt = f"""
        You are a video editing assistant.
        The video is at {video_path}.
        The user wants: {user_prompt}.
        Identify up to {max_clips} key moments.
        For each moment, output JSON with start, end, summary, caption.
        """
        response = self.client.generate(
            model="xlarge",
            prompt=prompt,
            max_tokens=500,
            temperature=0.5
        )

        if response.generations and len(response.generations) > 0:
            text_output = response.generations[0].text.strip()
        else:
            text_output = ""

        try:
            instructions = json.loads(text_output)
        except json.JSONDecodeError:
            instructions = []

        return instructions
