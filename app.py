import urllib3
from settings import TG_API_TOKEN, BASE_URL_TG_API, DB_NAME
from services import get_updates, return_message_content,\
                     command_handler, BotInstance, User

url = BASE_URL_TG_API
tg_token = TG_API_TOKEN
last_update_id = None



tg_bot = BotInstance(url, tg_token, urllib3.PoolManager(), None, DB_NAME)

while True:
    response_status, answ_json = get_updates(tg_bot)
    print(f"Status of connection {response_status}")
    if answ_json["result"]:
        try:
            for message in answ_json["result"]:
                message_id, chat_id, text_of_message = return_message_content(tg_bot, message)
                user = User(chat_id)
                command_handler(tg_bot, user, text_of_message, message_id)
        except KeyError:
            print(KeyError)

