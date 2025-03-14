import random, string, asyncio, base64, os, time, logging
from telebot import types
from datetime import datetime
from threading import Thread
from dateutil.relativedelta import relativedelta
from ToolBox_requests import ToolBox, pc
from ToolBox_DataBase import DataBase
from BaseSettings.config import config

# Objects initialized
tb = ToolBox(); bot = tb.bot
base = DataBase(db_name="UsersData.db", table_name="users_data_table", titles=config.titles)
logger = logging.getLogger(__name__)

# Database initialization and connection
base.create(); db = base.load_data_from_db()

# Update database short function
def update_db(uid: str|int, change_vals:dict[str, str|int|bool], key:str, value:str|int|bool=None) -> dict[str, str|int|bool]:
    global db
    if value is None:
        value = config.start_params()[key]
    db[uid][key] = value
    change_vals[key] = db[uid][key]
    return change_vals

# Processing payment request
@bot.pre_checkout_query_handler(func=lambda query: True)
def process_pre_checkout_query(pre_checkout_query):
    bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

# Processing success payment
@bot.message_handler(content_types=['successful_payment'])
def successful_payment(message):
    global db
    user_id = str(message.chat.id)
    change_vals = {}
    # User data initialization if not exist in database
    if not db.get(user_id, False):
        db[user_id] = config.start_params()

    # tariffs pay separation
    if message.successful_payment.invoice_payload == 'basic_invoice_payload':
        change_vals = update_db(user_id, change_vals, 'basic', True)
    elif message.successful_payment.invoice_payload == 'pro_invoice_payload':
        change_vals = update_db(user_id, change_vals, 'pro', True)
        change_vals = update_db(user_id, change_vals, 'basic', True)

    # Tokens enrollment
    change_vals = update_db(user_id, change_vals, 'incoming_tokens', 1.7*10**5)
    change_vals = update_db(user_id, change_vals, 'outgoing_tokens', 5*10**5)

    # Datetime tariff subscribe
    change_vals = update_db(user_id, change_vals, 'datetime_sub', datetime.now().replace(microsecond=0)+relativedelta(months=2))
    
    Thread(target=base.insert_or_update_data, args=(user_id, change_vals)).start()
    logger.info(f"{message.successful_payment.invoice_payload.split('_')[0]} Subscribe activation for user {user_id}")
    bot.send_message(user_id, "Спасибо за оплату! Ваша подписка активирована.")
    tb.restart(message)

# Processing start command
@bot.message_handler(commands=['start'])
def StartProcessing(message):
    global db
    user_id = str(message.chat.id)
    change_vals = {}
    if not db.get(user_id, False):
        db[user_id] = config.start_params()
        Thread(target=base.insert_or_update_data, args=(user_id, db[user_id])).start()
    else:
        change_vals = update_db(user_id, change_vals, 'text')
        change_vals = update_db(user_id, change_vals, 'images')
        change_vals = update_db(user_id, change_vals, 'free')
        change_vals = update_db(user_id, change_vals, 'sessions_messages')

        Thread(target=base.insert_or_update_data, args=(user_id, change_vals)).start()
    tb.start_request(message)
    logger.info(f"Start command processing for user {user_id}")

# Tariff information show
@bot.message_handler(commands=['profile'])
def personal_account(message):
    global db
    user_id = str(message.chat.id)

    # User data initialization if not exist in database
    if not db.get(user_id, False):
        db[user_id] = config.start_params()
        Thread(target=base.insert_or_update_data, args=(user_id, db[user_id])).start()

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
    if user_id in config.admin_ids:
        bot.send_message(chat_id=user_id, text=f"Всего пользователей: {len(db)}\nС промокодом: {len([1 for el in db.values() if el['promocode']!=''])}")

