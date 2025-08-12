import telebot
import concurrent.futures
import time
import logging
from random import randint
from telebot import types
from md2tgmd import escape
from BaseSettings.AuxiliaryClasses import PromptsCompressor, keyboards
from ToolBox_n_networks import neural_networks
from BaseSettings.config import config
from ToolBox_DataBase import DataBase

# Class initialization
pc = PromptsCompressor()
logger = logging.getLogger(__name__)

#Main functions class
class ToolBox(keyboards, neural_networks):
    def __init__(self):
        # Telegram bot initialization
        self.bot = telebot.TeleBot(token=config.token)
        # Inline keyboard blank lambda
        self.keyboard_blank = lambda self, name, data: super()._keyboard_two_blank(data, name)
        # Markup keyboard
        self.reply_keyboard = lambda self, name: super()._reply_keyboard(name)
        # Request delay
        self.__delay        = lambda message, self=self: self.bot.send_message(message.chat.id, config.delay, parse_mode='html')  
        # Start request
        self.start_request  = lambda message, self=self: self.bot.send_message(message.chat.id, config.prompts_text['hello'], reply_markup=self.keyboard_blank(self, config.start_name, config.start_data), parse_mode='html')
        # Restart request
        self.restart        = lambda message, self=self: self.bot.send_message(message.chat.id, config.choose_task, reply_markup=self.keyboard_blank(self, config.start_name, config.start_data), parse_mode='html')
        # Image change
        self.ImageChange    = lambda message, self=self: self.bot.send_message(chat_id=message.chat.id, text=config.next_step, reply_markup=self.keyboard_blank(self, ["Улучшить 🪄", "Перегенерировать 🔁", "Новая 🖼", "В меню"], ["upscale", "regenerate", "images", "exit"]), parse_mode='html')
        # Message before upscale
        self.BeforeUpscale  = lambda message, self=self: self.bot.send_message(chat_id=message.chat.id, text=config.next_step, reply_markup=self.keyboard_blank(self, ["Перегенерировать 🔁", "Новая 🖼", "В меню"], ["regenerate", "images", "exit"]), parse_mode='html')
        # Free mode request
        self.FreeArea       = lambda message, self=self: self.bot.send_message(chat_id=message.chat.id, text="Введите ваш запрос", reply_markup=self.reply_keyboard(self, ["В меню"]), parse_mode='html')
        # Tariffs area exit
        self.TariffExit     = lambda message, self=self: self.bot.send_message(chat_id=message.chat.id, text="Тарифы", reply_markup=self.keyboard_blank(self, config.tarrif_name, config.tarrif_data))
        # End tariff
        self.TarrifEnd      = lambda message, self=self: self.bot.send_message(chat_id=message.chat.id, text="У вас закончились запросы, но вы можете продлить ваш тариф.", reply_markup=self.keyboard_blank(self, config.tarrif_name, config.tarrif_data))
        # Free tariff end
        self.FreeTariffEnd  = lambda message, self=self: self.bot.send_message(chat_id=message.chat.id, text=config.limit_end, reply_markup=self.keyboard_blank(self, config.tarrif_name, config.tarrif_data))
        # Restart murkup
        self.restart_markup = lambda message, self=self: self.bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text=config.choose_task, reply_markup=self.keyboard_blank(self, config.start_name, config.start_data), parse_mode='html')
        # Image size on
        self.ImageSize_off  = lambda message, self=self: self.bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text=config.imagesize, reply_markup=self.keyboard_blank(self, config.improve_off_name, config.improve_off_data), parse_mode='html')
        # Image size off
        self.ImageSize_on   = lambda message, self=self: self.bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text=config.imagesize, reply_markup=self.keyboard_blank(self, config.improve_on_name, config.improve_on_data), parse_mode='html')
        # Model selection
        self.model_selection = lambda message, user_data, self=self: self.bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=message.message_id,
            text=f"Текущая модель: {config.model_names.get(user_data.get('images', '').split('|')[2] if '|' in user_data.get('images', '') and len(user_data.get('images', '').split('|')) > 2 else 'schnell', 'schnell')}\nВыберите новую модель для генерации:",
            reply_markup=self.keyboard_blank(
                self,
                [config.model_names[model] for model in config.tariff_models["ultra" if user_data['ultra'] else "pro" if user_data['pro'] else "basic" if user_data['basic'] else "free"]] + ["Назад"],
                [f"model_{model}" for model in config.tariff_models["ultra" if user_data['ultra'] else "pro" if user_data['pro'] else "basic" if user_data['basic'] else "free"]] + ["images"]
            )
        )
        # Image request
        self.ImageArea      = lambda message, self=self: self.bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text="Введите ваш запрос для изображений 🖼", reply_markup=self.keyboard_blank(self, ["В меню"], ["exit"]), parse_mode='html')
        # Tariff request
        self.TariffArea     = lambda message, self=self: self.bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text="Тарифы", reply_markup=self.keyboard_blank(self, config.tarrif_name, config.tarrif_data))
        # Text types
        self.Text_types     = lambda message, self=self: self.bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text="📝 Выберите тип текста", reply_markup=self.keyboard_blank(self, config.text_types_name, config.text_types_data))
        # Select one or some texts
        self.SomeTexts      = lambda message, ind, self=self: self.bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text="Хотите сделать один текст или сразу несколько?", reply_markup=self.keyboard_blank(self, ["Один", "Несколько", "Назад"], [f"one_{ind}", f"some_{ind}", "text_exit"]))
        # One text request
        self.OneTextArea    = lambda message, ind, self=self: self.bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text=config.prompts_text['text_list'][ind][0], reply_markup=self.keyboard_blank(self, ["Назад"], ["text_exit"]))
        # Some texts request
        self.SomeTextsArea  = lambda message, ind, self=self: self.bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text=config.prompts_text['few_texts_list'][ind][0], reply_markup=self.keyboard_blank(self, ["Назад"], ["text_exit"]))

