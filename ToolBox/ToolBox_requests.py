import telebot, os, json, concurrent.futures, time
from random import randint
from telebot import types
from md2tgmd import escape
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
        # Restart murkup
        self.restart_markup = lambda message, self=self: self.bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text="Выберите нужную вам задачу", reply_markup=self.keyboard_blank(self, self.name, self.data), parse_mode='html')
        # One text request
        self.OneTextArea    = lambda message, ind, self=self: self.bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text=self.prompts_text['text_list'][ind][0], reply_markup=self.keyboard_blank(self, ["Назад"], ["text_exit"]))
        # Some texts request
        self.SomeTextsArea  = lambda message, ind, self=self: self.bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text=self.prompts_text['few_texts_list'][ind][0], reply_markup=self.keyboard_blank(self, ["Назад"], ["text_exit"]))
        # Image size on
        self.ImageSize_off  = lambda message, self=self: self.bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text="В этом меню вы можете выбрать разрешение изображения и настроить автоматическое улучшение вводимого промпта (по умолчанию выключено).", reply_markup=self.keyboard_blank(self, ["9:16", "1:1", "16:9", "Улучшать промпты", "В меню"], ["576x1024", "1024x1024", "1024x576", "improve_prompts_off", "exit"]), parse_mode='html')
        # Image size off
        self.ImageSize_on   = lambda message, self=self: self.bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text="В этом меню вы можете выбрать разрешение изображения и настроить автоматическое улучшение вводимого промпта (по умолчанию выключено).", reply_markup=self.keyboard_blank(self, ["9:16", "1:1", "16:9", "Улучшать промпты✅", "В меню"], ["576x1024", "1024x1024", "1024x576", "improve_prompts_on", "exit"]), parse_mode='html')
        # Image request
        self.ImageArea      = lambda message, self=self: self.bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text="Введите ваш запрос для изображений 🖼", reply_markup=self.keyboard_blank(self, ["В меню"], ["exit"]), parse_mode='html')
        # Image change
        self.ImageChange    = lambda message, self=self: self.bot.send_message(chat_id=message.chat.id, text="Выберите следующее действие", reply_markup=self.keyboard_blank(self, ["Улучшить 🪄", "🔁", "Новая 🖼", "В меню"], ["upscale", "regenerate", "images", "exit"]), parse_mode='html')
        # Message before upscale
        self.BeforeUpscale  = lambda message, self=self: self.bot.send_message(chat_id=message.chat.id, text="Выберите следующее действие", reply_markup=self.keyboard_blank(self, ["🔁", "Новая 🖼", "В меню"], ["regenerate", "images", "exit"]), parse_mode='html')
        # Free mode request
        self.FreeArea       = lambda message, self=self: self.bot.send_message(chat_id=message.chat.id, text="Введите ваш запрос", reply_markup=self.reply_keyboard(self, ["В меню"]), parse_mode='html')
        # Tariff request
        self.TariffArea     = lambda message, self=self: self.bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text="Тарифы", reply_markup=self.keyboard_blank(self, ["BASIC", "PRO", "Промокод", "В меню", "Реферальная программа"], ["basic", "pro", "promo", "exit", "ref"]))
        # Tariffs area exit
        self.TariffExit     = lambda message, self=self: self.bot.send_message(chat_id=message.chat.id, text="Тарифы", reply_markup=self.keyboard_blank(self, ["BASIC", "PRO", "Промокод", "В меню", "Реферальная программа"], ["basic", "pro", "promo", "exit", "ref"]))
        # End tariff
        self.TarrifEnd      = lambda message, self=self: self.bot.send_message(chat_id=message.chat.id, text="У вас закончились запросы, но вы можете продлить ваш тариф.", reply_markup=self.keyboard_blank(self, ["BASIC", "PRO", "Промокод", "В меню", "Реферальная программа"], ["basic", "pro", "promo", "ref", "exit"]))
        # Free tariff end
        self.FreeTariffEnd  = lambda message, self=self: self.bot.send_message(chat_id=message.chat.id, text="Лимит бесплатных запросов, увы, исчерпан😢 Но вы можете выбрать один из наших платных тарифов. Просто нажмите на них и получите подробное описание", reply_markup=self.keyboard_blank(self, ["BASIC", "PRO", "Промокод", "В меню", "Реферальная программа"], ["basic", "pro", "promo", "exit", "ref"]))
        # Select one or some texts
        self.SomeTexts      = lambda message, ind, self=self: self.bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text="Хотите сделать один текст или сразу несколько?", reply_markup=self.keyboard_blank(self, ["Один", "Несколько", "Назад"], [f"one_{ind}", f"some_{ind}", "text_exit"]))
        
