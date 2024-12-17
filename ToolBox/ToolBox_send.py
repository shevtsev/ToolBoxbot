import telebot, sqlite3, os
from dotenv import load_dotenv
load_dotenv()
bot = telebot.TeleBot(token=os.environ['TOKEN'])
conn = sqlite3.connect('UsersData.db')
cursor = conn.cursor()
cursor.execute(f"SELECT id FROM users_data_table WHERE promocode != 1")
users = cursor.fetchall()
for us in users:
    try:
        bot.send_message(chat_id=us[0], text="Успейте воспользоваться промокодом FREE24 до 21 декабря!\n\nПо нему вы получите бесплатный месяц тарифа PRO — это безлимит на генерацию текста и изображений 💥 \n\nЧтобы ввести промокод, перейдите на вкладку Тарифы и нажмите кнопку «Промокод».", parse_mode='html')
    except:
        print(us[0], "no")
    else:
        print(us[0], "yes")