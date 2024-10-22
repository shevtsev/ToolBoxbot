import asyncio
from dotenv import load_dotenv
from datetime import datetime
from threading import Thread
from dateutil.relativedelta import relativedelta
from ToolBox_requests import ToolBox
from ToolBox_DataBase import DataBase

# User data initialization pattern
DATA_PATTERN = lambda text=[0]*7, images=False, free=False, basic=False, pro=False, incoming_tokens=0, outgoing_tokens=0, free_requests=10, datetime_sub=datetime(1900,1,1,0,0,0): {'text':text, 'images':images, 'free': free, 'basic': basic, 'pro': pro, 
                                                                                                                                                                                    'incoming_tokens': incoming_tokens, 'outgoing_tokens': outgoing_tokens,
                                                                                                                                                                                    'free_requests': free_requests, 'datetime_sub': datetime_sub}
# Check for admin ids
admin_check = lambda user_id: user_id == '206635551' or user_id == '2004851715'

# Load environment variables
load_dotenv()

# Objects initialized
tb = ToolBox(); bot = tb.bot
base = DataBase(db_name="UsersData.db", table_name="users_data_table",
                titles={"id": "TEXT PRIMARY KEY", "text": "INTEGER[]", "images": "BOOLEAN",
                        "free" : "BOOLEAN", "basic" : "BOOLEAN", "pro" : "BOOLEAN",
                        "incoming_tokens": "INTEGER", "outgoing_tokens" : "INTEGER",
                        "free_requests" : "INTEGER", "datetime_sub": "DATETIME"}
                )

# Database initialization and connection
base.create(); db = base.load_data_from_db()

# Processing payment request
@bot.pre_checkout_query_handler(func=lambda query: True)
def process_pre_checkout_query(pre_checkout_query):
    bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

# Processing success payment
@bot.message_handler(content_types=['successful_payment'])
def successful_payment(message):
    global db
    user_id = str(message.chat.id)
    # tariffs pay separation
    if message.successful_payment.invoice_payload == 'basic_invoice_payload':
        db[user_id]['basic'] = True
    elif message.successful_payment.invoice_payload == 'pro_invoice_payload':
        db[user_id]['pro'] = True

    # Tokens enrollment
    db[user_id]['incoming_tokens'] = 1.7*10**5
    db[user_id]['outgoing_tokens'] = 5*10**5

    # Datetime tariff subscribe
    db[user_id]['datetime_sub'] = datetime.now().replace(microsecond=0)+relativedelta(months=1)
    base.insert_or_update_data(user_id, db[user_id])
    bot.send_message(user_id, "Спасибо за оплату! Ваша подписка активирована.")
    tb.restart(message)

# Processing start command
@bot.message_handler(commands=['start'])
def StartProcessing(message):
    global db
    user_id = str(message.chat.id)
    db[user_id] = DATA_PATTERN() if not db.get(user_id, False) else DATA_PATTERN(basic=db[user_id]['basic'], pro=db[user_id]['pro'], incoming_tokens=db[user_id]['incoming_tokens'],
                                                                                outgoing_tokens=db[user_id]['outgoing_tokens'], free_requests=db[user_id]['free_requests'], datetime_sub=db[user_id]['datetime_sub']
                                                                                )
    base.insert_or_update_data(user_id, db[user_id])
    tb.start_request(message)

