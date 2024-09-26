import json
from telebot import types

# Keyboard class
class keyboards:
#Protected
    # Keyboard with 2 fields
    def _keyboard_two_blank(self, data: list[str], name: list[str]) -> types.InlineKeyboardMarkup:
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        buttons = [types.InlineKeyboardButton(str(name[i]), callback_data=str(data[i])) for i in range(len(data))]
        if len(buttons) % 2 == 0:
            [keyboard.add(buttons[i], buttons[i+1]) for i in range(0, len(buttons), 2)]
        else:
            [keyboard.add(buttons[i], buttons[i+1]) for i in range(0, len(buttons)-1, 2)]
            keyboard.add(buttons[-1])
        return keyboard
    
# Promts compression class
class PromptsCompressor:
    #__Init__
    def __init__(self):
        self.commands_size = [3, 3, 2, 5, 2, 3, 5]
        
    # Promts get function
    def get_prompt(self, info: list[str], ind: int) -> str:
        with open('ToolBox/BaseSettings/prompts.json', 'r') as file:
            commands = json.load(file)['commands'][ind]  
        response = commands[0]
        for i in range(len(info)):
            response += info[i] + commands[i+1]
        return response    