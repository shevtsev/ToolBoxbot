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
                            ["TOPIC", "TA", "TONE", "STRUCT", "LENGTH", "EXTRA"], # Сommercial text
                            ["TYPE", "THEME", "TA", "NUM", "DATES"],              # Content plan
                            ["TEXT", "COMPRESS"],                                 # Compression
                            ["THEME", "LENGTH", "STYLE", "TA", "TOV", "EXTRA"],   # Blog
                            ["THEME", "LENGTH", "STYLE", "TA", "TOV", "EXTRA"],   # Longrid
                            ["TOPIC", "TA", "STYLE", "LENGTH"],                   # SMM
                            ["TOPIC", "IDEA_NUM"],                                # Brainstorm
                            ["TYPE", "THEME", "TA", "EXTRA"],                     # Advertisement
                            ["HEADLINE", "NUM"],                                  # Headlines
                            ["TOPIC", "KEYWORDS", "INFO", "LENGTH"],              # SEO
                            ["TEXT", "LENGTH", "EXTRA"],                          # News
                            ["TEXT", "RED_TYPE", "EXTRA"]                         # Editing
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
        patterns = [(r'#### (.*?)\n', r'<h1>\1</h1>\n'), # H1
                    (r'### (.*?)\n', r'<h2>\1</h2>\n'), # H2
                    (r'## (.*?)\n', r'<h3>\1</h3>\n'), # H3
                    (r'# (.*?)\n', r'<h4>\1</h4>\n'),# H4
                    (r'```(\w+)?\n(.*?)\n```', r'<pre><code \1>\n\2\n</code></pre>'), # Code and copy
                    (r'`(.*?)`', r'<pre>\1</pre>'), # Copy field
                    (r'\*\*(.*?)\*\*', r'<i>\1</i>'), # Italic
                    (r'([*+-.=|!()_–\[\]~{}#\\`])', r'\\\1'), # Special symbols
                    (r'<i>(.*?)</i>', r'_\1_'), # Italic rewrite
                    (r'<h1>(.*?)</h1>', r'*__\1__*'), # H1 rewrite
                    (r'<h2>(.*?)</h2>', r'*_\1_*'), # H2 rewrite
                    (r'<h3>(.*?)</h3>', r'_\1_'), # H3 rewrite
                    (r'<h4>(.*?)</h4>', r'*\1*'), # H4 rewrite
                    (r'<pre><code (\w+)?>\n(.*?)\n</code></pre>', r'```\1\n\2\n```'), # Code and copy rewrite
                    (r'<pre>(.*?)</pre>', r'`\1`'), # Copy field rewrite
                    (r'([<>])', r'\\\1') # Special symbols rewrite
                    ]
        for pattern in patterns:
            response = re.sub(pattern[0], pattern[1], response, flags=re.DOTALL)
        return response