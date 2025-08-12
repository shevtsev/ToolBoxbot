import PyPDF2
from BaseSettings.config import config
from telebot import types

# Keyboard class
class keyboards:
#Protected
    # Keyboard with 2 fields
    def _keyboard_two_blank(self, data: list[str], name: list[str]) -> types.InlineKeyboardMarkup:
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        buttons = []
        
        # Сначала собираем все кнопки
        for i in range(len(data)):
            btn_name = str(name[i])
            btn = types.InlineKeyboardButton(btn_name, callback_data=str(data[i]))
            
            # Проверяем, является ли это кнопкой модели
            if "Текущая модель" in btn_name or "Назад" in btn_name:
                # Добавляем кнопки модели отдельной строкой
                keyboard.add(btn)
            else:
                buttons.append(btn)
        
        # Добавляем остальные кнопки парами
        if buttons:
            for i in range(0, len(buttons), 2):
                if i + 1 < len(buttons):
                    keyboard.add(buttons[i], buttons[i+1])
                else:
                    keyboard.add(buttons[i])
                    
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
    
    # PDF to text convertation
    def pdf_to_text(self, pdf_path: str) -> str:
        # Open the PDF file in read-binary mode
        with open(pdf_path, 'rb') as pdf_file:
            # Create a PdfReader object instead of PdfFileReader
            pdf_reader = PyPDF2.PdfReader(pdf_file)

            # Initialize an empty string to store the text
            text = ''

            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text += page.extract_text()
        return text

    # Promts get function
    def get_prompt(self, info: list[str], ind: int) -> str:
        commands = config.prompts_text['commands'][ind]
        for i, el in enumerate(self.commands_size[ind]):
            commands = commands.replace(f"[{el}]", info[i])
        return commands