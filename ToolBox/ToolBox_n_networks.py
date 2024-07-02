import subprocess, time, json, base64, os
from Images import Text2ImageAPI
#Класс с нейросетями
class neural_networks:
    #Cloud curl request
    def cloud_sonnet(self, prompt: str) -> str:
        payload = {
            "model": "claude-3-sonnet-20240229",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 1024
        }

        cmd = ["curl", "-X", "POST",
               "https://api.proxyapi.ru/anthropic/v1/messages",
               "-H", "Content-Type: application/json",
               "-H", f"Authorization: Bearer {os.environ['CLOUDE_ID']}",
               "-H", "Anthropic-Version: 2023-06-01",
               "-d", json.dumps(payload)]

        process = subprocess.run(cmd, capture_output=True, text=True)
        time.sleep(5)
        response = json.loads(process.stdout)
        return response.get('content')[0]['text']
    
    #Кандинский
    def FusionBrain(self, prompt: str) -> str:
        api = Text2ImageAPI('https://api-key.fusionbrain.ai/', os.environ["API_KEY"], os.environ["SECRET_KEY"])
        model_id = api.get_model()
        uuid = api.generate(prompt, model_id)
        if uuid:
            images = api.check_generation(uuid)
            return base64.b64decode((images[0]))