#Private        
    # Text generation processing
    def __text_generation(self, prompt: list[dict], message, temperature: float = 0.5, top_p: float = 0.85) -> tuple[dict[str, str], int, int]:
        send = self.__delay(message)
        
        # Проверяем, содержит ли промпт изображение
        has_image = any(isinstance(p.get('content'), list) and 
                       any(c.get('type') == 'image_url' for c in p['content']) 
                       for p in prompt)
        
        # Если есть изображение, используем Mistral Vision
        if has_image:
            response, incoming_tokens, outgoing_tokens = super()._mistral_vision(prompt=prompt, temperature=temperature, top_p=top_p)
        else:
            # Для текстовых запросов используем Mistral Large
            response, incoming_tokens, outgoing_tokens = super()._mistral_large_text(prompt=prompt, temperature=temperature, top_p=top_p)
        
        response = str(escape(response))
        for i in range(0, len(response), 4096):
            chunk = response[i:i+4096]
            if i == 0:
                self.bot.edit_message_text(chat_id=send.chat.id, message_id=send.message_id, text=chunk, parse_mode='MarkdownV2')
            else:
                self.bot.send_message(chat_id=send.chat.id, text=chunk, parse_mode='MarkdownV2')
        return response, incoming_tokens, outgoing_tokens
        
    # Обработка изображений через FLUX API
    def __generate_image(self, message, prompt: str, size: list[int], seed: int, num_inference_steps: int, user_data: dict) -> None:
        user_id = str(message.chat.id)
        settings = user_data.get('images', '').split('|') if user_data.get('images') else ['', '', 'schnell', '', '']
        selected_model = settings[2] if len(settings) > 2 else 'schnell'
        logger.info(f"User {user_id} requested image generation. Model: {selected_model}, Size: {size}, Seed: {seed}")
        
        # Генерируем изображение
        image, status = super().generate_image(user_data, prompt, size, seed, num_inference_steps)
        
        if image:
            logger.info(f"Image successfully generated for user {user_id}")
            self.bot.send_photo(chat_id=message.chat.id, photo=image)
            return True
        else:
            error_text = status if status else "При генерации возникла ошибка, попробуйте повторить позже"
            logger.error(f"Image generation failed for user {user_id}. Status: {status}")
            self.bot.send_message(chat_id=message.chat.id, text=error_text)
            return None

