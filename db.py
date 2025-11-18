import os
from pymongo import MongoClient
from .utilities import logging

mongo_client = None
db = None

def connect_mongo():
   global mongo_client,db
   mongo_client = MongoClient(os.getenv("MONGO_URI"))
   db = mongo_client[os.getenv("DB_NAME","default")]
   logging.info("db connected")

def is_connected():
    try:
        mongo_client.admin.command("ping")
        return True
    except Exception:
        return False

def get_db():
    global mongo_client, db
    if mongo_client is None or not is_connected():
        logging.info("reconnecting to db")
        connect_mongo()

    return db
