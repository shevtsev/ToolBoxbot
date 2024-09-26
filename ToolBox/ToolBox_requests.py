import telebot, os, json
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
        # Request delay
        self.__delay        = lambda message, self=self: self.bot.send_message(message.chat.id, "Подождите, это должно занять несколько секунд . . .", parse_mode='html')  
        # Start request
        self.start_request  = lambda message, self=self: self.bot.send_message(message.chat.id, self.prompts_text['hello'], reply_markup=self.keyboard_blank(self, self.name, self.data), parse_mode='html')
        # Restart request
        self.restart        = lambda message, self=self: self.bot.send_message(message.chat.id, "Выберите нужную вам задачу", reply_markup=self.keyboard_blank(self, self.name, self.data), parse_mode='html')
        # Text request
        self.TextArea       = lambda message, ind, self=self: self.bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text=self.prompts_text['text_list'][ind])
        # Image request
        self.ImageArea      = lambda message, self=self: self.bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text="Введите ваш запрос для изображений 🖼", reply_markup=self.keyboard_blank(self, ["Назад"], ["exit"]), parse_mode='html')
        # Free mode request
        self.FreeArea       = lambda message, self=self: self.bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text="Введите ваш запрос", reply_markup=self.keyboard_blank(self, ["Назад"], ["exit"]), parse_mode='html')

#Private        
    # GPT 4o mini processing
    def __gpt_4o(self, prompt: str, message):
        send = self.__delay(message)
        ans, tokens = super()._gpt_4o_mini(prompt=prompt)
        if ans:
            self.bot.edit_message_text(chat_id=send.chat.id, message_id=send.message_id, text=ans, parse_mode='html')
            return tokens
        return self.bot.edit_message_text(chat_id=send.chat.id, message_id=send.message_id, text="При генерации возникла ошибка, попробуйте повторить позже")

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
        name = ["Коммерческий  🛍️", "SMM 📱", "Брейншторм 💡", "Реклама 📺", "Заголовки 🔍", "SEO 🌐", "Email 📧", "Назад"]
        data = ["comm-text", "smm-text", "brainst-text", "advertising-text", "headlines-text", "seo-text", "email", "exit"]
        return self.bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text="📝 Выберите тип текста", reply_markup=self.keyboard_blank(self, name, data))
    
    # Tariff message
    def Tariff_field(self, message):
        keyboard = self.keyboard_blank(self, ["Назад"], ["exit"])
        keyboard.add(types.InlineKeyboardButton("Оплатить", pay=True))
        price = [types.LabeledPrice(label='Оплата подписки', amount=200*100)]
        self.bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
        self.bot.send_invoice(chat_id=message.chat.id, title = 'Подписка на 5 млн токенов',
            description = 'Эта подписка дает 5 млн токенов в месяц',
            invoice_payload = 'asdasd',
            start_parameter='subscription',
            provider_token = os.environ['PROVIDE_TOKEN'],
            currency='RUB', prices=price, reply_markup=keyboard)
        
    # Texts processing
    def TextCommands(self, message, ind: int):
        info = message.text.split(';')
        tokens = 0
        if len(info)==pc.commands_size[ind]:
            prompt = pc.get_prompt(ind=ind, info=info)
            tokens = self.__gpt_4o(prompt=prompt, message=message)
        self.restart(message)
        return tokens

    # Images processing
    def ImageCommand(self, message):
        self.__kandinsky(prompt=message.text, message=message)
        return self.restart(message)

    # Free mode processing
    def FreeCommand(self, message):
        tokens = self.__gpt_4o(prompt=message.text, message=message)
        self.restart(message)
        return tokens