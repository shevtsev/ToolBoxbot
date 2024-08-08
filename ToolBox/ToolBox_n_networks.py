import requests, time, json, base64, os
from Images import Text2ImageAPI

#Класс с нейросетями
class neural_networks:
#Protected
    #Cloud api request
    def _gpt_4o_mini(self, prompt: str) -> str|None:
        payload = {
            "model": "gpt-4o-mini",
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
        }
        response = requests.post("https://api.proxyapi.ru/openai/v1/chat/completions",
                                headers={'Authorization': os.environ['PROXY_API']},
                                json=payload)
        response = json.loads(response.text)
        if response.get('choices', None):
            time.sleep(5)
            return response['choices'][0]['message']['content']
        else:
            print(response)
    
    #Кандинский
    def _FusionBrain(self, prompt: str) -> str|None:
        api = Text2ImageAPI('https://api-key.fusionbrain.ai/', os.environ["API_KEY"], os.environ["SECRET_KEY"])
        model_id = api.get_model()
        uuid = api.generate(prompt, model_id)
        if uuid:
            images = api.check_generation(uuid)
            return base64.b64decode((images[0]))