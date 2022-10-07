import json

class BotInstance:
    def __init__(self, url, tg_token, http_pool):
        self.url = url
        self.tg_token = tg_token
        self.http = http_pool


def get_updates(bot, last_update_id = None, method_of_request="getUpdates"):
    """ Recive all updates from tg bot """
    r = bot.http.request("GET", f"{bot.url}{bot.tg_token}/{method_of_request}", fields={"offset": str(last_update_id), "timeout": 100})
    answ_json = json.loads(r.data.decode('utf-8'))
    return r.status, answ_json


def return_message_content(result_from_tg_response):
    """ Get needed info from tg json reponse to handle the response"""
    last_update_id = int(result_from_tg_response["update_id"])+1
    message_id = result_from_tg_response["message"]["message_id"]
    chat_id = result_from_tg_response["message"]["chat"]["id"]
    if result_from_tg_response["message"].get('text') != None:
        text_of_message = result_from_tg_response["message"]["text"]
    else:
        text_of_message = "Please send only text or smile"
    return last_update_id, message_id, chat_id, text_of_message 


def _start_or_unknown_command(chat_id, text, reply_to_message_id, bot, method_of_response):
    """ Send answer to /start or /help command """
    r = bot.http.request("GET", 
                            f"{bot.url}{bot.tg_token}/{method_of_response}", 
                            fields={"chat_id": chat_id, "text": text, "reply_to_message_id": reply_to_message_id})
    print(f'{r.status} start_or_unknown_command succeful')


def _create_post_command(chat_id, text, reply_to_message_id, bot, method_of_response):
    r = bot.http.request("GET", 
                            f"{bot.url}{bot.tg_token}/{method_of_response}", 
                            fields={"chat_id": chat_id, "text": text, "reply_to_message_id": reply_to_message_id})
    print(f'{r.status} create_post_command succeful')


def _check_new_comments_command(chat_id, text, reply_to_message_id, bot, method_of_response):
    r = bot.http.request("GET", 
                            f"{bot.url}{bot.tg_token}/{method_of_response}", 
                            fields={"chat_id": chat_id, "text": text, "reply_to_message_id": reply_to_message_id})
    print(f'{r.status} check_new_comments_command succeful')


def command_handler(text_of_message, chat_id, reply_to_message_id, bot, method_of_response="sendMessage"):
    if text_of_message in ["/start", "/help"]:
        answer_text = 'Available commands:\
        \n/start, /help - show help note\
        \n/create_post - start process for creating new post. Ask to input title, content for new post, check them after input and confirm sending\
        \n/check_new_comments  - send titles of blogposts with new comments or "no new comments" '
        _start_or_unknown_command(chat_id, answer_text, reply_to_message_id, bot, method_of_response=method_of_response)
    elif text_of_message == "/create_post":
        answer_text = "Start creating post process"
        _create_post_command(chat_id, answer_text, reply_to_message_id, bot, method_of_response=method_of_response)
    elif text_of_message == "/check_new_comments":
        answer_text = "New comments to your post here"
        _check_new_comments_command(chat_id, answer_text, reply_to_message_id, bot, method_of_response=method_of_response)
    else:
        answer_text = "Unknown command. Please use /start or /help to check all commands"
        _start_or_unknown_command(chat_id, answer_text, reply_to_message_id, bot, method_of_response=method_of_response)