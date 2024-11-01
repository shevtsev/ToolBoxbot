import requests, time, json, base64, os, io
from Images import Text2ImageAPI
from PIL import Image

# Neural networks class
class neural_networks:
    
#Private 
    def __reserve_dalle2(self, prompt: str)->bytes:
        data = {
            "model": "dall-e-2",
            "prompt": prompt,
            "n": 1,
            "size": "1024x1024"
        }
        response = requests.post("https://api.proxyapi.ru/openai/v1/images/generations",
                                headers={'Authorization': os.environ['PROXY_API']},
                                json=data)
        response = json.loads(response.text)["data"][0]["url"]
        image_bytes = requests.get(response).content
        return image_bytes
    
#Protected
    # Text model request
    def _gpt_4o_mini(self, prompt: str) -> tuple[str, int]|None:
        payload = {
            "model": "gpt-4o-mini",
            "messages": [
                {
                    "role": "user",
                    "content": prompt,
                    "max_tokens": 2048
                }
            ],
        }
        response = requests.post("https://api.proxyapi.ru/openai/v1/chat/completions",
                                headers={'Authorization': os.environ['PROXY_API']},
                                json=payload)
        response = json.loads(response.text)
        if response.get('choices', None):
            time.sleep(5)
            return response['choices'][0]['message']['content'], response['usage']['prompt_tokens'], response['usage']['completion_tokens']
        else:
            print(response.get("detail", None))

    # Hermes 3 - Llama-3.1 8B request
    def _HermesLlama(self, prompt: str):
        data = {
                "model": "NousResearch/Hermes-3-Llama-3.1-8B",
                "messages": [
                        { "role": "user", "content": prompt }
                    ],
                "max_tokens": 1024,
                "stream": False
            }
        response = requests.post("https://api-inference.huggingface.co/models/NousResearch/Hermes-3-Llama-3.1-8B/v1/chat/completions",
                                headers={"Authorization": "Bearer " + os.environ["HF_TOKEN"], "Content-Type": "application/json"},
                                json=data)
        
        response = json.loads(response.text)
        print(response)
        return response["choices"][0]["message"]["content"], response["usage"]["prompt_tokens"], response["usage"]["completion_tokens"]
    
    # Kandinsky request
    def _FusionBrain(self, prompt: str) -> str|None:
        api = Text2ImageAPI('https://api-key.fusionbrain.ai/', os.environ["API_KEY"], os.environ["SECRET_KEY"])
        model_id = api.get_model()
        uuid = api.generate(prompt, model_id)
        if uuid:
            images = api.check_generation(uuid)
            return base64.b64decode((images[0]))
        return self.__reserve_dalle2(prompt)

    # FLUX.1-schnell request
    def _FLUX_schnell(self, prompt: str) -> str|None:
        data = {"Authorization": "Bearer " + os.environ['HF_TOKEN'], "Content-Type": "application/json"}
        payload = {
            "inputs": prompt,
        }
        response = requests.post("https://api-inference.huggingface.co/models/black-forest-labs/FLUX.1-schnell", headers=data, json=payload).content
        image = Image.open(io.BytesIO(response))
        return image