import telebot, sqlite3, logging, json, time
from BaseSettings.config import config
from BaseSettings.AuxiliaryClasses import keyboards

logger = logging.getLogger(__name__)
bot = telebot.TeleBot(token=config.token1)
key = keyboards()

@bot.message_handler(commands=['start'])
def StartProcessing(message):
    chat_id = str(message.chat.id)
    if chat_id in config.admin_ids:
        name = ["Рассылка", "Промокоды"]
        return bot.send_message(chat_id=chat_id, text="Выберите действия", reply_markup=key.reply_keyboard(name))

def get_text(message):
    text = message.text
    chat_id = message.chat.id
    if text == "Назад":
        name = ["Рассылка", "Промокоды"]
        return bot.send_message(chat_id=chat_id, text="Выберите действия", reply_markup=key.reply_keyboard(name))
    bot.send_message(chat_id, "Хорошо, отправляю, подождите немного")
    ToolBoxBot = telebot.TeleBot(token=config.token2)
    conn = sqlite3.connect('db_data/UsersData.db')
    cursor = conn.cursor()
    cursor.execute(f"SELECT id FROM users_data_table")
    users = cursor.fetchall()
    cnt = 0
    for us in users:
        try:
            ToolBoxBot.send_message(chat_id=us[0], text=text, parse_mode='html')
        except:
            continue
        else:
            cnt+=1
    name = ["Отправить ещё", "Назад"]
    return bot.send_message(message.chat.id, f"{cnt} человек получило рассылку из {len(users)}", reply_markup=key.reply_keyboard(name))

def get_promocode(message):
    promocode = message.text
    config.promocodes["promocodes"].append(promocode)
    with open("promocodes/promocodes.json", 'w') as f:
        json.dump(config.promocodes, f)
    name = config.promocodes["promocodes"]+["➕ Промокод", "Назад"]
    return bot.send_message(chat_id=message.chat.id, text=f"Вот все промокоды", reply_markup=key.reply_keyboard(name))

def delete_promocode(message, promocode):
    config.promocodes["promocodes"].remove(promocode)
    with open("promocodes/promocodes.json", 'w') as f:
        json.dump(config.promocodes, f)
    name = config.promocodes["promocodes"]+["➕ Промокод", "Назад"]
    return bot.send_message(chat_id=message.chat.id, text=f"Вот все промокоды", reply_markup=key.reply_keyboard(name))

@bot.message_handler(content_types=['text'])
def buttons_request(message):
    chat_id = str(message.chat.id)

    if chat_id in config.admin_ids:
        match message.text:
            case "Рассылка" | "Отправить ещё":
                bot.send_message(chat_id, "Введите тект рассылки", reply_markup=key.reply_keyboard(["Назад"]))
                return bot.register_next_step_handler(message, get_text)
            case "Назад":
                name = ["Рассылка", "Промокоды"]
                return bot.send_message(chat_id=chat_id, text="Выберите действия", reply_markup=key.reply_keyboard(name))
            case "Промокоды":
                name = config.promocodes["promocodes"]+["➕ Промокод", "Назад"]
                return bot.send_message(chat_id=chat_id, text=f"Вот все промокоды", reply_markup=key.reply_keyboard(name))
            case "➕ Промокод":
                bot.send_message(chat_id, "Введите промокод")
                return bot.register_next_step_handler(message, get_promocode)
        if message.text in config.promocodes["promocodes"]:
            name = ["Удалить промокод", "Промокоды"]
            bot.send_message(chat_id=chat_id, text="Выберите действия", reply_markup=key.reply_keyboard(name))
            return bot.register_next_step_handler(message, delete_promocode, message.text)

def run_bot():
    try:
        bot.infinity_polling(timeout=60, long_polling_timeout=60)
    except Exception as e:
        logger.error(f"Bot crashed: {e}")
        time.sleep(10)
        run_bot()

# Bot launch
if __name__ == "__main__":
    run_bot()