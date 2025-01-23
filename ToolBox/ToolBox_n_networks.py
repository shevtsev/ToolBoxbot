import requests, json, io
from BaseSettings.config import config, logger
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
                                    headers={"Authorization": "Bearer " + config.hf_tokens[i], "Content-Type": "application/json"},
                                    json=payload)
            if response.status_code == 200:
                image = Image.open(io.BytesIO(response.content))
                logger.info(f"FLUX schnell API request was successful, status code: {response.status_code}")
                return image
            else:
                logger.error(f"FLUX schnell API request error, status code: {response.status_code}, response text: {response.content}")
        return None
    
    def _mistral_large_2407(self, prompt: list[dict[str, str]], temperature: float, top_p: float) -> tuple[str, int, int]|str:
        data = {
            "messages": prompt,
            "temperature": temperature,
            "top_p": top_p,
            "max_tokens": 1024,
            "model": "pixtral-12b-2409"
        }
        response = requests.post("https://api.mistral.ai/v1/chat/completions",
                                headers={"Content-Type": "application/json", "Authorization": "Bearer "+ config.mistral_token},
                                json=data)
        if response.status_code == 200:
            logger.info(f"Mistral large API request was successful, status code: {response.status_code}")
            response = json.loads(response.text)
            return response["choices"][0]["message"]["content"], response["usage"]["prompt_tokens"], response["usage"]["completion_tokens"]
        else:
            logger.error(f"Mistral large API request error, status code: {response.status_code}, response text: {response.content}")
            return "Возникла ошибка, попробуйте позже", 0, 0

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
                                    headers={"Authorization": config.git_tokens[i], "Content-Type" : "application/json"},
                                    json=data)
            if response.status_code == 200:
                logger.info(f"GPT 4o mini API request was successful, status code: {response.status_code}")
                response = json.loads(response.text)
                return response["choices"][0]["message"]["content"], response["usage"]["prompt_tokens"], response["usage"]["completion_tokens"]
            else:
                logger.error(f"GPT 4o mini API request error, status code: {response.status_code}, response text: {response.content}")
        return self._mistral_large_2407(prompt=prompt, temperature=temperature, top_p=top_p) 