import cohere
import json
from .llminterface import LLMInterface
import base64
COHERE_API_KEY = "api"
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