# Processing callback requests
@bot.callback_query_handler(func=lambda call: True)
def CallsProcessing(call):
    global db
    user_id = str(call.message.chat.id)

    text_buttons = [
        "comm-text", "smm-text", "brainst-text",
        "advertising-text", "headlines-text", 
        "seo-text", "email"
    ]
    # User data create
    if not db.get(user_id):
        db[user_id] = DATA_PATTERN()
        base.insert_or_update_data(user_id, db[user_id])

    # Main tasks buttons
    if call.data in tb.data:
        match call.data:
            # Text button
            case "text":
                tb.Text_types(call.message)
            # Image button
            case "images":
                if db[user_id]["pro"] or admin_check(user_id):
                    db[user_id]['images'] = True
                    base.insert_or_update_data(user_id, db[user_id])
                    tb.ImageArea(call.message)
                else:
                    bot.send_message(chat_id=user_id, text="Обновите ваш тариф до PRO")
                    tb.restart(call.message)
            # Free mode button
            case "free":
                db[user_id]['free'] = True
                base.insert_or_update_data(user_id, db[user_id])
                tb.FreeArea(call.message)
            # Tariff button
            case "tariff":
                tb.TariffArea(call.message)
    
    # Tariffs buttons
    # basic
    elif call.data == "basic":
        if not db[user_id]['basic']:
            tb.Basic_tariff(call.message)
        else:
            bot.send_message(chat_id=user_id, text="Вы уже подключили тариф BASIC.")
            tb.restart(call.message)
    # pro
    elif call.data == "pro":
        if not db[user_id]['pro']:
            tb.Pro_tariff(call.message)
        else:
            bot.send_message(chat_id=user_id, text="Вы уже подключили тариф PRO.")
            tb.restart(call.message)

    # Texts buttons
    elif call.data in text_buttons:
        index = text_buttons.index(call.data)
        db[user_id]['text'][index] = 1
        base.insert_or_update_data(user_id, db[user_id])
        tb.TextArea(call.message, index)

    # Cancel to main menu button
    elif call.data == "exit":
        db[user_id] = DATA_PATTERN(basic=db[user_id]['basic'], pro=db[user_id]['pro'], incoming_tokens=db[user_id]['incoming_tokens'],
                                   outgoing_tokens=db[user_id]['outgoing_tokens'], free_requests=db[user_id]['free_requests'], datetime_sub=db[user_id]['datetime_sub'])
        base.insert_or_update_data(user_id, db[user_id])
        bot.delete_message(user_id, call.message.message_id)
        tb.restart(call.message)

def TokensCancelletionPattern(user_id: str, message, i: int = None) -> None:
    global db
    if db[user_id]['incoming_tokens'] > 0 and db[user_id]['outgoing_tokens'] > 0 or db[user_id]['free_requests'] > 0 or admin_check(user_id):
        try:
            incoming_tokens, outgoing_tokens = tb.FreeCommand(message) if i is None else tb.TextCommands(message, i)
            if db[user_id]['incoming_tokens'] > 0 and db[user_id]['outgoing_tokens'] > 0:
                db[user_id]['incoming_tokens'] -= incoming_tokens
                db[user_id]['outgoing_tokens'] -= outgoing_tokens

            elif db[user_id]['free_requests'] > 0:
                db[user_id]['free_requests'] -= 1
        except TypeError:
            pass

    elif db[user_id]['free_requests'] == 0:
        tb.FreeTariffEnd(message)

    else:
        tb.TarrifEnd(message)
        db[user_id]['incoming_tokens'] = 0 if db[user_id]['incoming_tokens'] <= 0 else db[user_id]['incoming_tokens']
        db[user_id]['outgoing_tokens'] = 0 if db[user_id]['outgoing_tokens'] <= 0 else db[user_id]['outgoing_tokens']
        tb.restart(message)

# Tasks messages processing
@bot.message_handler(content_types=['text'])
def TasksProcessing(message):
    global db
    user_id = str(message.chat.id)

    # Images processing
    if db[user_id]['images']:
        tb.ImageCommand(message)
        db[user_id]['images'] = False

    # Free mode processing
    elif db[user_id]['free']:
        TokensCancelletionPattern(user_id, message)
        db[user_id]['free'] = False

    # Text processing
    else:
        for i in range(len(db[user_id]['text'])):
            if db[user_id]['text'][i]:
                TokensCancelletionPattern(user_id, message, i)
                db[user_id]['text'][i] = 0
    
    base.insert_or_update_data(user_id, db[user_id])

# Time to end tariff check
async def end_check_tariff_time():
    while True:
        global db
        for user_id, data in db.items():
            deltaf = data['datetime_sub'] - datetime.now().replace(microsecond=0) 
            if int(deltaf.total_seconds()) <= 0 and (data['basic'] or data['pro']):
                db[user_id] = DATA_PATTERN(text=data['text'], images=data['images'], free=data['free'], free_requests=data['free_requests'])
                base.insert_or_update_data(user_id, db[user_id])
        await asyncio.sleep(10)

# Bot launch
if __name__ == "__main__":
    Thread(target=bot.infinity_polling).start()
    asyncio.run(end_check_tariff_time())
    