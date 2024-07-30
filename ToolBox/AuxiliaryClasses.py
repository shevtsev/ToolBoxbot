from telebot import types
import json

#Класс с функциями для клавиатуры
class keyboards:
    #Клавиатура с двумя кнопками
    def keyboard_two_blank(self, data: list, name: list):
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        buttons = [types.InlineKeyboardButton(str(name[i]), callback_data=str(data[i])) for i in range(len(data))]
        if len(buttons) % 2 == 0:
            [keyboard.add(buttons[i], buttons[i+1]) for i in range(0, len(buttons), 2)]
        else:
            [keyboard.add(buttons[i], buttons[i+1]) for i in range(0, len(buttons)-1, 2)]
            keyboard.add(buttons[-1])
        return keyboard
    
#Класс со всеми текстами для бота
class TextContain:
    #__Init__
    def __init__(self):
        self.commands = [3, 3, 2, 5, 2, 3, 5]
        
    #Промпты генерации текста
    def command(self, info, ind):
        with open('ToolBox/prompts.json', 'r') as file:
            commands = json.load(file)['commands']

        response = commands[ind][0]
        for i in range(len(info)):
            response += info[i] + commands[ind][i+1]
        return response    