#Public
    # Mistral large processing
    def mistral_large(self, prompt: str, temperature: float = 0.6, top_p: float = 0.85) -> str:
        return super()._mistral_large_text(prompt=[{"role": "user", "content": prompt}], temperature=temperature, top_p=top_p)[0]
    
    # Tariffs
    # Basic tariff
    def Basic_tariff(self, message):
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton("Подключить тариф BASIC", pay=True))
        keyboard.add(types.InlineKeyboardButton("К тарифам", callback_data="tariff_exit"))
        price = [types.LabeledPrice(label='BASIC', amount=config.price_basic)]
        try:
            self.bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
        except Exception as e:
            logger.error(f"Error while deleting message: {e}")
        self.bot.send_invoice(chat_id=message.chat.id, title='BASIC',
            description="Безлимитная генерация текста + 3 Pro-генерации изображений в день (с доступом к разным моделям)",
            invoice_payload='basic_invoice_payload',
            start_parameter='subscription',
            need_phone_number=True,
            send_phone_number_to_provider=True,
            provider_data=config.provider_data_basic,
            provider_token=config.provider_token,
            currency=config.currency, prices=price, reply_markup=keyboard)
    
    # Pro tariff
    def Pro_tariff(self, message):
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton("Подключить тариф PRO", pay=True))
        keyboard.add(types.InlineKeyboardButton("К тарифам", callback_data="tariff_exit"))
        price = [types.LabeledPrice(label='PRO', amount=config.price_pro)]
        try:
            self.bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
        except Exception as e:
            logger.error(f"Error while deleting message: {e}")
        self.bot.send_invoice(chat_id=message.chat.id, title='PRO',
            description="Безлимитная генерация текста + 10 Pro-генераций изображений в день (все модели и лоры)",
            invoice_payload='pro_invoice_payload',
            start_parameter='subscription',
            need_phone_number=True,
            send_phone_number_to_provider=True,
            provider_data=config.provider_data_pro,
            provider_token=config.provider_token,
            currency=config.currency, prices=price, reply_markup=keyboard)
    
    # Ultra tariff
    def Ultra_tariff(self, message):
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton("Подключить тариф ULTRA", pay=True))
        keyboard.add(types.InlineKeyboardButton("К тарифам", callback_data="tariff_exit"))
        price = [types.LabeledPrice(label='ULTRA', amount=config.price_ultra)]
        try:
            self.bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
        except Exception as e:
            logger.error(f"Error while deleting message: {e}")
        self.bot.send_invoice(chat_id=message.chat.id, title='ULTRA',
            description="Безлимитная генерация текста и Pro-генерация изображений (все модели и лоры без ограничений)",
            invoice_payload='ultra_invoice_payload',
            start_parameter='subscription',
            need_phone_number=True,
            send_phone_number_to_provider=True,
            provider_data=config.provider_data_ultra,
            provider_token=config.provider_token,
            currency=config.currency, prices=price, reply_markup=keyboard)
        
    # One text processing
    def TextCommands(self, message, ind: int):
        info = []
        incoming_tokens = 0; outgoing_tokens = 0
        info.append(message.text)     
        for i in range(1, len(config.prompts_text['text_list'][ind])):
            msg = self.bot.send_message(chat_id=message.chat.id, text=config.prompts_text['text_list'][ind][i])
            param = None
            
            def Param_next_step(message):
                nonlocal info, param 
                param = message.text
                info.append(param)
            
            self.bot.register_next_step_handler(msg, Param_next_step)
            start_time = time.time()
            while param is None:
                if time.time() - start_time > 300:
                    self.bot.send_message(message.chat.id, "Время ожидания истекло")
                    return 0, 0, 0
                time.sleep(0.5)
        prompt = pc.get_prompt(ind=ind, info=info)
        response, incoming_tokens, outgoing_tokens = self.__text_generation(prompt=[{ "role": "user", "content": prompt }], message=message)
        self.restart(message)
        return incoming_tokens, outgoing_tokens, 1
    
    # Some texts processing
    def SomeTextsCommand(self, message, ind: int, tokens: dict[str, int]):
        n = int(message.text)
        text_buttons = config.text_types_data[:-1]
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
        for el in range(1, len(config.prompts_text["few_texts_list"][index])):
            msg = self.bot.send_message(chat_id=message.chat.id, text=config.prompts_text["few_texts_list"][index][el])
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
        user_id = str(message.chat.id)
        # Получаем данные пользователя из базы
        db = DataBase(db_name="UsersData.db", table_name="users_data_table", titles=config.titles)
        user_data = db.load_data_from_db().get(user_id)
        
        if user_data:
            settings = user_data.get('images', '').split('|')
            selected_model = settings[2] if len(settings) > 2 else 'schnell'
            model_name = config.model_names.get(selected_model, selected_model)
            
            logger.info(f"Generating image for user {user_id}. Model: {model_name}, Settings: {user_data.get('images', '')}")
            
            # Отправляем сообщение о начале генерации
            progress_msg = self.bot.send_message(chat_id=message.chat.id, 
                                              text=f"Генерирую изображение используя модель {model_name}...\nПодождите, это должно занять несколько секунд...")
            
            # Генерируем изображение
            result = self.__generate_image(message=message, prompt=prompt, size=size, seed=seed, 
                                    num_inference_steps=4, user_data=user_data)
            
            # Удаляем сообщение о процессе
            try:
                self.bot.delete_message(chat_id=progress_msg.chat.id, message_id=progress_msg.message_id)
            except Exception as e:
                logger.error(f"Error while deleting progress message: {e}")
            
            if isinstance(result, tuple) and result[0] is None:
                # Если возникла ошибка, выводим сообщение об ошибке
                self.bot.send_message(chat_id=message.chat.id, text=result[1])
                return None
            
            # Обновляем настройки, добавляя промпт и сид
            settings = settings if settings else ['', '', 'schnell', '', '']  # Инициализируем с дефолтными значениями
            while len(settings) < 5:  # Убедимся, что у нас достаточно элементов
                settings.append('')
            settings[3] = prompt  # Добавляем промпт
            settings[4] = str(seed)  # Добавляем сид
            new_settings = '|'.join(settings)
            
            # Сохраняем обновленные настройки в базу
            db.insert_or_update_data(user_id, {'images': new_settings})
                
        self.ImageChange(message)
        return seed
    
    # Image regeneration and upscaling
    def Image_Regen_And_Upscale(self, message, prompt: str, size: list[int], seed, num_inference_steps=4):
        user_id = str(message.chat.id)
        # Получаем данные пользователя из базы
        db = DataBase(db_name="UsersData.db", table_name="users_data_table", titles=config.titles)
        user_data = db.load_data_from_db().get(user_id)
        
        if user_data:
            settings = user_data.get('images', '').split('|')
            selected_model = settings[2] if len(settings) > 2 else 'schnell'
            model_name = config.model_names.get(selected_model, selected_model)
            
            logger.info(f"Regenerating image for user {user_id}. Model: {model_name}, Settings: {user_data.get('images', '')}")
            
            # Отправляем сообщение о начале генерации
            progress_msg = self.bot.send_message(chat_id=message.chat.id, 
                                              text=f"{'Улучшаю' if num_inference_steps > 4 else 'Перегенерирую'} изображение используя модель {model_name}...\nПодождите, это должно занять несколько секунд...")
            
            result = self.__generate_image(message=message, prompt=prompt, size=size, seed=seed, 
                                      num_inference_steps=num_inference_steps, user_data=user_data)
                                      
            # Удаляем сообщение о процессе
            try:
                self.bot.delete_message(chat_id=progress_msg.chat.id, message_id=progress_msg.message_id)
            except Exception as e:
                logger.error(f"Error while deleting progress message: {e}")
            
            if isinstance(result, tuple) and result[0] is None:
                # Если возникла ошибка, выводим сообщение об ошибке
                self.bot.send_message(chat_id=message.chat.id, text=result[1])
                return None
                
            return result
    
    # Free mode processing
    def FreeCommand(self, message, prompts: list[str]):
        response, incoming_tokens, outgoing_tokens = self.__text_generation(prompt=prompts, message=message, temperature=0.7, top_p=0.85)
        prompts.append({"content": response, "role": "assistant"})
        return incoming_tokens, outgoing_tokens, prompts