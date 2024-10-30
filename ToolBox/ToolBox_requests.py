import telebot, os, json
from telebot import types
from concurrent.futures import ThreadPoolExecutor, as_completed
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
        # Image request
        self.ImageArea      = lambda message, self=self: self.bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text="Введите ваш запрос для изображений 🖼", reply_markup=self.keyboard_blank(self, ["В меню"], ["exit"]), parse_mode='html')
        # Free mode request
        self.FreeArea       = lambda message, self=self: self.bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text="Введите ваш запрос", reply_markup=self.keyboard_blank(self, ["В меню"], ["exit"]), parse_mode='html')
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
    def __gpt_4o(self, prompt: str, message) -> int:
        send = self.__delay(message)
        try:
            response, incoming_tokens, outgoing_tokens = super()._gpt_4o_mini(prompt=prompt)
            self.bot.edit_message_text(chat_id=send.chat.id, message_id=send.message_id, text=PromptsCompressor.html_tags_insert(response), parse_mode='html')
            return incoming_tokens, outgoing_tokens
        except TypeError:
            self.bot.edit_message_text(chat_id=send.chat.id, message_id=send.message_id, text="При генерации возникла ошибка, попробуйте повторить позже")
            return 0, 0

    # Kandinsky processing
    def __kandinsky(self, prompt: str, message)-> None:
        send = self.__delay(message)
        photo = super()._FusionBrain(prompt=prompt)
        if photo:
            self.bot.send_photo(chat_id=message.chat.id, photo=photo)
            return self.bot.delete_message(chat_id=send.chat.id, message_id=send.message_id)
        return self.bot.edit_message_text(chat_id=send.chat.id, message_id=send.message_id, text="При генерации возникла ошибка, попробуйте повторить позже")

#Public
    # Text types
    def Text_types(self, message):
        name = ["Коммерческий  🛍️", "SMM 📱", "Брейншторм 💡", "Реклама 📺", "Заголовки 🔍", "SEO 🌐", "Email 📧", "В меню"]
        data = ["comm-text", "smm-text", "brainst-text", "advertising-text", "headlines-text", "seo-text", "email", "exit"]
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
        info = message.text.split(';')
        if len(info)==len(pc.commands_size[ind]):
            prompt = PromptsCompressor.get_prompt(ind=ind, info=info)
            incoming_tokens, outgoing_tokens = self.__gpt_4o(prompt=prompt, message=message)
            self.restart(message)
            return incoming_tokens, outgoing_tokens, 1
        return self.restart(message)
    
    # Some texts processing
    def SomeTextsCommand(self, message, ind: int):
        incoming_tokens = 0; outgoing_tokens = 0
        requests = message.text.split('\n')
        last_params = [{} for _ in pc.commands_size[ind]]

        def process_request(request, ind):
            params = request.split(';')

            if len(params) == 1 and "topic" in pc.commands_size[ind]:
                topic_index = pc.commands_size[ind].index("topic")
                for i, param in enumerate(pc.commands_size[ind]):
                    if i != topic_index:
                        params.append(last_params[ind].get(param, ''))

            elif len(params) == len(pc.commands_size[ind]):
                last_params[ind] = dict(zip(pc.commands_size[ind], params))

            else:
                for i, param in enumerate(pc.commands_size[ind]):
                    if i >= len(params) or not params[i]:
                        params.append(last_params[ind].get(param, ''))

            prompt = PromptsCompressor.get_prompt(ind=ind, info=params)
            in_tokens, out_tokens = self.__gpt_4o(prompt=prompt, message=message)
            return in_tokens, out_tokens

        with ThreadPoolExecutor() as executor:
            futures = [executor.submit(process_request, request, ind) for request in requests]
            
            for future in as_completed(futures):
                in_tokens, out_tokens = future.result()
                incoming_tokens += in_tokens
                outgoing_tokens += out_tokens
        self.restart(message)
        return incoming_tokens, outgoing_tokens, len(requests)

    # Images processing
    def ImageCommand(self, message):
        self.__kandinsky(prompt=message.text, message=message)
        return self.restart(message)

    # Free mode processing
    def FreeCommand(self, message):
        incoming_tokens, outgoing_tokens = self.__gpt_4o(prompt=message.text, message=message)
        self.restart(message)
        return incoming_tokens, outgoing_tokens, 1