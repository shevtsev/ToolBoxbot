import random, string, asyncio, base64, os, PyPDF2
from telebot import types
from dotenv import load_dotenv
from datetime import datetime
from threading import Thread
from dateutil.relativedelta import relativedelta
from ToolBox_requests import ToolBox
from ToolBox_DataBase import DataBase

# Number of text types
N = 12
# User data initialization pattern
DATA_PATTERN = lambda text=[0]*N, sessions_messages=[], some=False, images="0", free=False, basic=False, pro=False, incoming_tokens=0, outgoing_tokens=0, free_requests=10, datetime_sub=datetime.now().replace(microsecond=0)+relativedelta(days=1), promocode="", ref='': {'text':text, "sessions_messages": sessions_messages, "some":some, 'images':images, 'free': free, 'basic': basic, 'pro': pro, 
                                                                                                                                                                                                                                                                             'incoming_tokens': incoming_tokens, 'outgoing_tokens': outgoing_tokens,
                                                                                                                                                                                                                                                                             'free_requests': free_requests, 'datetime_sub': datetime_sub, 'promocode': promocode, 'ref': ref}

# Load environment variables
load_dotenv()

# Objects initialized
tb = ToolBox(); bot = tb.bot
base = DataBase(db_name="UsersData.db", table_name="users_data_table",
                titles={"id": "TEXT PRIMARY KEY", "text": "INTEGER[]", "sessions_messages": "TEXT[]", "some": "BOOLEAN",
                        "images": "CHAR", "free" : "BOOLEAN", "basic" : "BOOLEAN",
                        "pro" : "BOOLEAN", "incoming_tokens": "INTEGER", "outgoing_tokens" : "INTEGER",
                        "free_requests" : "INTEGER", "datetime_sub": "DATETIME", "promocode": "TEXT", "ref": "TEXT"}
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

    # User data initialization if not exist in database
    if not db.get(user_id, False):
        db[user_id] = DATA_PATTERN()

    # tariffs pay separation
    if message.successful_payment.invoice_payload == 'basic_invoice_payload':
        db[user_id]['basic'] = True
    elif message.successful_payment.invoice_payload == 'pro_invoice_payload':
        db[user_id]['pro'] = True
        db[user_id]['basic'] = True

    # Tokens enrollment
    db[user_id]['incoming_tokens'] = 1.7*10**5
    db[user_id]['outgoing_tokens'] = 5*10**5

    # Datetime tariff subscribe
    db[user_id]['datetime_sub'] = datetime.now().replace(microsecond=0)+relativedelta(months=1)
    Thread(target=base.insert_or_update_data, args=(user_id, db[user_id])).start()
    bot.send_message(user_id, "Спасибо за оплату! Ваша подписка активирована.")
    tb.restart(message)

# Processing start command
@bot.message_handler(commands=['start'])
def StartProcessing(message):
    global db
    user_id = str(message.chat.id)
    db[user_id] = DATA_PATTERN() if not db.get(user_id, False) else DATA_PATTERN(basic=db[user_id]['basic'], pro=db[user_id]['pro'], incoming_tokens=db[user_id]['incoming_tokens'],
                                                                                outgoing_tokens=db[user_id]['outgoing_tokens'], free_requests=db[user_id]['free_requests'], datetime_sub=db[user_id]['datetime_sub'],
                                                                                promocode=db[user_id]['promocode'], ref=db[user_id]['ref']
                                                                                )
    Thread(target=base.insert_or_update_data, args=(user_id, db[user_id])).start()
    tb.start_request(message)

# Tariff information show
@bot.message_handler(commands=['profile'])
def personal_account(message):
    global db
    user_id = str(message.chat.id)

    # User data initialization if not exist in database
    if not db.get(user_id, False):
        db[user_id] = DATA_PATTERN()

    if db[user_id]['basic'] and (not db[user_id]['pro']):
        bot.send_message(chat_id=user_id, text=f"Подписка: BASIC\nТекстовые генерации: безлимит\nГенерация изображений: нет\nСрок окончания подписки: {db[user_id]["datetime_sub"].strftime("%d.%m.%y")}", parse_mode='html')
    elif db[user_id]['basic'] and db[user_id]['pro']:
        bot.send_message(chat_id=user_id, text=f"Подписка: PRO\nТекстовые генерации: безлимит\nГенерация изображений: безлимит\nСрок окончания подписки: {db[user_id]["datetime_sub"].strftime("%d.%m.%y")}", parse_mode='html')
    else:
        bot.send_message(chat_id=user_id, text=f"У вас нет подписки\nТекстовые генерации: 10 в день, осталось:{db[user_id]['free_requests']}\nГенерация изображений: нет", parse_mode='html')

@bot.message_handler(commands=['stat'])
def show_stat(message):
    global db
    user_id = str(message.chat.id)
    if user_id in ['2004851715', '206635551']:
        bot.send_message(chat_id=user_id, text=f"Всего пользователей: {len(db)}\nС промокодом: {len([1 for el in db.values() if el['promocode']!=''])}")

# Processing callback requests
@bot.callback_query_handler(func=lambda call: True)
def CallsProcessing(call):
    global db
    user_id = str(call.message.chat.id)
    text_buttons = [
        "comm-text", "content-plan", "summarization",
        "blog", "longrid", "smm-text", "brainst-text",
        "advertising-text", "headlines-text", "seo-text",
        "news", "editing"
    ]
    avalible = [text_buttons.index(el) for el in ["comm-text", "blog", "longrid", "smm-text", "advertising-text", "seo-text", "news"]]

    # User data create
    if not db.get(user_id):
        db[user_id] = DATA_PATTERN()
        Thread(target=base.insert_or_update_data, args=(user_id, db[user_id])).start()

    # Main tasks buttons
    if call.data in tb.data:
        match call.data:
            # Text button
            case "text":
                tb.Text_types(call.message)
            # Image button
            case "images":
                db[user_id]['text'] = [0]*N
                if db[user_id]["pro"]:
                    db[user_id]["images"] = db[user_id]["images"][0]
                    if db[user_id]["images"] == "0":
                        tb.ImageSize_off(call.message)
                    else:
                        tb.ImageSize_on(call.message)
                    Thread(target=base.insert_or_update_data, args=(user_id, db[user_id])).start()
                else:
                    bot.send_message(chat_id=user_id, text="Обновите ваш тариф до PRO")
                    tb.restart(call.message)
            # Free mode button
            case "free":
                db[user_id]['text'] = [0]*N
                db[user_id]['free'] = True
                Thread(target=base.insert_or_update_data, args=(user_id, db[user_id])).start()
                bot.delete_message(user_id, message_id=call.message.message_id)
                tb.FreeArea(call.message)
            # Tariff button
            case "tariff":
                tb.TariffArea(call.message)
    
    # Image size buttons
    elif call.data in ["576x1024", "1024x1024", "1024x576"]:
        db[user_id]['images'] += f'|{call.data}'
        Thread(target=base.insert_or_update_data, args=(user_id, db[user_id])).start()
        tb.ImageArea(call.message)

    # Prompts imporove
    elif call.data in ["improve_prompts_off", "improve_prompts_on"]:
        if call.data == "improve_prompts_off":
            db[user_id]['images'] = '1'
            tb.ImageSize_on(call.message)
        else:
            db[user_id]['images'] = '0'
            tb.ImageSize_off(call.message)
        Thread(target=base.insert_or_update_data, args=(user_id, db[user_id])).start()
    
    # Prompts upscale and regenerate
    elif call.data in ["upscale", "regenerate"]:
        improve_prompts, size, prompt, seed = db[user_id]["images"].split('|')
        size = [int(el) for el in size.split('x')]
        match call.data:
            case "upscale":
                bot.delete_message(user_id, call.message.message_id)
                thr=Thread(target=tb.Image_Regen_And_Upscale, args=(call.message, prompt, size, int(seed), 30))
                thr.start(); thr.join()
                tb.BeforeUpscale(call.message)
            case "regenerate":
                bot.delete_message(user_id, call.message.message_id)
                seed = random.randint(1, 1000000)
                thr=Thread(target=tb.Image_Regen_And_Upscale, args=(call.message, prompt, size, seed))
                thr.start()
                db[user_id]["images"] = '|'.join(db[user_id]["images"].split('|')[:-1])+'|'+str(seed)
                Thread(target=base.insert_or_update_data, args=(user_id, db[user_id])).start()
                thr.join()
                tb.ImageChange(call.message)

    # Tariffs buttons
    elif call.data in ["basic", "pro", "promo", "ref"]:
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
            # promo
            case "promo":
                if (not db[user_id]['pro']):
                    msg = bot.send_message(chat_id=user_id, text="Введите ваш промокод")
                    def get_promo_code(message):
                        if message.text.lower() == "newyear" and db[user_id]['promocode']!=message.text.lower() or message.text in [us['ref'] for us in db.values()] and db[user_id]['ref']!=message.text:
                            if message.text in [us['ref'] for us in db.values()] and db[user_id]['ref']!=message.text:
                                uid = [key for key, val in db.items() if message.text == val['ref']][0]
                                db[uid]['pro'] = True
                                db[uid]['basic'] = True
                                db[uid]['incoming_tokens'] = 1.7*10**5
                                db[uid]['outgoing_tokens'] = 5*10**5
                                db[uid]['promocode'] = message.text.lower()
                                db[uid]['datetime_sub'] = datetime.now().replace(microsecond=0)+relativedelta(days=10)
                                
                            db[user_id]['pro'] = True
                            db[user_id]['basic'] = True
                            db[user_id]['incoming_tokens'] = 1.7*10**5
                            db[user_id]['outgoing_tokens'] = 5*10**5
                            db[user_id]['promocode'] = message.text.lower()
                            db[user_id]['datetime_sub'] = datetime.now().replace(microsecond=0)+relativedelta(months=1)
                            Thread(target=base.insert_or_update_data, args=(user_id, db[user_id])).start()
                            bot.send_message(chat_id=user_id, text="Ваша подписка активирвана. Приятного использования ☺️", parse_mode='html')
                        else:
                            bot.send_message(chat_id=user_id, text="Неверный промокод")
                        tb.restart(message)
                    bot.register_next_step_handler(msg, get_promo_code)
                else:
                    bot.send_message(chat_id=user_id, text="Вы уже подключили тариф PRO или уже активировали промокод")
                    tb.restart(call.message)
            # Referal link
            case "ref":
                if db[user_id]['ref'] == '':
                    # Generate a referal code
                    generate_referal_code = lambda length = 10: ''.join(random.choices(string.ascii_letters + string.digits, k=length))
                    db[user_id]['ref'] = generate_referal_code()

                referal = db[user_id]['ref']
                bot.send_message(chat_id=user_id, text=f"Приглашайте друзей и пользуйтесь ботом бесплатно! За каждого приглашённого друга вы получаете +10 дней бесплатного безлимита на генерацию текста и изображений, а друг получит целый месяц такого же тарифа 💰 \n\nПросто отправьте другу ваш реферальный код — его надо будет ввести во вкладке «Промокод» (раздел «Тарифы») ⌨️\nВаш реферальный код: {referal}", parse_mode='html')
                tb.restart(call.message)
                Thread(target=base.insert_or_update_data, args=(user_id, db[user_id])).start()

    # Texts buttons
    elif call.data in text_buttons:
        index = text_buttons.index(call.data)
        if index in avalible:
            tb.SomeTexts(call.message, avalible.index(index))
        else:
            db[user_id]['text'][index] = 1
            Thread(target=base.insert_or_update_data, args=(user_id, db[user_id])).start()
            tb.OneTextArea(call.message, index)

    # All exit buttons
    elif call.data in ["exit", "text_exit", "tariff_exit"]:
        match call.data:
            # Cancel to main menu button
            case "exit":
                db[user_id] = DATA_PATTERN(images=db[user_id]['images'].split('|')[0], basic=db[user_id]['basic'], pro=db[user_id]['pro'], incoming_tokens=db[user_id]['incoming_tokens'],
                                        outgoing_tokens=db[user_id]['outgoing_tokens'], free_requests=db[user_id]['free_requests'],
                                        datetime_sub=db[user_id]['datetime_sub'], promocode=db[user_id]['promocode'], ref=db[user_id]['ref'])
                Thread(target=base.insert_or_update_data, args=(user_id, db[user_id])).start()
                tb.restart_markup(call.message)
            # Cancel from text field input
            case "text_exit":
                db[user_id]['text'] = [0]*N
                db[user_id]['some'] = False
                Thread(target=base.insert_or_update_data, args=(user_id, db[user_id])).start()
                tb.Text_types(call.message)
            # Cancel from tariff area selection
            case "tariff_exit":
                bot.delete_message(user_id, call.message.message_id)
                tb.TariffExit(call.message)

    # One text area buttons
    elif call.data in [f"one_{ind}" for ind in range(N)]:
        index = avalible[int(call.data[-1])]
        db[user_id]['text'][index] = 1
        Thread(target=base.insert_or_update_data, args=(user_id, db[user_id])).start()
        tb.OneTextArea(call.message, index)

    # Some texts area buttons
    elif call.data in [f"some_{ind}" for ind in range(N)]:
        index = avalible[int(call.data[-1])]
        db[user_id]['text'][index] = 1
        db[user_id]['some'] = True
        Thread(target=base.insert_or_update_data, args=(user_id, db[user_id])).start()
        tb.SomeTextsArea(call.message, int(call.data[-1]))

# Text generation pattern
def TokensCancelletionPattern(user_id: str, func, message, i: int = None) -> None:
    global db
    in_tokens = db[user_id]['incoming_tokens']
    out_tokens = db[user_id]['outgoing_tokens']
    free_requests = db[user_id]['free_requests']

    if in_tokens > 0 and out_tokens > 0 or free_requests > 0:
        if i is None:
            incoming_tokens, outgoing_tokens, db[user_id]['sessions_messages'] = func(message, db[user_id]['sessions_messages']); cnt = 1
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

def pdf_to_text(pdf_path):
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

# Tasks messages processing
@bot.message_handler(func=lambda message: True, content_types=['text', 'photo', 'document'])
def TasksProcessing(message):
    global db
    user_id = str(message.chat.id)

    # User data initialization if not exist in database
    if not db.get(user_id, False):
        db[user_id] = DATA_PATTERN()
        
    # Images processing
    if db[user_id]['images'] != "" and len(db[user_id]['images'].split('|')) == 2:
        improve_prompts, size = db[user_id]['images'].split('|')
        size = [int(el) for el in size.split('x')]
        prompt = message.text
        if '|' in prompt:
            prompt = prompt.replace('|', '/')
        if improve_prompts == '1':
            prompt = tb.mistral_large(tb.prompts_text["image_prompt"].replace("[PROMPT]", prompt))
        db[user_id]['images']+=f"|{prompt}"
        seed = tb.ImageCommand(message, prompt, size)
        db[user_id]['images']+=f"|{seed}"

    # Main menu exit button
    elif db[user_id]['free'] and message.text == 'В меню':
        db[user_id]['sessions_messages'] = []
        db[user_id]['free'] = False
        bot.send_message(chat_id=user_id, text='Сессия завершена', reply_markup=types.ReplyKeyboardRemove(), parse_mode='html')
        tb.restart(message)

    # Free mode processing
    elif db[user_id]['free']:
        if message.content_type == 'photo':
            photo = base64.b64encode(bot.download_file(bot.get_file(message.photo[-1].file_id).file_path)).decode()
            if message.caption is not None:
                db[user_id]['sessions_messages'].append({"content": [{"type": "text", "text": message.caption}, {"type": "image_url", "image_url": f"data:image/jpeg;base64,{photo}"}], "role": "user"})
            else:
                db[user_id]['sessions_messages'].append({"content": [{"type": "image_url", "image_url": f"data:image/jpeg;base64,{photo}"}], "role": "user"})
        elif message.content_type == "document":
            file_info = bot.get_file(message.document.file_id)
            try:
                downloaded_file = bot.download_file(file_info.file_path)
                with open("temp_file", "wb") as new_file:
                    new_file.write(downloaded_file)
                if file_info.file_path[-4:] == '.pdf':
                    downloaded_file = pdf_to_text("temp_file")
                else:
                    with open("temp_file", "rb") as new_file:
                        downloaded_file = new_file.read()
                os.remove("temp_file")
            except Exception as e:
                print(e)
                downloaded_file = "Ошибка загрузки файла"

            if message.caption is not None:
                db[user_id]['sessions_messages'].append({"content": f"{message.caption} |{downloaded_file}| – это содержимое файла", "role": "user"})
            else:
                db[user_id]['sessions_messages'].append({"content": f"{downloaded_file}", "role": "user"})
        else:
            db[user_id]['sessions_messages'].append({"content": message.text, "role": "user"})
        thr = Thread(target=TokensCancelletionPattern, args=(user_id, tb.FreeCommand, message))
        thr.start(); thr.join()

    # Text processing
    else:
        for i in range(len(db[user_id]['text'])):
            if db[user_id]['text'][i] and not db[user_id]['some']:
                thr=Thread(target=TokensCancelletionPattern, args=(user_id, tb.TextCommands, message, i))
                thr.start()
                db[user_id]['text'][i] = 0
                thr.join()
            elif db[user_id]['text'][i] and db[user_id]['some']:
                thr=Thread(target=TokensCancelletionPattern, args=(user_id, tb.SomeTextsCommand, message, i))
                thr.start()
                db[user_id]['text'][i] = 0
                db[user_id]['some'] = False
                thr.join()
    Thread(target=base.insert_or_update_data, args=(user_id, db[user_id])).start()

# Time to end tariff check
async def end_check_tariff_time():
    while True:
        global db
        for user_id, data in db.items():
            deltaf = data['datetime_sub'] - datetime.now().replace(microsecond=0)
            if int(deltaf.total_seconds()) <= 0 and (data['basic'] or data['pro'] or data['free_requests']<10):
                db[user_id] = DATA_PATTERN(text=data['text'], images=data['images'],
                                        free=data['free'], promocode=data['promocode'], ref=data['ref'])
                Thread(target=base.insert_or_update_data, args=(user_id, db[user_id])).start()
        await asyncio.sleep(10)

# Bot launch
if __name__ == "__main__":
    start = lambda : bot.infinity_polling(timeout=10, long_polling_timeout = 5)
    Thread(target=start).start()
    asyncio.run(end_check_tariff_time())