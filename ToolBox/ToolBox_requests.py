import telebot, os, json, time
from telebot import types
from BaseSettings.AuxiliaryClasses import PromptsCompressor, keyboards
from ToolBox_n_networks import neural_networks

# Class initialization
pc = PromptsCompressor()

#Main functions class
class ToolBox(keyboards, neural_networks):
    def __init__(self):
        # Start buttons
        self.name = ["Текст 📝", "Изображения 🎨", "Свободный режим 🗽", "Тарифы 💸"]
        self.data = ["text", "images", "free", "tariff"]

        # Promts texts load
        with open("ToolBox/BaseSettings/prompts.json", 'r') as file:
            self.prompts_text = json.load(file)

        # Telegram bot initialization
        self.bot = telebot.TeleBot(token=os.environ['TOKEN'])
        # Inline keyboard blank lambda
        self.keyboard_blank = lambda self, name, data: super()._keyboard_two_blank(data, name)
        # Markup keyboard
        self.reply_keyboard = lambda self, name: super()._reply_keyboard(name)
        # Request delay
        self.__delay        = lambda message, self=self: self.bot.send_message(message.chat.id, "Подождите, это должно занять несколько секунд . . .", parse_mode='html')  
        # Start request
        self.start_request  = lambda message, self=self: self.bot.send_message(message.chat.id, self.prompts_text['hello'], reply_markup=self.keyboard_blank(self, self.name, self.data), parse_mode='html')
        # Restart request
        self.restart        = lambda message, self=self: self.bot.send_message(message.chat.id, "Выберите нужную вам задачу", reply_markup=self.keyboard_blank(self, self.name, self.data), parse_mode='html')
        # One text request
        self.OneTextArea    = lambda message, ind, self=self: self.bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text=self.prompts_text['text_list'][ind], reply_markup=self.keyboard_blank(self, ["Назад"], ["text_exit"]))
        # Some texts request
        self.SomeTextsArea  = lambda message, ind, self=self: self.bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text=self.prompts_text['few_texts_list'][ind], reply_markup=self.keyboard_blank(self, ["Назад"], ["text_exit"]))
        # Image size
        self.ImageSize      = lambda message, self=self: self.bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text="Выберите разрешение изображения", reply_markup=self.keyboard_blank(self, ["256x256", "512x512", "1024x1024", "В меню"], ["256x256", "512x512", "1024x1024", "exit"]), parse_mode='html')
        # Image request
        self.ImageArea      = lambda message, self=self: self.bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text="Введите ваш запрос для изображений 🖼", reply_markup=self.keyboard_blank(self, ["В меню"], ["exit"]), parse_mode='html')
        # Free mode request
        self.FreeArea       = lambda message, self=self: self.bot.send_message(chat_id=message.chat.id, text="Введите ваш запрос", reply_markup=self.reply_keyboard(self, ["В меню"]), parse_mode='html')
        # Tariff request
        self.TariffArea     = lambda message, self=self: self.bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text="Тарифы", reply_markup=self.keyboard_blank(self, ["BASIC", "PRO", "В меню"], ["basic", "pro", "exit"]))
        # Tariffs area exit
        self.TariffExit     = lambda message, self=self: self.bot.send_message(chat_id=message.chat.id, text="Тарифы", reply_markup=self.keyboard_blank(self, ["BASIC", "PRO", "В меню"], ["basic", "pro", "exit"]))
        # End tariff
        self.TarrifEnd      = lambda message, self=self: self.bot.send_message(chat_id=message.chat.id, text="У вас закончились запросы, но вы можете продлить ваш тариф.", reply_markup=self.keyboard_blank(self, ["BASIC", "PRO", "В меню"], ["basic", "pro", "exit"]))
        # Free tariff end
        self.FreeTariffEnd  = lambda message, self=self: self.bot.send_message(chat_id=message.chat.id, text="Лимит бесплатных запросов, увы, исчерпан😢 Но вы можете выбрать один из наших платных тарифов. Просто нажмите на них и получите подробное описание", reply_markup=self.keyboard_blank(self, ["BASIC", "PRO", "В меню"], ["basic", "pro", "exit"]))
        # Select one or some texts
        self.SomeTexts      = lambda message, ind, self=self: self.bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text="Хотите сделать один текст или сразу несколько?", reply_markup=self.keyboard_blank(self, ["Один", "Несколько", "Назад"], [f"one_{ind}", f"some_{ind}", "text_exit"]))
        
