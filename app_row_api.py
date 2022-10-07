import urllib3
import json
from settings import TG_API_TOKEN, BASE_URL_TG_API
from services import get_updates, return_message_content,\
                     text_handler, BotInstance

url = BASE_URL_TG_API
tg_token = TG_API_TOKEN
last_update_id = None



tg_bot = BotInstance(url, tg_token, urllib3.PoolManager())


while True:
    response_status, answ_json = get_updates(tg_bot, last_update_id)
    print(f"Status of connection {response_status}")
    if answ_json["result"]:
        try:
            for message in answ_json["result"]:
                last_update_id, message_id, chat_id, text_of_message = return_message_content(message)
                text_handler(text_of_message, chat_id, message_id, tg_bot)
        except KeyError:
            print(KeyError)

