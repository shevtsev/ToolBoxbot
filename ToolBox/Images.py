import json, time, requests

class Text2ImageAPI:

    def __init__(self, url: str, api_key: str, secret_key: str):
        self.URL = url
        self.AUTH_HEADERS = {
            'X-Key': f'Key {api_key}',
            'X-Secret': f'Secret {secret_key}',
        }

    def get_model(self) -> str:
        response = requests.get(self.URL + 'key/api/v1/models', headers=self.AUTH_HEADERS)
        data = response.json()
        return data[0]['id']

    def generate(self, prompt: str, model: str, images: int = 1, width: int = 1024, height: int = 1024) -> str:
        params = {
            "type": "GENERATE",
            "numImages": images,
            "width": width,
            "height": height,
            "generateParams": {
                "query": f"{prompt}"
            }
        }

        data = {
            'model_id': (None, model),
            'params': (None, json.dumps(params), 'application/json')
        }
        status_response = requests.get(self.URL + 'key/api/v1/text2image/availability', headers=self.AUTH_HEADERS, files=data)
        status_request = status_response.json()
        if status_request['status'] == 'ACTIVE':
            response = requests.post(self.URL + 'key/api/v1/text2image/run', headers=self.AUTH_HEADERS, files=data)
            data = response.json()
            return data['uuid']
        print(status_request['status'])

    def check_generation(self, request_id, attempts: int = 10, delay: int = 10):
        while attempts > 0:
            response = requests.get(self.URL + 'key/api/v1/text2image/status/' + request_id, headers=self.AUTH_HEADERS)
            data = response.json()
            if data['status'] == 'DONE':
                return data['images']

            attempts -= 1
            time.sleep(delay)