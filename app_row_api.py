import urllib3
import json
from settings import TG_API_TOKEN

url = "https://api.telegram.org/bot"
tg_token = TG_API_TOKEN
tg_method = "getUpdates"
tg_method_response = "sendMessage"
last_update_id = None


def get_updates(last_update_id = None, url=url, token=tg_token, method_of_request="getUpdates"):
    r = http.request("GET", f"{url}{token}/{method_of_request}", fields={"offset": str(last_update_id), "timeout": 100})
    answ_json = json.loads(r.data.decode('utf-8'))
    return r.status, answ_json

def return_message_content(result_from_tg_response):
    last_update_id = int(result_from_tg_response["update_id"])+1
    message_id = result_from_tg_response["message"]["message_id"]
    chat_id = result_from_tg_response["message"]["chat"]["id"]
    if result_from_tg_response["message"].get('text') != None:
        text_of_message = result_from_tg_response["message"]["text"]
    else:
        text_of_message = "Please send only text or smile"
    return last_update_id, message_id, chat_id, text_of_message 

def start_or_help_command(chat_id, text, reply_to_message_id, url, token, method_of_response):
    r = http.request("GET", 
                            f"{url}{token}/{method_of_response}", 
                            fields={"chat_id": chat_id, "text": text, "reply_to_message_id": reply_to_message_id})
    print(f'{r.status} start_or_help_command succeful')

def create_post_command(chat_id, text, reply_to_message_id, url, token, method_of_response):
    r = http.request("GET", 
                            f"{url}{token}/{method_of_response}", 
                            fields={"chat_id": chat_id, "text": text, "reply_to_message_id": reply_to_message_id})
    print(f'{r.status} create_post_command succeful')

def check_new_comments_command(chat_id, text, reply_to_message_id, url, token, method_of_response):
    r = http.request("GET", 
                            f"{url}{token}/{method_of_response}", 
                            fields={"chat_id": chat_id, "text": text, "reply_to_message_id": reply_to_message_id})
    print(f'{r.status} check_new_comments_command succeful')

def unknown_command(chat_id, text, reply_to_message_id, url, token, method_of_response):
    r = http.request("GET", 
                            f"{url}{token}/{method_of_response}", 
                            fields={"chat_id": chat_id, "text": text, "reply_to_message_id": reply_to_message_id})
    print(f'{r.status} unknown_command succeful')

def text_handler(text_of_message, chat_id, reply_to_message_id, url=url, token=tg_token, method_of_response="sendMessage"):
    if text_of_message in ["/start", "/help"]:
        answer_text = 'Available commands:\
        \n/start, /help - show help note\
        \n/create_post - start process for creating new post. Ask to input title, content for new post, check them after input and confirm sending\
        \n/check_new_comments  - send titles of blogposts with new comments or "no new comments" '
        start_or_help_command(chat_id, answer_text, reply_to_message_id, url=url, token=token, method_of_response=method_of_response)
    elif text_of_message == "/create_post":
        answer_text = "Start creating post process"
        create_post_command(chat_id, answer_text, reply_to_message_id, url=url, token=token, method_of_response=method_of_response)
    elif text_of_message == "/check_new_comments":
        answer_text = "New comments to your post here"
        check_new_comments_command(chat_id, answer_text, reply_to_message_id, url=url, token=token, method_of_response=method_of_response)
    else:
        answer_text = "Unknown command. Please use /start or /help to check all commands"
        unknown_command(chat_id, answer_text, reply_to_message_id, url=url, token=token, method_of_response=method_of_response)

http = urllib3.PoolManager()
while True:
    response_status, answ_json = get_updates(last_update_id)
    print(f"Status of connection {response_status}")
    if answ_json["result"]:
        try:
            for message in answ_json["result"]:
                last_update_id, message_id, chat_id, text_of_message = return_message_content(message)
                text_handler(text_of_message, chat_id, message_id)
        except KeyError:
            print(KeyError)

