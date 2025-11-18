import os
import requests
from .logger import logging

def send_email(to_mail, subject,message):
	auth = os.getenv('MAIL_API_KEY')
	if auth is None:
		logging.error("mailing auth key is not found")
		return {"response":"error"}
	return requests.post(
  		os.getenv("MAIL_URL"),
  		auth=("api", auth),
  		data={"from": os.getenv("MAIL_FROM"),
			"to": to_mail,
  			"subject": subject,
  			"text": message})

