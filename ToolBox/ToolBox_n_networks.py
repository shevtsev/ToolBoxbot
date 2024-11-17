import requests, json, os, io
from random import randint
from g4f.client import Client
from PIL import Image

# Neural networks class
class neural_networks:
    
#Protected
    def _gpt_4o_mini(self, prompt: list[dict[str, str]]) -> tuple[str, int, int]|None:
        client = Client()
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=prompt,
            max_tokens=1024
        )
        return response.choices[0].message.content, response.usage["prompt_tokens"], response.usage["completion_tokens"]

    # FLUX.1-schnell request
    def _FLUX_schnell(self, prompt: str, size: list[int, int]) -> str|None:
        data = {"Authorization": "Bearer " + os.environ['HF_TOKEN'], "Content-Type": "application/json"}
        payload = {
            "inputs": prompt,
            "parameters": {
                "guidance_scale": 1.5,
                "num_inference_steps": 5,
                "width": size[0],
                "height": size[1],
                "seed": randint(1, 1000000)
            }
        }
        response = requests.post("https://api-inference.huggingface.co/models/black-forest-labs/FLUX.1-schnell", headers=data, json=payload).content
        image = Image.open(io.BytesIO(response))
        return image
    
    def __mistral_large_2407(self, prompt: list[dict[str, str]]) -> tuple[str, int, int]|str:
        data = {
            "messages": prompt,
            "temperature": 1.0,
            "top_p": 1.0,
            "max_tokens": 1024,
            "model": "mistral-large-2407"
        }
        response = requests.post("https://api.mistral.ai/v1/chat/completions", headers={"Content-Type": "application/json", "Authorization": "Bearer "+ os.environ['MISTRAL_TOKEN']},
                                json=data)
        response = json.loads(response.text)
        return response['choices'][0]['message']['content'], response['usage']['prompt_tokens'], response['usage']['completion_tokens']

    def _free_gpt_4o_mini(self, prompt: list[dict[str, str]]) -> tuple[str, int, int]|str:
        data = {
            "messages": prompt,
            "temperature": 1.0,
            "top_p": 1.0,
            "max_tokens": 1024,
            "model": "gpt-4o-mini"
        }
        for i in range(1, 6):
            response = requests.post("https://models.inference.ai.azure.com/chat/completions", headers={"Authorization": os.environ[f'GIT_TOKEN{i}'], "Content-Type" : "application/json"},
                                    json=data)
            if response.status_code == 200:
                response = json.loads(response.text)
                return response['choices'][0]["message"]["content"], response["usage"]["prompt_tokens"], response["usage"]["completion_tokens"]
        
        return self.__mistral_large_2407(prompt)
    
    