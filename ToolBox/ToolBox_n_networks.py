import requests, json, os, io
from PIL import Image

# Neural networks class
class neural_networks:
    
#Protected
    # FLUX.1-schnell request
    def _FLUX_schnell(self, prompt: str, size: list[int, int], seed: int, num_inference_steps: int) -> str|None:
        payload = {
            "inputs": prompt,
            "parameters": {
                "guidance_scale": 1.5,
                "num_inference_steps": num_inference_steps,
                "width": size[0],
                "height": size[1],
                "seed": seed
            }
        }
        for i in range(1, 7):
            response = requests.post("https://api-inference.huggingface.co/models/black-forest-labs/FLUX.1-schnell",
                                    headers={"Authorization": "Bearer " + os.environ[f"HF_TOKEN{i}"], "Content-Type": "application/json"},
                                    json=payload)
            if response.status_code == 200:
                image = Image.open(io.BytesIO(response.content))
                return image
    
    def _mistral_large_2407(self, prompt: list[dict[str, str]], temperature: float, top_p: float) -> tuple[str, int, int]|str:
        data = {
            "messages": prompt,
            "temperature": temperature,
            "top_p": top_p,
            "max_tokens": 1024,
            "model": "pixtral-12b-2409"
        }
        response = requests.post("https://api.mistral.ai/v1/chat/completions",
                                headers={"Content-Type": "application/json", "Authorization": "Bearer "+ os.environ['MISTRAL_TOKEN']},
                                json=data)
        response = json.loads(response.text)
        if response.get("choices", False):
            return response["choices"][0]["message"]["content"], response["usage"]["prompt_tokens"], response["usage"]["completion_tokens"]
        else:
            return "Возникла ошибка", 0, 0

    def _free_gpt_4o_mini(self, prompt: str, temperature: float, top_p: float) -> tuple[str, int, int]|str:
        data = {
            "messages": prompt,
            "temperature": temperature,
            "top_p": top_p,
            "max_tokens": 1024,
            "model": "gpt-4o-mini"
        }
        for i in range(1, 7):
            response = requests.post("https://models.inference.ai.azure.com/chat/completions",
                                    headers={"Authorization": os.environ[f'GIT_TOKEN{i}'], "Content-Type" : "application/json"},
                                    json=data)
            if response.status_code == 200:
                response = json.loads(response.text)
                return response["choices"][0]["message"]["content"], response["usage"]["prompt_tokens"], response["usage"]["completion_tokens"]
        
        return self._mistral_large_2407(prompt=prompt, temperature=temperature, top_p=top_p) 