#Private        
    # GPT 4o mini processing
    def __gpt_4o_mini(self, prompt: list[dict], message, temperature: float = 0.5, top_p: float = 0.85) -> tuple[dict[str, str], int, int]:
        send = self.__delay(message)
        response, incoming_tokens, outgoing_tokens = super()._free_gpt_4o_mini(prompt=prompt, temperature=temperature, top_p=top_p)
        response = escape(response)
        for i in range(0, len(response), 4096):
            chunk = response[i:i+4096]
            if i == 0:
                self.bot.edit_message_text(chat_id=send.chat.id, message_id=send.message_id, text=chunk, parse_mode='MarkdownV2')
            else:
                self.bot.send_message(chat_id=send.chat.id, text=chunk, parse_mode='MarkdownV2')
        return response, incoming_tokens, outgoing_tokens
        
    # Mistral large processing
    def mistral_large(self, prompt: str, temperature: float = 0.6, top_p: float = 0.85) -> tuple[str, int, int]:
        response, incoming_tokens, outgoing_tokens = super()._mistral_large_2407(prompt=[{"role": "user", "content": prompt}], temperature=temperature, top_p=top_p)
        return response
    
    # FLUX schnell processing
    def __FLUX_schnell(self, prompt: str, size: list[int], message, seed: int, num_inference_steps: int)-> None:
        send = self.__delay(message)
        while True:
            try:
                photo = super()._FLUX_schnell(prompt, size, seed, num_inference_steps)
            except:
                continue
            else:
                break
        if photo:
            self.bot.send_photo(chat_id=message.chat.id, photo=photo)
            return self.bot.delete_message(chat_id=send.chat.id, message_id=send.message_id)
        self.bot.edit_message_text(chat_id=send.chat.id, message_id=send.message_id, text="При генерации возникла ошибка, попробуйте повторить позже")

