import json, re
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
        self.commands_size = [
                            ["topic", "TA", "length"], ["topic", "style", "length"],
                            ["topic", "ideas_num"], ["type", "topic", "TA", "length", "style"],
                            ["title", "options_num"], ["topic", "keywords_w_uses_num", "length"],
                            ["topic", "style", "tone", "length", "sender"]
                            ]
        
    # Promts get function
    @staticmethod
    def get_prompt(info: list[str], ind: int) -> str:
        with open('ToolBox/BaseSettings/prompts.json', 'r') as file:
            commands = json.load(file)['commands'][ind]  
        response = commands[0]
        for i in range(len(info)):
            response += info[i] + commands[i+1]
        return response
    
    # HTML tags insert function
    @staticmethod
    def html_tags_insert(response: str) -> str:
        patterns = [(r'#### (.*?)\n', r'<b><u>\1</u></b>\n'),
                    (r'### (.*?)\n', r'<u>\1</u>\n'),
                    (r'\*\*(.*?)\*\*', r'<b>\1</b>'),
                    (r'\*(.*?)\*', r'<i>\1</i>')]
        for pattern in patterns:
            response = re.sub(pattern[0], pattern[1], response)
        return response