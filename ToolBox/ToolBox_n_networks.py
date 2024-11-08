import requests, json, base64, os, io
from g4f.client import Client
from Images import Text2ImageAPI
from PIL import Image

# Neural networks class
class neural_networks:
    
#Protected
    def _gpt_4o(self, prompt: list[dict]) -> tuple[str, int]|None:
        client = Client()
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=prompt
        )
        return response.choices[0].message.content, response.usage["prompt_tokens"], response.usage["completion_tokens"]

    # FLUX.1-schnell request
    def _FLUX_schnell(self, prompt: str) -> str|None:
        data = {"Authorization": "Bearer " + os.environ['HF_TOKEN'], "Content-Type": "application/json"}
        payload = {
            "inputs": prompt,
        }
        response = requests.post("https://api-inference.huggingface.co/models/black-forest-labs/FLUX.1-schnell", headers=data, json=payload).content
        image = Image.open(io.BytesIO(response))
        return image