import sqlite3, pandas as pd
from re import sub
from datetime import datetime
from ast import literal_eval

# Database functions class
class DataBase:
    def __init__(self, db_name: str, table_name: str, titles: dict[str, str]) -> None:
        self.db_name = db_name
        self.table_name = table_name
        self.titles = titles
        self.types = {
                    "INTEGER":   lambda x: int(x),
                    "BOOLEAN":   lambda x: bool(x),
                    "INTEGER[]": lambda x: [int(el) for el in literal_eval(sub(r"{(.*?)}", r"[\1]", x))],
                    "BOOLEAN[]": lambda x: [bool(el) for el in literal_eval(sub(r"{(.*?)}", r"[\1]", x))],
                    "DATETIME":  lambda x: datetime.strptime(x, "%Y-%m-%d %H:%M:%S"), 
                    "CHAR":      lambda x: str(x),
                    "TEXT":      lambda x: str(x)
                    }
    
    # Database creation function
    def create(self) -> None:
        conn = sqlite3.connect(self.db_name); cursor = conn.cursor()
        cursor.execute(f"CREATE TABLE IF NOT EXISTS {self.table_name} ({',\n'.join(f"{key} {value}" for key, value in self.titles.items())})")
        conn.close()
        
    # Function of insert or update data
    def insert_or_update_data(self, record_id: str, values: dict[str, list[bool|int]|bool|int|str]) -> None:
        conn = sqlite3.connect(self.db_name); cursor = conn.cursor()
        
        placeholders = ', '.join(['?'] * (len(self.titles)))
        
        sql = f"REPLACE INTO {self.table_name} ({', '.join(list(self.titles.keys()))}) VALUES ({placeholders})"
        cursor.execute(sql, [record_id] + [ sub(r"\[(.*?)\]", r"{\1}", str(val)) if type(val)==list else val for val in values.values() ])
        
        conn.commit(); conn.close()

    # Function for load data in dictionary
    def load_data_from_db(self) -> dict[str, dict[str, list[bool|int]|bool|int|str]]:
        loaded_data = dict(); conn = sqlite3.connect(self.db_name); cursor = conn.cursor()
        cursor.execute(f"SELECT {', '.join(list(self.titles.keys()))} FROM {self.table_name}")
        rows = cursor.fetchall()
        for row in rows:
            id = row[0]; loaded_data[id] = dict()
            for i, (key, value) in enumerate(list(self.titles.items())[1:], 1):
                loaded_data[id][key] = self.types[value](row[i])
        conn.close()
        return loaded_data

# Database visualization
if __name__ == "__main__":
    base = DataBase(db_name="UsersData.db", table_name="users_data_table", titles={"id": "TEXT PRIMARY KEY", "text": "INTEGER[]", "some": "BOOLEAN",
                        "images": "BOOLEAN", "free" : "BOOLEAN", "basic" : "BOOLEAN",
                        "pro" : "BOOLEAN", "incoming_tokens": "INTEGER", "outgoing_tokens" : "INTEGER",
                        "free_requests" : "INTEGER", "datetime_sub": "DATETIME"})
    base.create(); db = base.load_data_from_db()
    df = pd.DataFrame.from_dict(db, orient='index')
    print(df)