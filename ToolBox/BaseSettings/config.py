import json, logging
from datetime import datetime
from dotenv import load_dotenv
from os import environ as env
from dateutil.relativedelta import relativedelta
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
        cls.__instance.start_params = lambda text=[0]*12, sessions_messages=[], some=False, images="0", free=False, basic=False, pro=False, incoming_tokens=0, outgoing_tokens=0, free_requests=10, datetime_sub=datetime.now().replace(microsecond=0)+relativedelta(days=1), promocode="", ref='': {'text':text, "sessions_messages": sessions_messages, "some":some, 'images':images, 'free': free, 'basic': basic, 'pro': pro, 'incoming_tokens': incoming_tokens, 'outgoing_tokens': outgoing_tokens, 'free_requests': free_requests, 'datetime_sub': datetime_sub, 'promocode': promocode, 'ref': ref}
        cls.__instance.token = env['TOKEN']
        cls.__instance.hf_tokens = [env[f"HF_TOKEN{i}"] for i in range(1, 7)]
        cls.__instance.git_tokens = [env[f'GIT_TOKEN{i}'] for i in range(1, 7)]
        cls.__instance.mistral_token = env['MISTRAL_TOKEN']
        cls.__instance.titles = {
          "id": "TEXT PRIMARY KEY", "text": "INTEGER[]",
          "sessions_messages": "TEXT[]", "some": "BOOLEAN",
          "images": "CHAR", "free" : "BOOLEAN", "basic" : "BOOLEAN",
          "pro" : "BOOLEAN", "incoming_tokens": "INTEGER", "outgoing_tokens" : "INTEGER",
          "free_requests" : "INTEGER", "datetime_sub": "DATETIME", "promocode": "TEXT", "ref": "TEXT"
        }
        cls.__instance.provider_token = env['PROVIDE_TOKEN']
        cls.__instance.currency = "RUB"
        cls.__instance.price_basic = 60*100
        cls.__instance.price_pro = 100*100
        provider_data_basic = {
          "receipt": {
            "items": [
              {
                "description": "Подписка на месяц использования бота ToolBox по тарифу Basic",
                "quantity": "1.00",
                "amount": {
                  "value": f"{cls.__instance.price_basic / 100:.2f}",
                  "currency": cls.__instance.currency
                },
                "payment_mode" : "full_payment",
                "vat_code": 1
              }
            ]
          }
        }
        provider_data_pro = {
          "receipt": {
            "items": [
              {
                "description": "Подписка на месяц использования бота ToolBox по тарифу Pro",
                "quantity": "1.00",
                "amount": {
                  "value": f"{cls.__instance.price_pro / 100:.2f}",
                  "currency": cls.__instance.currency
                },
                "payment_mode" : "full_payment",
                "vat_code": 1
              }
            ]
          }
        }
        cls.__instance.provider_data_basic = json.dumps(provider_data_basic)
        cls.__instance.provider_data_pro = json.dumps(provider_data_pro)

        with open("BaseSettings/prompts.json", 'r') as file:
            prompts_text = json.load(file)
        cls.__instance.prompts_text = prompts_text
        cls.__instance.delay = "Подождите, это должно занять несколько секунд . . ."
        cls.__instance.start_name = ["Текст 📝", "Изображения 🎨", "Свободный режим 🗽", "Тарифы 💸"]
        cls.__instance.start_data = ["text", "images", "free", "tariff"]
        cls.__instance.choose_task = "Выберите нужную вам задачу"
        cls.__instance.imagesize = "В этом меню вы можете выбрать разрешение изображения и настроить автоматическое улучшение вводимого промпта (по умолчанию выключено)."
        cls.__instance.next_step = "Выберите следующее действие"
        cls.__instance.limit_end = "Лимит бесплатных запросов, увы, исчерпан😢 Но вы можете выбрать один из наших платных тарифов. Просто нажмите на них и получите подробное описание"
        cls.__instance.text_types_name = ["Коммерческий  🛍️", "Контент-план 📋", "Суммаризировать текст 📚", "Статья для блога 💻", "Лонгрид 📑", "SMM 📱",
                "Брейншторм 💡", "Рекламные креативы 📺", "Заголовки 🔍", "SEO 🌐", "Новость 📰", "Редактура 📝", "В меню"]
        cls.__instance.text_types_data = ["comm-text", "content-plan", "summarization", "blog", "longrid", "smm-text", "brainst-text", "advertising-text",
                "headlines-text", "seo-text", "news", "editing", "exit"]
        cls.__instance.tarrif_name = ["BASIC", "PRO", "Промокод", "В меню", "Реферальная программа"]
        cls.__instance.tarrif_data = ["basic", "pro", "promo", "exit", "ref"]
        cls.__instance.improve_off_name = ["9:16", "1:1", "16:9", "Улучшать промпты", "В меню"]
        cls.__instance.improve_off_data = ["576x1024", "1024x1024", "1024x576", "improve_prompts_off", "exit"]
        cls.__instance.improve_on_name = ["9:16", "1:1", "16:9", "Улучшать промпты✅", "В меню"]
        cls.__instance.improve_on_data = ["576x1024", "1024x1024", "1024x576", "improve_prompts_on", "exit"]
        cls.__instance.admin_ids = ['2004851715', '206635551']
        cls.__instance.promocodes = json.load(open("promocodes/promocodes.json"))
        return cls.__instance
      
config = Config()