import telebot, sqlite3, os
from dotenv import load_dotenv
load_dotenv()
bot = telebot.TeleBot(token=os.environ['TOKEN'])
conn = sqlite3.connect('UsersData.db')
cursor = conn.cursor()
cursor.execute(f"SELECT id FROM users_data_table")
users = cursor.fetchall()
cnt = 0
for us in users:
    try:
        msg = bot.send_message(chat_id=us[0], text="Хотите пользоваться ботом бесплатно? Легко! За каждого приглашённого друга можно получить +10 дней безлимита на генерацию текста и изображений. Ваш друг получит целый месяц такого же тарифа 💰\n\nПросто зайдите во вкладку «Тарифы» → «Реферальная программа» и увидите внизу сообщения свой реферальный код. Отправьте его другу — пусть он введет его во вкладке «Промокод» (раздел «Тарифы») ♥️", parse_mode='html')
    except:
        print(us[0], "no")
    else:
        cnt+=1
        print(us[0], "yes")
print(cnt)