from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os
import asyncio

# Load environment variables from .env file
load_dotenv()

MONGO_HOST = os.getenv('MONGO_HOST')
MONGO_PORT = os.getenv('MONGO_PORT')
MONGO_DB_NAME = os.getenv('MONGO_DB_NAME')
MONGO_USER = os.getenv('MONGO_USER')
MONGO_PASSWORD = os.getenv('MONGO_PASSWORD')
MONGO_SRV = os.getenv('MONGO_SRV')

if MONGO_USER and MONGO_PASSWORD:
    if os.getenv('MONGO_SRV') == 'true':
        MONGO_URI = f"mongodb+srv://{MONGO_USER}:{MONGO_PASSWORD}@{MONGO_HOST}"
    else:
        if MONGO_PORT:
            MONGO_URI = f"mongodb://{MONGO_USER}:{MONGO_PASSWORD}@{MONGO_HOST}:{MONGO_PORT}"
        else:
            MONGO_URI = f"mongodb://{MONGO_USER}:{MONGO_PASSWORD}@{MONGO_HOST}"
else:
    if os.getenv('MONGO_SRV') == 'true':
        MONGO_URI = f"mongodb+srv://{MONGO_HOST}"
    else:
        if MONGO_PORT:
            MONGO_URI = f"mongodb://{MONGO_HOST}:{MONGO_PORT}"
        else:
            MONGO_URI = f"mongodb://{MONGO_HOST}"

client = AsyncIOMotorClient(MONGO_URI)
database = client.get_database(MONGO_DB_NAME)

async def check_connection():
    try:
        # The ping command is cheap and does not require auth.
        await database.command('ping')
        print('Database connection is working fine.')
    except Exception as e:
        print(f"Database connection failed: {e}")

# Schedule the check_connection coroutine
asyncio.create_task(check_connection())

user_collection = database.get_collection('users')
wallet_collection = database.get_collection('wallets')
private_keys_collection = database.get_collection('private_keys')