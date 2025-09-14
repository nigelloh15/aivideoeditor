import cohere
import json
from .llminterface import LLMInterface
import base64
COHERE_API_KEY = "UlwKB40GjK7AB6opxyiGwDJ1DDUXSTFUMEDGdnyE"  # <- replace this
MODEL = "c4ai-aya-vision-8b"
co = cohere.ClientV2(COHERE_API_KEY)
class CohereLLM(LLMInterface):
    def __init__(self):
        self.client = cohere.ClientV2(COHERE_API_KEY)

    def generate_video_instructions(self, frame_image_path, prompt="Describe this frame in exactly one concise sentence. Could be a lengthy sentence depending on how detailed the image is."):
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
        1. Select all clips relevant to the user prompt.
        2. Determine a logical order.
        Returns a list of indices corresponding to instructions.

        instructions: list of dicts with 'start', 'end', 'summary', 'caption'
        """
        # Prepare summaries text
        summaries_text = "\n".join(
            [f"[{i}] {instr['summary']}" for i, instr in enumerate(instructions)]
        )

        selection_prompt = f"""
        You are an expert video editor. The user gave the prompt: "{user_prompt}".

        Here are all clip summaries:
        {summaries_text}

        TASK:
        1. Include ALL clips that match the prompt.
        2. Order them logically for coherent storytelling.
        3. Respond ONLY with a JSON array of the selected clip indices in order.
        Example: [0, 2, 5, 7]
        """

        try:
            response = self.client.chat(
                model=MODEL,
                messages=[{"role": "user", "content": [{"type": "text", "text": selection_prompt}]}],
                temperature=0.3,
            )

            selection_text = response.message.content[0].text.strip()

            # Extract first JSON array from response
            import re
            import json

            json_match = re.search(r"\[[^\]]*\]", selection_text)
            if json_match:
                chosen_indices = json.loads(json_match.group(0))
            else:
                print("Warning: Cohere returned no JSON, selecting all clips by default.")
                chosen_indices = list(range(len(instructions)))

            return chosen_indices

        except Exception as e:
            print(f"Error in CohereLLM.select_and_order_clips: {e}")
            # fallback: include all clips in chronological order
            return list(range(len(instructions)))