# Processing callback requests
@bot.callback_query_handler(func=lambda call: True)
def CallsProcessing(call):
    global db
    user_id = str(call.message.chat.id)
    change_vals = {}
    text_buttons = config.text_types_data[:-1]
    avalible = [text_buttons.index(el) for el in ["comm-text", "blog", "longrid", "smm-text", "advertising-text", "seo-text", "news"]]
    
    # User data create
    if not db.get(user_id):
        db[user_id] = config.start_params()
        Thread(target=base.insert_or_update_data, args=(user_id, db[user_id])).start()

    # Main tasks buttons
    if call.data in config.start_data:
        match call.data:
            # Text button
            case "text":
                tb.Text_types(call.message)
            # Image button
            case "images":
                change_vals = update_db(user_id, change_vals, 'text')
                change_vals = update_db(user_id, change_vals, 'free')
                change_vals = update_db(user_id, change_vals, 'sessions_messages')
                
                if db[user_id]["pro"]:
                    change_vals = update_db(user_id, change_vals, 'images', db[user_id]["images"][0])
                    if db[user_id]["images"] == "0":
                        tb.ImageSize_off(call.message)
                    else:
                        tb.ImageSize_on(call.message)
                else:
                    bot.send_message(chat_id=user_id, text="Обновите ваш тариф до PRO")
                    tb.restart(call.message)
            # Free mode button
            case "free":
                change_vals = update_db(user_id, change_vals, 'text')
                change_vals = update_db(user_id, change_vals, 'free', True)
                try:
                    bot.delete_message(user_id, message_id=call.message.message_id)
                except Exception as e:
                    logger.error(f"Error while deleting message: {e}")
                tb.FreeArea(call.message)
            # Tariff button
            case "tariff":
                tb.TariffArea(call.message)
    
    # Image size buttons
    elif call.data in config.improve_off_data[:3]:
        change_vals = update_db(user_id, change_vals, 'images', db[user_id]["images"]+f'|{call.data}')
        tb.ImageArea(call.message)

    # Prompts imporove
    elif call.data in ["improve_prompts_off", "improve_prompts_on"]:
        if call.data == "improve_prompts_off":
            change_vals = update_db(user_id, change_vals, 'images', '1')
            tb.ImageSize_on(call.message)
        else:
            change_vals = update_db(user_id, change_vals, 'images')
            tb.ImageSize_off(call.message)
    
    # Prompts upscale and regenerate
    elif call.data in ["upscale", "regenerate"]:
        improve_prompts, size, prompt, seed = db[user_id]["images"].split('|')
        size = [int(el) for el in size.split('x')]
        match call.data:
            case "upscale":
                try:
                    bot.delete_message(user_id, call.message.message_id)
                except Exception as e:
                    logger.error(f"Error while deleting message: {e}")
                thr=Thread(target=tb.Image_Regen_And_Upscale, args=(call.message, prompt, size, int(seed), 30))
                thr.start(); thr.join()
                tb.BeforeUpscale(call.message)
            case "regenerate":
                try:
                    bot.delete_message(user_id, call.message.message_id)
                except Exception as e:
                    logger.error(f"Error while deleting message: {e}")
                seed = random.randint(1, 1000000)
                thr=Thread(target=tb.Image_Regen_And_Upscale, args=(call.message, prompt, size, seed))
                thr.start()
                change_vals = update_db(user_id, change_vals, 'images',
                                        '|'.join(db[user_id]["images"].split('|')[:-1])+'|'+str(seed))
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
                msg = bot.send_message(chat_id=user_id, text="Введите ваш промокод")
                def get_promo_code(message):
                    nonlocal change_vals
                    change_vals2 = {}
                    if message.text.lower() == "vesnagpt" and db[user_id]['promocode']!=message.text.lower() or message.text in [us['ref'] for us in db.values()] and db[user_id]['ref']!=message.text:
                        if message.text in [us['ref'] for us in db.values()] and db[user_id]['ref']!=message.text:
                            uid = [key for key, val in db.items() if message.text == val['ref']][0]
                            change_vals2 = update_db(uid, change_vals2, 'pro', True)
                            change_vals2 = update_db(uid, change_vals2, 'basic', True)
                            change_vals2 = update_db(uid, change_vals2, 'incoming_tokens', 1.7*10**5)
                            change_vals2 = update_db(uid, change_vals2, 'outgoing_tokens', 5*10**5)
                            change_vals2 = update_db(uid, change_vals2, 'promocode', db[user_id]['ref'])
                            change_vals2 = update_db(uid, change_vals2, 'datetime_sub',
                                                        db[uid]['datetime_sub']+relativedelta(days=10))
                            Thread(target=base.insert_or_update_data, args=(uid, change_vals2)).start()
                            logger.info(f"User {uid} subscribe was extended to 10 days, date of end: {db[uid]['datetime_sub']}")

                        change_vals = update_db(user_id, change_vals, 'pro', True)
                        change_vals = update_db(user_id, change_vals, 'basic', True)
                        change_vals = update_db(user_id, change_vals, 'incoming_tokens', 1.7*10**5)
                        change_vals = update_db(user_id, change_vals, 'outgoing_tokens', 5*10**5) 
                        change_vals = update_db(user_id, change_vals, 'promocode', message.text.lower())
                        change_vals = update_db(user_id, change_vals, 'datetime_sub',
                                                        db[user_id]['datetime_sub']+relativedelta(months=1))
                        Thread(target=base.insert_or_update_data, args=(user_id, change_vals)).start()
                        logger.info(f"User {user_id} promocode is activated before {db[user_id]['datetime_sub']}")
                        bot.send_message(chat_id=user_id, text="Ваша подписка активирвана. Приятного использования ☺️", parse_mode='html')
                    else:
                        bot.send_message(chat_id=user_id, text="Неверный промокод")
                    tb.restart(message)
                bot.register_next_step_handler(msg, get_promo_code)

            # Referal link
            case "ref":
                if db[user_id]['ref'] == '':
                    # Generate a referal code
                    generate_referal_code = lambda length = 10: ''.join(random.choices(string.ascii_letters + string.digits, k=length))
                    change_vals = update_db(user_id, change_vals, 'ref', generate_referal_code())

                referal = db[user_id]['ref']
                bot.send_message(chat_id=user_id, text=f"Приглашайте друзей и пользуйтесь ботом бесплатно! За каждого приглашённого друга вы получаете +10 дней бесплатного безлимита на генерацию текста и изображений, а друг получит целый месяц такого же тарифа 💰 \n\nПросто отправьте другу ваш реферальный код — его надо будет ввести во вкладке «Промокод» (раздел «Тарифы») ⌨️\nВаш реферальный код: {referal}", parse_mode='html')
                tb.restart(call.message)

    # Texts buttons
    elif call.data in text_buttons:
        index = text_buttons.index(call.data)
        if index in avalible:
            tb.SomeTexts(call.message, avalible.index(index))
        else:
            l = config.start_params()['text'].copy(); l[index] = 1
            change_vals = update_db(user_id, change_vals, 'text', l)
            tb.OneTextArea(call.message, index)

    # All exit buttons
    elif call.data in ["exit", "text_exit", "tariff_exit"]:
        match call.data:
            # Cancel to main menu button
            case "exit":
                change_vals = update_db(user_id, change_vals, 'text')
                change_vals = update_db(user_id, change_vals, 'some')
                change_vals = update_db(user_id, change_vals, 'images', db[user_id]['images'].split('|')[0])
                change_vals = update_db(user_id, change_vals, 'free')
                change_vals = update_db(user_id, change_vals, 'sessions_messages')
                
                logger.info(f"User {user_id} exiting")
                tb.restart_markup(call.message)
            # Cancel from text field input
            case "text_exit":
                change_vals = update_db(user_id, change_vals, 'text')
                change_vals = update_db(user_id, change_vals, 'some')
                tb.Text_types(call.message)
            # Cancel from tariff area selection
            case "tariff_exit":
                try:
                    bot.delete_message(user_id, call.message.message_id)
                except Exception as e:
                    logger.error(f"Error while deleting message: {e}")
                tb.TariffExit(call.message)

    # One text area buttons
    elif call.data in [f"one_{ind}" for ind in range(12)]:
        index = avalible[int(call.data[-1])]
        l = config.start_params()['text'].copy(); l[index] = 1
        change_vals = update_db(user_id, change_vals, 'text', l)
        tb.OneTextArea(call.message, index)

    # Some texts area buttons
    elif call.data in [f"some_{ind}" for ind in range(12)]:
        index = avalible[int(call.data[-1])]
        l = config.start_params()['text'].copy(); l[index] = 1
        change_vals = update_db(user_id, change_vals, 'text', l)
        change_vals = update_db(user_id, change_vals, 'some', True)
        tb.SomeTextsArea(call.message, int(call.data[-1]))

    if len(change_vals) > 0:
        Thread(target=base.insert_or_update_data, args=(user_id, change_vals)).start()

