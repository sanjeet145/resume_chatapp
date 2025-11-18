from .db import get_db
import os
import time
from .utilities import logging
from .utilities import send_email

def record_user_details(email:str,name="unknown",notes="not provided"):
  logging.info(f"called tool")
  db = get_db()
  collections = db[os.getenv('COLLECTION_NAME',"emails")]
  if email is not None:
    result = collections.find_one({"email":email})
    if result:
       return {"recorded":"already have your record"}
    collections.insert_one({
       "email":email,
       "record_time":time.strftime("%Y-%m-%d %H:%M", time.localtime())
       })
    logging.info("saved to db")
    subject=f"{name} is trying to connect with you"
    message =f"user {name} with email {email} trying to connect with you. And here is the full message :- {notes}"
    result = send_email(os.getenv("TO_MAIL"),subject,message)
    logging.info(f"email sent {result.ok}")
  return {"recorded":"ok"}


record_user_details_json = {
    "name": "record_user_details",
    "description": "Use this tool to record that a user is interested in being in touch and provided an email address",
    "parameters": {
        "type": "object",
        "properties": {
            "email": {
                "type": "string",
                "description": "The email address of this user"
            },
            "name": {
                "type": "string",
                "description": "The user's name, if they provided it"
            }
            ,
            "notes": {
                "type": "string",
                "description": "Any additional information about the conversation that's worth recording to give context"
            }
        },
        "required": ["email"],
        "additionalProperties": False
    }
}

