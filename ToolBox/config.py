import json, logging
from dotenv import load_dotenv
from os import environ as env
from dataclasses import dataclass

logging.basicConfig(filename='out.log', level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class Config:
    __instance = None

    def __new__(cls):
      if cls.__instance is None:
        load_dotenv()
        cls.__instance = super(Config, cls).__new__(cls)
        cls.__instance.token = env['TOKEN']
        cls.__instance.hf_tokens = [env[f"HF_TOKEN{i}"] for i in range(1, 7)]
        cls.__instance.git_tokens = [env[f'GIT_TOKEN{i}'] for i in range(1, 7)]
        cls.__instance.mistral_token = env['MISTRAL_TOKEN']
        cls.__instance.provider_token = env['PROVIDE_TOKEN']
        cls.__instance.currency = "RUB"
        cls.__instance.price_basic = 60*100
        cls.__instance.price_pro = 100*100
        provider_data_basic = {
          "receipt": {
            "items": [
              {
                "description": "Безлимитная генерация текста, в том числе по готовым промптам.",
                "quantity": "1.00",
                "amount": {
                  "value": f"{cls.__instance.price_basic / 100:.2f}",
                  "currency": cls.__instance.currency
                },
                "vat_code": 1
              }
            ]
          }
        }
        provider_data_pro = {
          "receipt": {
            "items": [
              {
                "description": "Безлимитная генерация текста (в том числе по готовым промптам) и изображений.",
                "quantity": "1.00",
                "amount": {
                  "value": f"{cls.__instance.price_pro / 100:.2f}",
                  "currency": cls.__instance.currency
                },
                "vat_code": 1
              }
            ]
          }
        }
        cls.__instance.provider_data_basic = json.dumps(provider_data_basic)
        cls.__instance.provider_data_pro = json.dumps(provider_data_pro)

        with open("ToolBox/BaseSettings/prompts.json", 'r') as file:
            prompts_text = json.load(file)
        cls.__instance.prompts_text = prompts_text

        return cls.__instance
config = Config()