#Public
    # Text types
    def Text_types(self, message):
        name = ["Коммерческий  🛍️", "Контент-план 📋", "Суммаризировать текст 📚", "Статья для блога 💻", "Лонгрид 📑", "SMM 📱",
                "Брейншторм 💡", "Рекламные креативы 📺", "Заголовки 🔍", "SEO 🌐", "Новость 📰", "Редактура 📝", "В меню"]
        data = ["comm-text", "content-plan", "summarization", "blog", "longrid", "smm-text", "brainst-text", "advertising-text",
                "headlines-text", "seo-text", "news", "editing", "exit"]
        return self.bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text="📝 Выберите тип текста", reply_markup=self.keyboard_blank(self, name, data))
    
    # Tariffs
    # Basic tariff
    def Basic_tariff(self, message):
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton("Подключить тариф BASIC", pay=True))
        keyboard.add(types.InlineKeyboardButton("К тарифам", callback_data="tariff_exit"))
        price = [types.LabeledPrice(label='BASIC', amount=60*100)]
        self.bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
        self.bot.send_invoice(chat_id=message.chat.id, title = 'BASIC',
            description = "Безлимитная генерация текста, в том числе по готовым промптам.",
            invoice_payload = 'basic_invoice_payload',
            start_parameter='subscription',
            provider_token = os.environ['PROVIDE_TOKEN'],
            currency='RUB', prices=price, reply_markup=keyboard)
    
    # Pro tariff
    def Pro_tariff(self, message):
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton("Подключить тариф PRO", pay=True))
        keyboard.add(types.InlineKeyboardButton("К тарифам", callback_data="tariff_exit"))
        price = [types.LabeledPrice(label='PRO', amount=100*100)]
        self.bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
        self.bot.send_invoice(chat_id=message.chat.id, title = 'PRO',
            description = "Безлимитная генерация текста (в том числе по готовым промптам) и изображений.",
            invoice_payload = 'pro_invoice_payload',
            start_parameter='subscription',
            provider_token = os.environ['PROVIDE_TOKEN'],
            currency='RUB', prices=price, reply_markup=keyboard)
        
    # One text processing
    def TextCommands(self, message, ind: int):
        info = []
        incoming_tokens = 0; outgoing_tokens = 0
        info.append(message.text)
        for i in range(1, len(self.prompts_text['text_list'][ind])):
            msg = self.bot.send_message(chat_id=message.chat.id, text=self.prompts_text['text_list'][ind][i])
            param = None

            def Param_next_step(message):
                nonlocal info, param
                param = message.text
                info.append(param)

            self.bot.register_next_step_handler(msg, Param_next_step)
            while param is None:
                time.sleep(0.5)
        prompt = pc.get_prompt(ind=ind, info=info)
        response, incoming_tokens, outgoing_tokens = self.__gpt_4o_mini(prompt=[{ "role": "user", "content": prompt }], message=message)
        self.restart(message)
        return incoming_tokens, outgoing_tokens, 1
    
    # Some texts processing
    def SomeTextsCommand(self, message, ind: int, tokens: dict[str, int]):
        n = int(message.text)
        text_buttons = [
            "comm-text", "content-plan", "summarization",
            "blog", "longrid", "smm-text", "brainst-text",
            "advertising-text", "headlines-text", "seo-text",
            "news", "editing"
        ]
        ans = []
        avalible = [text_buttons.index(el) for el in [
                                                    "comm-text", "blog", "longrid", "smm-text",
                                                    "advertising-text", "seo-text", "news"
                                                    ]]

        for i in range(n):
            ans.append([])
            if "TEXT" in pc.commands_size[ind]:
                msg = self.bot.send_message(chat_id=message.chat.id, text=f"Введите текст источника {i+1}")
                text = None
                def Text_next_step(message):
                    nonlocal text, ans
                    text = message.text
                    ans[i].append(text)
                self.bot.register_next_step_handler(msg, Text_next_step)
                while text is None:
                    time.sleep(0.5)
        
        index = avalible.index(ind)
        for el in range(1, len(self.prompts_text["few_texts_list"][index])):
            msg = self.bot.send_message(chat_id=message.chat.id, text=self.prompts_text["few_texts_list"][index][el])
            params = None
            def Params_addition(message):
                nonlocal params, ans
                params = message.text
                params = params.split(';')
                if len(params) < len(pc.commands_size[ind]):
                    while len(params) < len(pc.commands_size[ind]):
                        params.append(None)
                param = params[0]
                [ans[i].append(param) if params[i] is None else ans[i].append(params[i]) for i in range(len(ans))]
            self.bot.register_next_step_handler(msg, Params_addition)
            while params is None:
                time.sleep(0.5)

        incoming_tokens = 0; outgoing_tokens = 0
        def process_prompt(i):
            nonlocal incoming_tokens, outgoing_tokens
            prompt = pc.get_prompt(ind=ind, info=ans[i])
            if tokens['incoming_tokens'] - incoming_tokens > 0 and tokens['outgoing_tokens'] - outgoing_tokens > 0 or tokens['free_requests'] - i > 0:
                response, in_tokens, out_tokens = self.__gpt_4o_mini(prompt=[{"role": "user", "content": prompt}], message=message)
                return in_tokens, out_tokens
            return 0, 0
        
        with concurrent.futures.ThreadPoolExecutor() as executor:
            results = list(executor.map(process_prompt, range(n)))
        
        for in_tokens, out_tokens in results:
            incoming_tokens += in_tokens
            outgoing_tokens += out_tokens
        
        self.restart(message)
        return incoming_tokens, outgoing_tokens, n
    
    # Images processing
    def ImageCommand(self, message, prompt: str, size: list[int]):
        seed = randint(1, 1000000)
        self.__FLUX_schnell(prompt=prompt, size=size, message=message, seed=seed, num_inference_steps=4)
        self.ImageChange(message)
        return seed
    
    # Image regeneration and upscaling
    def Image_Regen_And_Upscale(self, message, prompt: str, size: list[int], seed, num_inference_steps=4):
        return self.__FLUX_schnell(prompt=prompt, size=size, message=message, seed=seed, num_inference_steps=num_inference_steps)
    
    # Free mode processing
    def FreeCommand(self, message, prompts: list[str]):
        response, incoming_tokens, outgoing_tokens = self.__gpt_4o_mini(prompt=prompts, message=message, temperature=0.7, top_p=0.85)
        prompts.append({"content": response, "role": "assistant"})
        return incoming_tokens, outgoing_tokens, prompts