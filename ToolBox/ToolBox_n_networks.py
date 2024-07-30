import requests, time, json, base64, os
from Images import Text2ImageAPI

#Класс с нейросетями
class neural_networks:
    #Cloud api request
    def cloud_sonnet(self, prompt: str) -> str:
        payload = {
            "model": "claude-3-5-sonnet-20240620",
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": 1024
        }
        response = requests.post("https://api.proxyapi.ru/anthropic/v1/messages",
                                headers={'Authorization': os.environ['CLOUDE_ID'], 'Anthropic-Version': '2023-06-01'},
                                json=payload)
        response = json.loads(response.text)
        if response.get('content', None):
            time.sleep(5)
            return response['content'][0]['text']
        else:
            print(response)
    
    #Кандинский
    def FusionBrain(self, prompt: str) -> str:
        api = Text2ImageAPI('https://api-key.fusionbrain.ai/', os.environ["API_KEY"], os.environ["SECRET_KEY"])
        model_id = api.get_model()
        uuid = api.generate(prompt, model_id)
        if uuid:
            images = api.check_generation(uuid)
            return base64.b64decode((images[0]))