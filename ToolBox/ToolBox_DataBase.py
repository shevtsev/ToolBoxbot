import sqlite3, json, logging
from re import sub
from datetime import datetime
from dateutil.relativedelta import relativedelta
from ast import literal_eval

logging.basicConfig(filename='out.log', level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Database functions class
class DataBase:
    def __init__(self, db_name: str, table_name: str, titles: dict[str, str]) -> None:
        self.db_name = db_name
        self.table_name = table_name
        self.titles = titles
        self.types = {
                    "INTEGER":   lambda x: int(x),
                    "BOOLEAN":   lambda x: bool(x),
                    "CHAR":      lambda x: str(x),
                    "TEXT":      lambda x: str(x),
                    "DATETIME":  lambda x: datetime.strptime(x, "%Y-%m-%d %H:%M:%S"),
                    "INTEGER[]": lambda x: [int(el) for el in literal_eval(sub(r"{(.*?)}", r"[\1]", x))],
                    "BOOLEAN[]": lambda x: [bool(el) for el in literal_eval(sub(r"{(.*?)}", r"[\1]", x))],
                    "TEXT[]":    lambda x: [json.loads(el) for el in literal_eval(sub(r"^{(.*?)}$", r"[\1]", x))]
                    }
    
    # Database creation function
    def create(self) -> None:
        conn = sqlite3.connect(self.db_name); cursor = conn.cursor()
        cursor.execute(f"CREATE TABLE IF NOT EXISTS {self.table_name} ({',\n'.join(f"{key} {value}" for key, value in self.titles.items())})")
        conn.close()
        
    # Function of insert or update data
    def insert_or_update_data(self, record_id: str, values: dict[str, list[bool|int]|bool|int|str]) -> None:
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        # Check if the record exists
        cursor.execute(f"SELECT 1 FROM {self.table_name} WHERE id = ?", (record_id,))
        exists = cursor.fetchone() is not None

        if exists:
            # Update the existing record
            set_clause = ', '.join([f"{key} = ?" for key in values.keys() if key != 'id'])
            try:
                sql = f"UPDATE {self.table_name} SET {set_clause} WHERE id = ?"
                data = [sub(r"^\[(.*?)\]$", r'{\1}', str([json.dumps(el) if isinstance(el, dict) else int(el) for el in val])) if isinstance(val, list) else val for val in values.values()]
                cursor.execute(sql, data + [record_id])
            except:
                logger.error(f"User {record_id} data update error")
            if 'sessions_messages' in list(values.keys()):
                data[list(values.keys()).index('sessions_messages')] = data[list(values.keys()).index('sessions_messages')][:15]
            logger.info(f"Updated user with record id: {record_id}, updated keys: {list(values.keys())}, updated data: {data}")
        else:
            # Insert a new record
            placeholders = ', '.join(['?'] * len(self.titles))
            sql = f"INSERT INTO {self.table_name} ({', '.join(self.titles.keys())}) VALUES ({placeholders})"
            cursor.execute(sql, [record_id] + [sub(r"^\[(.*?)\]$", r'{\1}', str([json.dumps(el) if isinstance(el, dict) else int(el) for el in val])) if isinstance(val, list) else val for val in values.values()])
            logger.info(f"User {record_id} was added to database")
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
        logger.info(f"Data from {self.db_name} was loaded")
        conn.close()
        return loaded_data

# Users data update
if __name__ == "__main__":
    base = DataBase(db_name="UsersData.db", table_name="users_data_table", titles={"id": "TEXT PRIMARY KEY", "text": "INTEGER[]",
                        "sessions_messages": "TEXT[]", "some": "BOOLEAN",
                        "images": "CHAR", "free" : "BOOLEAN", "basic" : "BOOLEAN",
                        "pro" : "BOOLEAN", "incoming_tokens": "INTEGER", "outgoing_tokens" : "INTEGER",
                        "free_requests" : "INTEGER", "datetime_sub": "DATETIME", "promocode": "TEXT", "ref": "TEXT"})
    base.create(); db = base.load_data_from_db(); N = 12
    uid = input()
    if uid != '':
        if "pro" in uid:
            db[uid.split()[0]] = {"text": [0]*N, "sessions_messages": [], "some": False, "images": "0", "free": False, "basic": True, "pro": True, "incoming_tokens": 1.7*10**5, "outgoing_tokens": 5*10**5, "free_requests": 10, "datetime_sub": datetime.now().replace(microsecond=0)+relativedelta(months=1), "promocode": "", "ref": ""}
        elif 'admin' in uid:
            db[uid.split()[0]] = {"text": [0]*N, "sessions_messages": [], "some": False, "images": "0", "free": False, "basic": True, "pro": True, "incoming_tokens": 100*10**5, "outgoing_tokens": 100*10**5, "free_requests": 1000, "datetime_sub": datetime.now().replace(microsecond=0)+relativedelta(years=5), "promocode": "", "ref": ""}
        else:
            db[uid] = {"text": [0]*N, "sessions_messages": [], "some": False, "images": "0", "free": False, "basic": False, "pro": False, "incoming_tokens": 0, "outgoing_tokens": 0, "free_requests": 10, "datetime_sub": datetime.now().replace(microsecond=0)+relativedelta(days=1), "promocode": "", "ref": ""}
        base.insert_or_update_data(uid.split()[0], db[uid.split()[0]])