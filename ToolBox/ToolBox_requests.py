import telebot, os, json
from telebot import types
from BaseSettings.AuxiliaryClasses import TextContain, keyboards
from ToolBox_n_networks import neural_networks

txt = TextContain()

#commands functions class
class ToolBox(keyboards, neural_networks):
    def __init__(self):
        #telebot
        with open("ToolBox/BaseSettings/prompts.json", 'r') as file:
            self.prompts_text = json.load(file)
        self.bot = telebot.TeleBot(token=os.environ['TOOL_BOX_TG_ID'])
#Private        
    #Ожидание ответа
    def __delay(self, message):
        return self.bot.send_message(message.chat.id, "Подождите, это должно занять несколько секунд . . .", parse_mode='html')
    
    #Restart
    def restart(self, message):
        name = ["Текст 📝", "Изображения 🎨", "Свободный режим 🗽", "Тарифы 💸"]
        data = ["text", "images", "free", "tariff"]
        keyboard = super()._keyboard_two_blank(data=data, name=name)
        return self.bot.send_message(message.chat.id, "Выберите нужную вам задачу", reply_markup=keyboard, parse_mode='html')
    
    #Запуск GPT 4o mini
    def __gpt_4o(self, prompt: str, message):
        send = self.__delay(message=message)
        ans, tokens = super()._gpt_4o_mini(prompt=prompt)
        if ans:
            self.bot.edit_message_text(chat_id=send.chat.id, message_id=send.message_id, text=ans, parse_mode='html')
            return tokens
        else:
            self.bot.edit_message_text(chat_id=send.chat.id, message_id=send.message_id, text="При генерации возникла ошибка, попробуйте повторить позже")

    #Запуск Кандинского
    def __kandinsky(self, prompt: str, message)-> None:
        send = self.__delay(message=message)
        photo = super()._FusionBrain(prompt=prompt)
        if photo:
            self.bot.send_photo(chat_id=message.chat.id, photo=photo)
            self.bot.delete_message(chat_id=send.chat.id, message_id=send.message_id)
        else:
            self.bot.edit_message_text(chat_id=send.chat.id, message_id=send.message_id, text="При генерации возникла ошибка, попробуйте повторить позже")
#Public
    #Start
    def start_request(self, message):
        name = ["Текст 📝", "Изображения 🎨", "Свободный режим 🗽", "Тарифы 💸"]
        data = ["text", "images", "free", "tariff"]
        keyboard = super()._keyboard_two_blank(data=data, name=name)
        return self.bot.send_message(message.chat.id, self.prompts_text['hello'], reply_markup=keyboard, parse_mode='html')
        
    #Текст
    def text_area(self, message):
        name = ["Коммерческий  🛍️", "SMM 📱", "Брейншторм 💡", "Реклама 📺", "Заголовки 🔍", "SEO 🌐", "Email 📧"]
        data = ["comm-text", "smm-text", "brainst-text", "advertising-text", "headlines-text", "seo-text", "email"]
        keyboard = super()._keyboard_two_blank(data=data, name=name)
        return self.bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text="📝 Выберите тип текста", reply_markup=keyboard)
    
    def tarrif_area(self, message):
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton("Оплатить", pay=True))
        keyboard.add(types.InlineKeyboardButton("Назад", callback_data="exit"))
        price = [types.LabeledPrice(label='Оплата подписки', amount=200*100)]
        self.bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
        self.bot.send_invoice(chat_id=message.chat.id, title = 'Подписка на 5 млн токенов',
            description = 'Эта подписка дает 5 млн токенов в месяц',
            invoice_payload = 'asdasd',
            start_parameter='subscription',
            provider_token = os.environ['PROVIDE_TOKEN'],
            currency='RUB', prices=price, reply_markup=keyboard)
        
###Тексты
    def TextArea(self, message, ind: int):
        return self.bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text=self.prompts_text['text_list'][ind])
        
    def TextCommands(self, message, ind: int):
        info = message.text.split(';')
        tokens = 0
        if len(info)==txt.commands_size[ind]:
            prompt = txt.command(ind=ind, info=info)
            tokens = self.__gpt_4o(prompt=prompt, message=message)
        self.restart(message=message)
        return tokens
###

###Изображения
    def ImageArea(self, message):
        return self.bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text="Введите ваш запрос для изображений 🖼")
    
    def ImageCommand(self, message):
        self.__kandinsky(prompt=message.text, message=message)
        return self.restart(message=message)
###

###Свобдный режим
    def FreeArea(self, message):
        return self.bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text="Введите ваш запрос")
    
    def FreeCommand(self, message):
        tokens = self.__gpt_4o(prompt=message.text, message=message)
        self.restart(message=message)
        return tokens
###