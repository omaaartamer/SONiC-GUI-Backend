import motor.motor_asyncio
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB = os.getenv("MONGO_DB")

client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI) # Connect to MongoDB
db = client[MONGO_DB] # type: ignore # Select the specific database you want

users = db["users"] # Getting the users collection
otps = db["otps"]


