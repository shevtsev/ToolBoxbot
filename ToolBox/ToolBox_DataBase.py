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
                           image BOOLEAN,
                           comm BOOLEAN,
                           smm BOOLEAN,
                           brainst BOOLEAN,
                           advertising BOOLEAN,
                           headlines BOOLEAN,
                           seo BOOLEAN,
                           email BOOLEAN)''')
        self.conn.close()
        
    #Функция для вставки или обновления данных в базе
    def insert_or_update_data(self, record_id: str, values: list) -> None:
        conn = sqlite3.connect('UsersData.db')
        cursor = conn.cursor()
        placeholders = ', '.join(['?'] * len(values))
        update_query = f"REPLACE INTO users_data_table (id, image, comm, smm, brainst, advertising, headlines, seo, email) VALUES (?, {placeholders})"
        cursor.execute(update_query, [record_id] + values)
        conn.commit()
        conn.close()

    #Функция обновления массива
    def load_data_from_db(self) -> dict[str, list[bool]]:
        loaded_data = {}
        conn = sqlite3.connect('UsersData.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id, image, comm, smm, brainst, advertising, headlines, seo, email FROM users_data_table")
        rows = cursor.fetchall()
        for row in rows:
            record_id = row[0]
            values_list = [bool(col) for col in row[1:]]
            loaded_data[record_id] = values_list
        conn.close()
        return loaded_data