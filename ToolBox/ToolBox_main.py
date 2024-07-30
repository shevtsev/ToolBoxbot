import dotenv, os, json
from threading import Thread
from ToolBox_requests import ToolBox
from ToolBox_DataBase import DataBase

#Загрузка переменных окружения
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
dotenv.load_dotenv(dotenv_path)

#class objects
tb = ToolBox()
base = DataBase()

#Bot extern
bot = tb.bot

#data base init
base.create()
db = base.load_data_from_db()

text_buttons = ["text", "images", "comm-text", "smm-text", "brainst-text", "advertising-text", "headlines-text", "seo-text", "email"]

#start
@bot.message_handler(commands=['start'])
def start_function(*message):
    global db
    id = str(message[0].chat.id)
    db[id] = [False]*8
    Thread(target=tb.start_request, args=(message)).start()

#call decorate
@bot.callback_query_handler(func=lambda call: True)
def handle_query(*call):
    global db
    id = str(call[0].message.chat.id)
    if not db.get(id, False):
        db[id] = [False]*8

    if call[0].data == text_buttons[0]:
        Thread(target=tb.text_area, args=call).start()

    elif call[0].data == text_buttons[1]:
        Thread(target=tb.ImageArea, args=call).start()
        db[id][0] = True
        base.insert_or_update_data(id, db[id])

    elif call[0].data in text_buttons:
        i = text_buttons.index(call[0].data)
        Thread(target=tb.TextArea, args=(call[0], i-2)).start()
        db[id][i-1] = True
        base.insert_or_update_data(id, db[id])
        
#text decorate
@bot.message_handler(content_types=['text'])
def text_command(*message):
    global db
    id = str(message[0].chat.id)
    if db[id][0]:
        Thread(target=tb.ImageCommand, args= message).start()
        db[id][0]=False
        base.insert_or_update_data(id, db[id])

    for i in range(len(db[id])):
        if db[id][i]:
            Thread(target=tb.TextCommands, args = (message[0], i-1)).start()
            db[id][i] = False
            base.insert_or_update_data(id, db[id])

#run bot
if __name__ == "__main__":
    bot.infinity_polling()
