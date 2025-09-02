import os
from dotenv import load_dotenv
from tinydb import TinyDB, Query

load_dotenv()

DB_PATH = os.getenv("DB_PATH", "./db.json")

db = TinyDB(DB_PATH)
users_table = db.table("users")
User = Query()