#Private        
    # GPT 4o mini processing
    def __gpt_4o_mini(self, prompt: list[dict], message) -> tuple[str, int, int]:
        send = self.__delay(message)
        response, incoming_tokens, outgoing_tokens = super()._free_gpt_4o_mini(prompt=prompt)
        self.bot.edit_message_text(chat_id=send.chat.id, message_id=send.message_id, text=PromptsCompressor.html_tags_insert(response), parse_mode='html')
        return response, incoming_tokens, outgoing_tokens
        
    # FLUX schnell processing
    def __FLUX_schnell(self, prompt: str, size: str, message)-> None:
        send = self.__delay(message)
        while True:
            try:
                photo = super()._FLUX_schnell(prompt, size)
            except:
                continue
            else:
                break
        if photo:
            self.bot.send_photo(chat_id=message.chat.id, photo=photo)
            return self.bot.delete_message(chat_id=send.chat.id, message_id=send.message_id)
        return self.bot.edit_message_text(chat_id=send.chat.id, message_id=send.message_id, text="При генерации возникла ошибка, попробуйте повторить позже")

#Public
    # Text types
    def Text_types(self, message):
        name = ["Коммерческий  🛍️", "SMM 📱", "Брейншторм 💡", "Реклама 📺", "Заголовки 🔍", "SEO 🌐", "Новость 📰", "Редактура 📝", "В меню"]
        data = ["comm-text", "smm-text", "brainst-text", "advertising-text", "headlines-text", "seo-text", "news", "editing", "exit"]
        return self.bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text="📝 Выберите тип текста", reply_markup=self.keyboard_blank(self, name, data))
    
    # Tariffs
    # Basic tariff
    def Basic_tariff(self, message):
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton("Подключить тариф BASIC", pay=True))
        keyboard.add(types.InlineKeyboardButton("К тарифам", callback_data="tariff_exit"))
        price = [types.LabeledPrice(label='BASIC', amount=99*100)]
        self.bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
        self.bot.send_invoice(chat_id=message.chat.id, title = 'BASIC',
            description = "Доступ к генерации текстового контента. Каждый день вы можете генерировать более 35 страниц\nНесколько категорий запросов в зависимости от рабочих задач\nПоддержка пакетной обработки сразу нескольких задач по одному и тому же запросу.",
            invoice_payload = 'basic_invoice_payload',
            start_parameter='subscription',
            provider_token = os.environ['PROVIDE_TOKEN'],
            currency='RUB', prices=price, reply_markup=keyboard)
    
    # Pro tariff
    def Pro_tariff(self, message):
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton("Подключить тариф PRO", pay=True))
        keyboard.add(types.InlineKeyboardButton("К тарифам", callback_data="tariff_exit"))
        price = [types.LabeledPrice(label='PRO', amount=199*100)]
        self.bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
        self.bot.send_invoice(chat_id=message.chat.id, title = 'PRO',
            description = "Генерация текста и изображений. Каждый день вы можете генерировать более 35 страниц текста и безлимитное количество изображений.",
            invoice_payload = 'pro_invoice_payload',
            start_parameter='subscription',
            provider_token = os.environ['PROVIDE_TOKEN'],
            currency='RUB', prices=price, reply_markup=keyboard)
        
    # One text processing
    def TextCommands(self, message, ind: int):
        info = []
        incoming_tokens = 0; outgoing_tokens = 0; response = None
        if 'TEXT' in pc.commands_size[ind]:
            info.append(message.text)
            msg = self.bot.send_message(chat_id=message.chat.id, text="Введите параметры через ;\nНе забывайте ставить ; между параметрами, иначе бот не сможет понять запрос 🤷‍♂️")
            def Text_next_step(message):
                nonlocal info, incoming_tokens, outgoing_tokens, response
                info += message.text.split(';')
                if len(info)==len(pc.commands_size[ind]):
                    prompt = pc.get_prompt(ind=ind, info=info)
                    response, incoming_tokens, outgoing_tokens = self.__gpt_4o_mini(prompt=[{ "role": "user", "content": prompt }], message=message)
                return self.restart(message)
            self.bot.register_next_step_handler(msg, Text_next_step)
            while response is None:
                time.sleep(1)
            return incoming_tokens, outgoing_tokens, 1
        else:
            info = message.text.split(';')
            if len(info)==len(pc.commands_size[ind]):
                prompt = pc.get_prompt(ind=ind, info=info)
                response, incoming_tokens, outgoing_tokens = self.__gpt_4o_mini(prompt=[{ "role": "user", "content": prompt }], message=message)
                self.restart(message)
                return incoming_tokens, outgoing_tokens, 1
            return self.restart(message)
    
    # Some texts processing
    def SomeTextsCommand(self, message, ind: int, tokens: dict[str, int]):
        incoming_tokens = 0; outgoing_tokens = 0
        requests = message.text.split('\n')
        last_params = [{} for _ in requests]

        def process_request(request, ind, num):
            params = request.split(';')

            if len(params) == 1:
                topic_index = pc.commands_size[ind].index("TOPIC") if "TOPIC" in pc.commands_size[ind] else pc.commands_size[ind].index("TEXT")
                for i, param in enumerate(pc.commands_size[ind]):
                    if i != topic_index:
                        params.append(last_params[num].get(param, ''))

            elif len(params) == len(pc.commands_size[ind]) or len(params) == len(pc.commands_size[ind])-1 and "TEXT" in pc.commands_size[ind]:
                last_params[num] = dict(zip(pc.commands_size[ind], params)) if len(params) == len(pc.commands_size[ind]) else dict(zip(pc.commands_size[ind][1:], params))

            else:
                for i, param in enumerate(pc.commands_size[ind]):
                    if i >= len(params):
                        params.append(last_params[num].get(param, ''))

            if "TEXT" in pc.commands_size[ind]:
                msg = self.bot.send_message(chat_id=message.chat.id, text="Введите ваш текст")
                def Some_Text_next_step(message):
                    nonlocal params, last_params
                    params = [message.text] + params
                    last_params[num] = dict(zip(pc.commands_size[ind], params))
                    return params
                self.bot.register_next_step_handler(msg, Some_Text_next_step)
                while len(params) < len(pc.commands_size[ind]):
                    time.sleep(1)

            prompt = pc.get_prompt(ind=ind, info=params)
            response, in_tokens, out_tokens = self.__gpt_4o_mini(prompt=[{ "role": "user", "content": prompt }], message=message)
            return in_tokens, out_tokens

        for cnt, request in enumerate(requests, 1):
            if tokens["incoming_tokens"]-incoming_tokens >= 0 and tokens["outgoing_tokens"]-outgoing_tokens >= 0 or tokens["free_requests"]-cnt >= 0:
                in_tokens, out_tokens = process_request(request, ind, cnt-1)
                incoming_tokens += in_tokens
                outgoing_tokens += out_tokens
        self.restart(message)
        return incoming_tokens, outgoing_tokens, len(requests)

    # Images processing
    def ImageCommand(self, message, size):
        self.__FLUX_schnell(prompt=message.text, size=size, message=message)
        return self.restart(message)

    # Free mode processing
    def FreeCommand(self, message, prompts: list[str]):
        prompts.append({ "role": "user", "content": message.text })
        response, incoming_tokens, outgoing_tokens = self.__gpt_4o_mini(prompt=prompts, message=message)
        prompts.append({ "role": "assistant", "content": response})
        return incoming_tokens, outgoing_tokens, prompts