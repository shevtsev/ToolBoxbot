from dotenv import load_dotenv
from ToolBox_requests import ToolBox
from ToolBox_DataBase import DataBase

# Load environment variables
load_dotenv()

# Objects initialized
tb = ToolBox()
base = DataBase()
bot = tb.bot

# Database initialization and connection
base.create()
db = base.load_data_from_db()

# Processing payment request
@bot.pre_checkout_query_handler(func=lambda query: True)
def process_pre_checkout_query(pre_checkout_query):
    bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

# Processing success payment
@bot.message_handler(content_types=['successful_payment'])
def successful_payment(message):
    global db
    user_id = str(message.chat.id)
    user_data = db[user_id]

    user_data['subscribe'] = True
    user_data['tokens'] = 5*10**6
    base.insert_or_update_data(user_id, user_data)
    bot.send_message(user_id, "Спасибо за оплату! Ваша подписка активирована.")
    tb.restart(message)

# Processing start command
@bot.message_handler(commands=['start'])
def start_function(message):
    global db
    user_id = str(message.chat.id)
    user_data = {'text':[False]*7, 'images':False, 'free': False, 'subscribe': False, 'tokens': 10} if db.get(user_id, False) else {'text':[False]*7, 'images':False, 'free': False, 'subscribe': db[user_id]['subscribe'], 'tokens': db[user_id]['tokens']}
    
    base.insert_or_update_data(user_id, user_data)
    tb.start_request(message)

# Processing callback requests
@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    global db
    user_id = str(call.message.chat.id)

    text_buttons = [
        "comm-text", "smm-text", 
        "brainst-text", "advertising-text", "headlines-text", 
        "seo-text", "email"
    ]
    if not db.get(user_id):
        user_data = {'text':[False]*7, 'images': False, 'free': False, 'subscribe': False, 'tokens': 10}
        base.insert_or_update_data(user_id, user_data)
    else:  
        user_data = db[user_id]

    if call.data in tb.data:

        match call.data:
            case "text":
                tb.Text_types(call.message)
            case "images":
                user_data['images'] = True
                base.insert_or_update_data(user_id, user_data)
                tb.ImageArea(call.message)
            case "free":
                user_data['free'] = True
                base.insert_or_update_data(user_id, user_data)
                tb.FreeArea(call.message)
            case "tariff":
                if not user_data['subscribe']:
                    tb.Tariff_field(call.message) 
                else:
                    bot.send_message(chat_id=user_id, text="Вы уже оплатили подписку")
                    tb.restart(call.message)

    elif call.data in text_buttons:
        index = text_buttons.index(call.data)

        user_data['text'][index] = True
        base.insert_or_update_data(user_id, user_data)
        tb.TextArea(call.message, index)

    elif call.data == "exit":
        bot.delete_message(user_id, call.message.message_id)
        tb.restart(call.message)

# Text messages processing
@bot.message_handler(content_types=['text'])
def text_command(message):
    global db
    user_id = str(message.chat.id)
    user_data = db[user_id]

    if user_data['images']:
        tb.ImageCommand(message)
        user_data['images'] = False

    elif user_data['free']:
        if user_data['tokens'] > 0:
            tokens = tb.FreeCommand(message)
            if type(tokens)==int:
                user_data['tokens'] -= tokens
            user_data['free'] = False
        else:
            bot.send_message(chat_id=user_id, text="У вас закончились токены.")
            user_data['tokens'] = 0
            user_data['free'] = False
            tb.restart(message)

    else:
        for i in range(len(user_data['text'])):
            if user_data['text'][i]:
                if user_data['tokens'] > 0:
                    tokens = tb.TextCommands(message, i)
                    if type(tokens)==int:
                        user_data['tokens'] -= tokens
                    user_data['text'][i] = False
                else:
                    bot.send_message(chat_id=user_id, text="У вас закончились токены.")
                    user_data['tokens'] = 0
                    user_data['text'][i] = False
                    tb.restart(message)
    
    base.insert_or_update_data(user_id, user_data)

# Bot launch
if __name__ == "__main__":
    bot.infinity_polling()