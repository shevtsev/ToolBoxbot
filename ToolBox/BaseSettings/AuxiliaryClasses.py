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
    def _reply_keyboard(self, name: list[str]):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        buttons = [types.KeyboardButton(el) for el in name]
        [markup.add(btn) for btn in buttons]
        return markup
    
# Promts compression class
class PromptsCompressor:
    #__Init__
    def __init__(self):
        self.commands_size = [
                            ["TOPIC", "TA", "TONE", "STRUCT", "LENGTH", "EXTRA"], ["TOPIC", "TA", "STYLE", "LENGTH"],
                            ["TOPIC", "IDEA_NUM"], ["TYPE", "TOPIC", "TA", "LENGTH", "STYLE"],
                            ["HEADLINE", "NUM"], ["TOPIC", "KEYWORDS", "INFO", "LENGTH"],
                            ["TEXT", "LENGTH", "EXTRA"], ["TEXT", "RED_TYPE", "EXTRA"]
                            ]
        
    # Promts get function
    def get_prompt(self, info: list[str], ind: int) -> str:
        with open('ToolBox/BaseSettings/prompts.json', 'r') as file:
            commands = json.load(file)['commands'][ind]
        for i, el in enumerate(self.commands_size[ind]):
            commands = commands.replace(f"[{el}]", info[i])
        return commands
    
    # HTML tags insert function
    @staticmethod
    def html_tags_insert(response: str) -> str:
        patterns = [(r'#### (.*?)\n', r'<strong>\1</strong>\n'),
                    (r'### (.*?)\n', r'<b>\1</b>\n'),
                    (r'```(\w+)?\n(.*?)\n```', r'<pre><code \1>\n\2\n</code></pre>'),
                    (r'`(.*?)`', r'<pre>\1</pre>'),
                    (r'\*\*(.*?)\*\*', r'<i>\1</i>'),
                    (r'([*+-.=|!()_–\[\]~{}#\\`])', r'\\\1'),
                    (r'<i>(.*?)</i>', r'_\1_'),
                    (r'<strong>(.*?)</strong>', r'*__\1__*'),
                    (r'<b>(.*?)</b>', r'*\1*'),
                    (r'<pre><code (\w+)?>\n(.*?)\n</code></pre>', r'```\1\n\2\n```'),
                    (r'<pre>(.*?)</pre>', r'`\1`'),
                    (r'([<>])', r'\\\1')
                    ]
        for pattern in patterns:
            response = re.sub(pattern[0], pattern[1], response, flags=re.DOTALL)
        return response