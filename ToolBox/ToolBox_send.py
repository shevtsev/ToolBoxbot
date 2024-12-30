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
        bot.send_message(chat_id=us[0], text="🎅 Хо-хо-хо, Дед Мороз принёс вам подарок! Промокод NEWYEAR даст вам бесплатный месяц безлимита на нейросети для генерации текста и изображений. \n\nПросто введите его во вкладке Тарифы → Промокод 🎁\n\nС наступающим Новым годом!\n\nДля пользователей с промокодом (отправить 30 декабря): \n\nДед Мороз теперь работает на нас! И дарит вам 75% скидку на все подписки! Просто заходите во вкладку Тарифы и успевайте подарить себе подарок на Новый год!\n\nНо долго держать Деда мы не можем — акция продлится до 8 января будущего года ⌛", parse_mode='html')
    except:
        print(us[0], "no")
    else:
        cnt+=1
        print(us[0], "yes")
print(cnt)