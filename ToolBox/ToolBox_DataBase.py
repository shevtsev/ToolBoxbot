import sqlite3

#Класс базы данных
class DataBase:
    def __init__(self) -> None:
        self.conn = sqlite3.connect('UsersData.db')
        self.cursor = self.conn.cursor()
    
    #Создание базы данных
    def create(self) -> None:
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS users_data_table
                          (id TEXT PRIMARY KEY,
                           comm BOOLEAN,
                           smm BOOLEAN,
                           brainst BOOLEAN,
                           advertising BOOLEAN,
                           headlines BOOLEAN,
                           seo BOOLEAN,
                           email BOOLEAN,
                           images BOOLEAN,
                           common BOOLEAN,
                           subscribe BOOLEAN,
                           tokens INTEGER)''')
        self.conn.close()
        
    #Функция для вставки или обновления данных в базе
    def insert_or_update_data(self, record_id: str, values: dict[str, list[bool]|bool|int]) -> None:
        conn = sqlite3.connect('UsersData.db')
        cursor = conn.cursor()

        text_values = values['text']
        images = values['images']
        free = values['free']
        subscribe = values['subscribe']
        tokens = values['tokens']
        
        placeholders = ', '.join(['?'] * (len(text_values) + 4))  # Для text_values + images, free, subscribe, tokens
        update_query = f"REPLACE INTO users_data_table (id, comm, smm, brainst, advertising, headlines, seo, email, images, common, subscribe, tokens) VALUES (?, {placeholders})"
        cursor.execute(update_query, [record_id] + text_values + [images, free, subscribe, tokens])
        
        conn.commit()
        conn.close()


    #Функция обновления массива
    def load_data_from_db(self) -> dict[str, dict[str, list[bool]|bool|int]]:
        loaded_data = {}
        conn = sqlite3.connect('UsersData.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id, comm, smm, brainst, advertising, headlines, seo, email, images, common, subscribe, tokens FROM users_data_table")
        rows = cursor.fetchall()
        for row in rows:
            record_id = row[0]
            values_list = [bool(col) for col in row[1:8]]
            loaded_data[record_id] = {'text': values_list,
                                      'images': row[8],
                                      'free': row[9],
                                      'subscribe': row[10],
                                      'tokens': int(row[11])
                                      }
        conn.close()
        return loaded_data

if __name__ == "__main__":
    base = DataBase()
    base.create()
    db = base.load_data_from_db()
    print(db)