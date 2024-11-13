import asyncio
from dotenv import load_dotenv
from datetime import datetime
from threading import Thread
from dateutil.relativedelta import relativedelta
from ToolBox_requests import ToolBox
from ToolBox_DataBase import DataBase

# User data initialization pattern
DATA_PATTERN = lambda text=[0]*7, sessions_messages=[], some=False, images=False, free=False, basic=False, pro=False, incoming_tokens=0, outgoing_tokens=0, free_requests=10, datetime_sub=datetime(1900,1,1,0,0,0): {'text':text, "sessions_messages": sessions_messages, "some":some, 'images':images, 'free': free, 'basic': basic, 'pro': pro, 
                                                                                                                                                                                    'incoming_tokens': incoming_tokens, 'outgoing_tokens': outgoing_tokens,
                                                                                                                                                                                    'free_requests': free_requests, 'datetime_sub': datetime_sub}

# Load environment variables
load_dotenv()

# Objects initialized
tb = ToolBox(); bot = tb.bot
base = DataBase(db_name="UsersData.db", table_name="users_data_table",
                titles={"id": "TEXT PRIMARY KEY", "text": "INTEGER[]", "sessions_messages": "TEXT[]", "some": "BOOLEAN",
                        "images": "BOOLEAN", "free" : "BOOLEAN", "basic" : "BOOLEAN",
                        "pro" : "BOOLEAN", "incoming_tokens": "INTEGER", "outgoing_tokens" : "INTEGER",
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
                if db[user_id]["pro"]:
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
                bot.delete_message(user_id, message_id=call.message.message_id)
                tb.FreeArea(call.message)
            # Tariff button
            case "tariff":
                tb.TariffArea(call.message)
    
    # Tariffs buttons
    elif call.data in ["basic", "pro"]:
        match call.data:
            # basic
            case "basic":
                if not db[user_id]['basic']:
                    tb.Basic_tariff(call.message)
                else:
                    bot.send_message(chat_id=user_id, text="Вы уже подключили тариф BASIC.")
                    tb.restart(call.message)
            # pro
            case "pro":
                if not db[user_id]['pro']:
                    tb.Pro_tariff(call.message)
                else:
                    bot.send_message(chat_id=user_id, text="Вы уже подключили тариф PRO.")
                    tb.restart(call.message)

    # Texts buttons
    elif call.data in text_buttons:
        index = text_buttons.index(call.data)
        tb.SomeTexts(call.message, index)

    # All exit buttons
    elif call.data in ["exit", "text_exit", "tariff_exit"]:
        match call.data:
            # Cancel to main menu button
            case "exit":
                db[user_id] = DATA_PATTERN(basic=db[user_id]['basic'], pro=db[user_id]['pro'], incoming_tokens=db[user_id]['incoming_tokens'],
                                        outgoing_tokens=db[user_id]['outgoing_tokens'], free_requests=db[user_id]['free_requests'], datetime_sub=db[user_id]['datetime_sub'])
                base.insert_or_update_data(user_id, db[user_id])
                bot.delete_message(user_id, call.message.message_id)
                tb.restart(call.message)
            # Cancel from text field input
            case "text_exit":
                db[user_id]['text'] = [0]*7
                db[user_id]['some'] = False
                base.insert_or_update_data(user_id, db[user_id])
                tb.Text_types(call.message)
            # Cancel from tariff area selection
            case "tariff_exit":
                bot.delete_message(user_id, call.message.message_id)
                tb.TariffExit(call.message)

    elif call.data in [f"one_{ind}" for ind in range(7)]:
        db[user_id]['text'][int(call.data[-1])] = 1
        base.insert_or_update_data(user_id, db[user_id])
        tb.OneTextArea(call.message, int(call.data[-1]))

    elif call.data in [f"some_{ind}" for ind in range(7)]:
        db[user_id]['text'][int(call.data[-1])] = 1
        db[user_id]['some'] = True
        base.insert_or_update_data(user_id, db[user_id])
        tb.SomeTextsArea(call.message, int(call.data[-1]))

def TokensCancelletionPattern(user_id: str, func, message, i: int = None) -> None:
    global db
    in_tokens = db[user_id]['incoming_tokens']
    out_tokens = db[user_id]['outgoing_tokens']
    free_requests = db[user_id]['free_requests']

    if in_tokens > 0 and out_tokens > 0 or free_requests > 0:
        if i is None:
            incoming_tokens, outgoing_tokens, db[user_id]['sessions_messages'] = func(message, db[user_id]['sessions_messages'])
            cnt = 1
        else:
            incoming_tokens, outgoing_tokens, cnt = func(message, i) if func == tb.TextCommands else func(message, i, {"incoming_tokens": in_tokens,
                                                                                                                        "outgoing_tokens": out_tokens,
                                                                                                                        "free_requests": free_requests})
        if in_tokens > 0 and out_tokens > 0:
            db[user_id]['incoming_tokens'] -= incoming_tokens
            db[user_id]['outgoing_tokens'] -= outgoing_tokens

        elif free_requests > 0:
            db[user_id]['free_requests'] -= cnt

    elif db[user_id]['free_requests'] == 0:
        tb.FreeTariffEnd(message)

    else:
        tb.TarrifEnd(message)
        db[user_id]['incoming_tokens'] = 0 if in_tokens <= 0 else in_tokens
        db[user_id]['outgoing_tokens'] = 0 if out_tokens <= 0 else out_tokens
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

    elif db[user_id]['free'] and message.text == 'В меню':
        db[user_id]['sessions_messages'] = []
        db[user_id]['free'] = False
        tb.restart(message)

    # Free mode processing
    elif db[user_id]['free']:
        TokensCancelletionPattern(user_id, tb.FreeCommand, message)

    # Text processing
    else:
        for i in range(len(db[user_id]['text'])):
            if db[user_id]['text'][i] and not db[user_id]['some']:
                TokensCancelletionPattern(user_id, tb.TextCommands, message, i)
                db[user_id]['text'][i] = 0
            elif db[user_id]['text'][i] and db[user_id]['some']:
                TokensCancelletionPattern(user_id, tb.SomeTextsCommand, message, i)
                db[user_id]['text'][i] = 0
                db[user_id]['some'] = False
    
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