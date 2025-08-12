import json, logging
from dotenv import load_dotenv
from os import environ as env
from dataclasses import dataclass

@dataclass
class Config:
    __instance = None

    def __new__(cls):
      if cls.__instance is None:
        load_dotenv()
        logging.basicConfig(filename='out.log', level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        cls.__instance = super(Config, cls).__new__(cls)
        cls.__instance.token1 = env['TOKEN1']
        cls.__instance.token2 = env['TOKEN2']
        cls.__instance.promocodes = json.load(open("promocodes/promocodes.json"))
        cls.__instance.admin_ids = ['2004851715', '206635551']
        return cls.__instance
      
config = Config()