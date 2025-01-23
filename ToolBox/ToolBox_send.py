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
        msg = bot.send_message(chat_id=us[0], text="Купите любую подписку на ToolBox и получите дополнительный месяц бесплатно!\n\nУ нас самые низкие цены на подписки:\n\n⭐ безлимит на генерацию текста — 60 рублей в месяц;\n⭐ безлимит на генерацию текста и изображений — 100 рублей в месяц;", parse_mode='html')
    except:
        print(us[0], "no")
    else:
        cnt+=1
        print(us[0], "yes")
print(cnt)