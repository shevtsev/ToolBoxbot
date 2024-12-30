import telebot, sqlite3, os
from dotenv import load_dotenv
load_dotenv()
bot = telebot.TeleBot(token=os.environ['TOKEN'])
conn = sqlite3.connect('UsersData.db')
cursor = conn.cursor()
cursor.execute(f"SELECT id FROM users_data_table WHERE pro != 1")
users = cursor.fetchall()
cnt = 0
for us in users:
    try:
        msg = bot.send_message(chat_id=us[0], text="message", parse_mode='html')
        bot.delete_message(us[0], msg.message_id -1)
        bot.delete_message(us[0], msg.message_id)
    except:
        print(us[0], "no")
    else:
        cnt+=1
        print(us[0], "yes")
print(cnt)