import json
import urllib3


class BotInstance:
    def __init__(self, url, tg_token, http_pool, last_update_id):
        self.url = url
        self.tg_token = tg_token
        self.http = http_pool
        self.last_update_id = last_update_id


class User:
    def __init__(self, user_id):
        self.user_id = user_id
        self.post_title = None
        self.post_content = None
        self.ready_to_post = False
    
    def reset_post_info(self):
        self.post_title = None
        self.post_content = None
        self.ready_to_post = False
        

def get_updates(bot, method_of_request="getUpdates"):
    """ Recive all updates from tg bot """
    r = bot.http.request("GET", f"{bot.url}{bot.tg_token}/{method_of_request}", fields={"offset": str(bot.last_update_id), "timeout": 100})
    answ_json = json.loads(r.data.decode('utf-8'))
    return r.status, answ_json


def return_message_content(bot, result_from_tg_response):
    """ Get needed info from tg json reponse to handle the response"""
    bot.last_update_id = int(result_from_tg_response["update_id"])+1
    message_id = result_from_tg_response["message"]["message_id"]
    chat_id = result_from_tg_response["message"]["chat"]["id"]
    if result_from_tg_response["message"].get('text') != None:
        text_of_message = result_from_tg_response["message"]["text"]
    else:
        text_of_message = "Please send only text or smile"
    return message_id, chat_id, text_of_message 


def _start_or_unknown_command(chat_id, text, reply_to_message_id, bot, method_of_response):
    """ Send answer to /start or /help command """
    r = bot.http.request("GET", 
                            f"{bot.url}{bot.tg_token}/{method_of_response}", 
                            fields={"chat_id": chat_id, "text": text, "reply_to_message_id": reply_to_message_id})
    print(f'{r.status} start_or_unknown_command succeful')


def _create_post_command_steps(user, bot, method_of_response):
    while user.ready_to_post == False:
        response_status, answ_json = get_updates(bot)
        print(f"Status of connection {response_status}")
        if answ_json["result"]:
                for message in answ_json["result"]:
                    message_id, chat_id, text_of_message = return_message_content(bot, message)
                    if user.post_title == None:
                        user.post_title = text_of_message
                        r = bot.http.request("GET", 
                            f"{bot.url}{bot.tg_token}/{method_of_response}", 
                            fields={"chat_id": chat_id, "text": "Please input content text for your new post", "reply_to_message_id": message_id})
                    elif user.post_content == None:
                        user.post_content = text_of_message
                        r = bot.http.request("GET", 
                            f"{bot.url}{bot.tg_token}/{method_of_response}", 
                            fields={"chat_id": chat_id,
                            "text": f"Please check data for the new post. Type 'ok' to submit creating the post\nPost title: {user.post_title}\nPost content: {user.post_content}", 
                            "reply_to_message_id": message_id})
                    else:
                        if text_of_message in ["ok", "Ok", "OK", "ок", "Ок", "ОК"]:
                            user.ready_to_post = True
                        return user.ready_to_post

    

def _create_post_command(chat_id, text, reply_to_message_id, bot, method_of_response):
    """ Create post on blogcalc site """
    r = bot.http.request("GET", 
                            f"{bot.url}{bot.tg_token}/{method_of_response}", 
                            fields={"chat_id": chat_id, "text": text, "reply_to_message_id": reply_to_message_id})
    user = User(chat_id)
    status_of_command =_create_post_command_steps(user, bot, method_of_response)
    if status_of_command == True:
        myHeaders = urllib3.util.make_headers(basic_auth='pavel:test_password')
        myHeaders['Content-Type'] = 'application/json'
        data = {"title": user.post_title, "content":  user.post_content}
        encoded_data = json.dumps(data).encode('utf-8')
        r_blogcalc = bot.http.request('POST',
                                    'http://127.0.0.1:8000/api/posts',
                                    body=encoded_data,
                                    headers=myHeaders
        )
        r = bot.http.request("GET", 
                            f"{bot.url}{bot.tg_token}/{method_of_response}", 
                            fields={"chat_id": chat_id, "text": "Post created successfully", "reply_to_message_id": reply_to_message_id})
    else:
        r = bot.http.request("GET", 
                            f"{bot.url}{bot.tg_token}/{method_of_response}", 
                            fields={"chat_id": chat_id, "text": "Post not created", "reply_to_message_id": reply_to_message_id})
    user.reset_post_info()
    print(f'{r.status} create_post_command succeful, sending to blogcalc:', (r_blogcalc.status, r_blogcalc.data) if "r_blogcalc" in locals() else 'did not send')


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
        answer_text = "Please input title for your new post"
        _create_post_command(chat_id, answer_text, reply_to_message_id, bot, method_of_response=method_of_response)
    elif text_of_message == "/check_new_comments":
        answer_text = "New comments to your post here"
        _check_new_comments_command(chat_id, answer_text, reply_to_message_id, bot, method_of_response=method_of_response)
    else:
        answer_text = "Unknown command. Please use /start or /help to check all commands"
        _start_or_unknown_command(chat_id, answer_text, reply_to_message_id, bot, method_of_response=method_of_response)