# Text generation pattern
def TokensCancelletionPattern(user_id: str, func, message, i: int = None) -> None:
    global db
    change_vals = {} 

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
            change_vals = update_db(user_id, change_vals, 'incoming_tokens', db[user_id]['incoming_tokens']-incoming_tokens)
            change_vals = update_db(user_id, change_vals, 'outgoing_tokens', db[user_id]['outgoing_tokens']-outgoing_tokens) 

        elif free_requests > 0:
            change_vals = update_db(user_id, change_vals, 'free_requests', db[user_id]['free_requests']-cnt)

    elif db[user_id]['free_requests'] == 0:
        tb.FreeTariffEnd(message)

    else:
        tb.TarrifEnd(message)
        change_vals = update_db(user_id, change_vals, 'incoming_tokens') if in_tokens <= 0 else in_tokens
        change_vals = update_db(user_id, change_vals, 'outgoing_tokens') if out_tokens <= 0 else out_tokens
        tb.restart(message)
    Thread(target=base.insert_or_update_data, args=(user_id, change_vals)).start()

# Tasks messages processing
@bot.message_handler(func=lambda message: True, content_types=['text', 'photo', 'document'])
def TasksProcessing(message):
    global db
    user_id = str(message.chat.id)
    change_vals = {}

    # User data initialization if not exist in database
    if not db.get(user_id, False):
        db[user_id] = config.start_params()
        
    # Images processing
    if db[user_id]['images'] != "" and len(db[user_id]['images'].split('|')) == 2:
        improve_prompts, size = db[user_id]['images'].split('|')
        size = [int(el) for el in size.split('x')]
        prompt = message.text
        if '|' in prompt:
            prompt = prompt.replace('|', '/')
        if improve_prompts == '1':
            prompt = tb.mistral_large(config.prompts_text["image_prompt"].replace("[PROMPT]", prompt))
        change_vals = update_db(user_id, change_vals, 'images', db[user_id]['images']+f"|{prompt}")
        seed = tb.ImageCommand(message, prompt, size)
        change_vals = update_db(user_id, change_vals, 'images', db[user_id]['images']+f"|{seed}")

    # Main menu exit button
    elif db[user_id]['free'] and message.text == 'В меню':
        change_vals = update_db(user_id, change_vals, 'sessions_messages')
        change_vals = update_db(user_id, change_vals, 'free')
        bot.send_message(chat_id=user_id, text='Сессия завершена', reply_markup=types.ReplyKeyboardRemove(), parse_mode='html')
        tb.restart(message)

    # Free mode processing
    elif db[user_id]['free']:
        if message.content_type == 'photo':
            photo = base64.b64encode(bot.download_file(bot.get_file(message.photo[-1].file_id).file_path)).decode()
            if message.caption is not None:
                change_vals = update_db(user_id, change_vals, 'sessions_messages',
                                        db[user_id]['sessions_messages']+[{"content": [{"type": "text", "text": message.caption}, {"type": "image_url", "image_url": f"data:image/jpeg;base64,{photo}"}], "role": "user"}])
            else:
                change_vals = update_db(user_id, change_vals, 'sessions_messages',
                                        db[user_id]['sessions_messages']+[{"content": [{"type": "image_url", "image_url": f"data:image/jpeg;base64,{photo}"}], "role": "user"}])
        elif message.content_type == "document":
            file_info = bot.get_file(message.document.file_id)
            try:
                downloaded_file = bot.download_file(file_info.file_path)
                with open("temp_file", "wb") as new_file:
                    new_file.write(downloaded_file)
                if file_info.file_path[-4:] == '.pdf':
                    downloaded_file = pc.pdf_to_text("temp_file")
                else:
                    with open("temp_file", "rb") as new_file:
                        downloaded_file = new_file.read()
                os.remove("temp_file")
            except Exception as e:
                logger.error(f"Failed to download user {user_id} file")
                downloaded_file = "Файл отсутствует"

            if message.caption is not None:
                change_vals = update_db(user_id, change_vals, 'sessions_messages', db[user_id]['sessions_messages']+[{"content": f"{message.caption} |{downloaded_file}| – это содержимое файла", "role": "user"}])
            else:
                change_vals = update_db(user_id, change_vals, 'sessions_messages', db[user_id]['sessions_messages']+[{"content": f"{downloaded_file}", "role": "user"}])
        else:
            change_vals = update_db(user_id, change_vals, 'sessions_messages', db[user_id]['sessions_messages'] + [{"content": message.text, "role": "user"}])
        thr = Thread(target=TokensCancelletionPattern, args=(user_id, tb.FreeCommand, message))
        thr.start(); thr.join()

    # Text processing
    else:
        for i in range(len(db[user_id]['text'])):
            if db[user_id]['text'][i] and not db[user_id]['some']:
                thr=Thread(target=TokensCancelletionPattern, args=(user_id, tb.TextCommands, message, i))
                thr.start()
                change_vals = update_db(user_id, change_vals, 'text')
                thr.join()
            elif db[user_id]['text'][i] and db[user_id]['some']:
                thr=Thread(target=TokensCancelletionPattern, args=(user_id, tb.SomeTextsCommand, message, i))
                thr.start()
                change_vals = update_db(user_id, change_vals, 'text')
                change_vals = update_db(user_id, change_vals, 'some')
                thr.join()
    
    Thread(target=base.insert_or_update_data, args=(user_id, change_vals)).start()

# Time to end tariff check
async def end_check_tariff_time():
    while True:
        global db
        change_vals = {}
        for user_id, data in db.items():
            deltaf = data['datetime_sub'] - datetime.now().replace(microsecond=0)
            if int(deltaf.total_seconds()) <= 0 and (data['basic'] or data['pro'] or data['free_requests']<10):
                change_vals = update_db(user_id, change_vals, 'pro')
                change_vals = update_db(user_id, change_vals, 'basic')
                change_vals = update_db(user_id, change_vals, 'incoming_tokens')
                change_vals = update_db(user_id, change_vals, 'outgoing_tokens')
                change_vals = update_db(user_id, change_vals, 'free_requests')
                change_vals = update_db(user_id, change_vals, 'datetime_sub')
                logger.info(f"User {user_id} subscription deactivated")
                Thread(target=base.insert_or_update_data, args=(user_id, change_vals)).start()
        await asyncio.sleep(10)

def bot_start():
    while True:
        try:
            bot.polling()
        except Exception as e:
            logger.error(f"Polling exception {e}")
        time.sleep(2)

# Bot launch
if __name__ == "__main__":
    Thread(target=bot_start).start()
    asyncio.run(end_check_tariff_time())