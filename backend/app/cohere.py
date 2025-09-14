import cohere
import json
from .llminterface import LLMInterface
import base64

COHERE_API_KEY = ""
MODEL = "c4ai-aya-vision-8b"

co = cohere.ClientV2(COHERE_API_KEY)
class CohereLLM(LLMInterface):
    def __init__(self):
        self.client = cohere.ClientV2(COHERE_API_KEY)

    def generate_video_instructions(self, frame_image_path, prompt="Describe this frame in exactly one concise sentence, including what is in it andwhat is happening. Could be a lengthy sentence depending on how detailed the image is."):
        try:
            # Encode frame as base64
            with open(frame_image_path, "rb") as img_file:
                base64_image = f"data:image/jpeg;base64,{base64.b64encode(img_file.read()).decode('utf-8')}"

            response = self.client.chat(
                model=MODEL,
                messages=[{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": base64_image}}
                    ]
                }],
                temperature=0.3,
            )

            text_output = response.message.content[0].text.strip()
            return [{"summary": text_output, "caption": text_output}]
        except Exception as e:
            print(f"Error in CohereLLM.generate_video_instructions: {e}")
            return [{"summary": "Error generating description", "caption": ""}]

    def select_and_order_clips(self, instructions, user_prompt: str):
        """
        Ask Cohere to go through all summary instructions and:
        1. Select clips relevant to the user prompt.
        2. Order them logically for storytelling.
        Returns a list of indices.
        """

        # Build summary text
        summaries_text = "\n".join(
            [f"[{i}] {instr['summary']}" for i, instr in enumerate(instructions)]
        )

        selection_prompt = f"""
        You are an expert video editor. The story is: "{user_prompt}"

        Available clips:
        {summaries_text}

        TASK:
        - Select only the clips that directly fit the story.
        - Order them logically for a coherent narrative.
        - Respond ONLY with a JSON array of integers.
        Example: [0, 2, 5, 7]
        """

        try:
            response = self.client.chat(
                model=MODEL,
                messages=[{"role": "user", "content": [{"type": "text", "text": selection_prompt}]}],
                temperature=0.3,
            )

            selection_text = response.message.content[0].text.strip()

            import re, json
            json_match = re.search(r"\[[0-9,\s]*\]", selection_text)

            if json_match:
                chosen_indices = json.loads(json_match.group(0))
            else:
                print("[WARN] No valid JSON returned by Cohere.")
                chosen_indices = []

            print(f"[DEBUG] User prompt: {user_prompt}")
            print(f"[DEBUG] LLM raw response: {selection_text}")
            print(f"[DEBUG] Chosen indices: {chosen_indices}")

            return chosen_indices

        except Exception as e:
            print(f"[ERROR] CohereLLM.select_and_order_clips: {e}")
            return []
