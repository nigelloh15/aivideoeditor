from abc import ABC, abstractmethod
from typing import List, Dict

class LLMInterface(ABC):
    @abstractmethod
    def generate_video_instructions(
        self, video_path: str, user_prompt: str, max_clips: int = 10
    ) -> List[Dict]:
        """
        Generate JSON instructions for key video moments.
        Should return a list of dicts with:
        start, end, summary, caption
        """
        pass
