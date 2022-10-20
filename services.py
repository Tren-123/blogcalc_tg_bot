import json
import urllib3
from database import get_username_and_password_from_db, insert_or_update_db
from settings import DB_NAME


class BotInstance:
    def __init__(self, url, tg_token, http_pool, last_update_id, name_of_db):
        self.url = url
        self.tg_token = tg_token
        self.http = http_pool
        self.last_update_id = last_update_id
        self.name_of_db = name_of_db


class User:
    def __init__(self, user_id):
        self.user_id = user_id
        self.post_title = None
        self.post_content = None
        self.username = None
        self.password = None
        self.credentials_exist = False
        self.ready_to_post = False
    
    def reset_post_info(self):
        self.post_title = None
        self.post_content = None
        self.ready_to_post = False

    def reset_credentials_info(self):
        self.username = None
        self.password = None
        self.credentials_exist = False

    def display_vars(self):
        print(
            f"user_id: {self.user_id},\npost_title: {self.post_title},\
            \npost_content: {self.post_content},\nusername: {self.username},\
            \npassword: {self.password},\ncredentials_exist: {self.credentials_exist},\nready_to_post: {self.ready_to_post}"
            )
        

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


def ask_credentials(bot, user, method_of_response="sendMessage"):
    """ Ask user his credential for blogcalc website """
    bot.http.request("GET", 
                            f"{bot.url}{bot.tg_token}/{method_of_response}", 
                            fields={"chat_id": user.user_id, "text": "Please input your username for blogcalc website"})
    while user.credentials_exist == False:
        response_status, answ_json = get_updates(bot)
        print(f"Status of connection {response_status}")
        if answ_json["result"]:
                for message in answ_json["result"]:
                    message_id, chat_id, text_of_message = return_message_content(bot, message)
                    if chat_id != user.user_id:
                        continue
                    if user.username == None:
                        user.username = text_of_message
                        r = bot.http.request("GET", 
                            f"{bot.url}{bot.tg_token}/{method_of_response}", 
                            fields={"chat_id": user.user_id, "text": "Please input your password for blogcalc website", "reply_to_message_id": message_id})
                    elif user.password == None:
                        user.password = text_of_message
                        r = bot.http.request("GET", 
                            f"{bot.url}{bot.tg_token}/{method_of_response}", 
                            fields={"chat_id": user.user_id,
                            "text": f"Please check username and password. Type 'ok' to submit\nUsername: {user.username}\nPassword: {user.password}", 
                            "reply_to_message_id": message_id})
                    else:
                        if text_of_message in ["ok", "Ok", "OK", "ок", "Ок", "ОК"]:
                            user.credentials_exist = True
                            r = bot.http.request("GET", 
                                f"{bot.url}{bot.tg_token}/{method_of_response}", 
                                fields={"chat_id": user.user_id,
                                "text": f"New credentinals set:\nUsername: {user.username}\nPassword: {user.password}", 
                                "reply_to_message_id": message_id})
                        return user.username, user.password

                            


def user_auth_or_ask_credentials(bot, user):
    """ get username and password of user from db or ask its from user to update db"""
    username, password = get_username_and_password_from_db(bot.name_of_db, user.user_id)
    if (username and password) == False: 
        username, password = ask_credentials(bot, user)
        insert_or_update_db(bot.name_of_db, user.user_id, username, password)
    return username, password


def _start_or_unknown_command(bot, user, text, reply_to_message_id, method_of_response):
    """ Send answer to /start or /help command """
    r = bot.http.request("GET", 
                            f"{bot.url}{bot.tg_token}/{method_of_response}", 
                            fields={"chat_id": user.user_id, "text": text, "reply_to_message_id": reply_to_message_id})
    print(f'{r.status} start_or_unknown_command succeful')


def _create_post_command_steps(bot, user, method_of_response):
    """ Ask user for input post title and post content """
    while user.ready_to_post == False:
        response_status, answ_json = get_updates(bot)
        print(f"Status of connection {response_status}")
        if answ_json["result"]:
                for message in answ_json["result"]:
                    message_id, chat_id, text_of_message = return_message_content(bot, message)
                    if chat_id != user.user_id:
                        continue
                    if user.post_title == None:
                        user.post_title = text_of_message
                        r = bot.http.request("GET", 
                            f"{bot.url}{bot.tg_token}/{method_of_response}", 
                            fields={"chat_id": user.user_id, "text": "Please input content text for your new post", "reply_to_message_id": message_id})
                    elif user.post_content == None:
                        user.post_content = text_of_message
                        r = bot.http.request("GET", 
                            f"{bot.url}{bot.tg_token}/{method_of_response}", 
                            fields={"chat_id": user.user_id,
                            "text": f"Please check data for the new post. Type 'ok' to submit creating the post\nPost title: {user.post_title}\nPost content: {user.post_content}", 
                            "reply_to_message_id": message_id})
                    else:
                        if text_of_message in ["ok", "Ok", "OK", "ок", "Ок", "ОК"]:
                            user.ready_to_post = True
                        return user.ready_to_post

    

def _create_post_command(bot, user, text, reply_to_message_id, method_of_response):
    """ Create post on blogcalc site """
    r = bot.http.request("GET", 
                            f"{bot.url}{bot.tg_token}/{method_of_response}", 
                            fields={"chat_id": user.user_id, "text": text, "reply_to_message_id": reply_to_message_id})
    status_of_command =_create_post_command_steps(bot, user, method_of_response)
    if status_of_command == True:
        username, password = user_auth_or_ask_credentials(bot, user)
        myHeaders = urllib3.util.make_headers(basic_auth=f'{username}:{password}')
        myHeaders['Content-Type'] = 'application/json'
        data = {"title": user.post_title, "content":  user.post_content}
        encoded_data = json.dumps(data).encode('utf-8')
        r_blogcalc = bot.http.request('POST',
                                    'http://127.0.0.1:8000/api/posts',
                                    body=encoded_data,
                                    headers=myHeaders
        )
    if "r_blogcalc" in locals() and str(r_blogcalc.status).startswith("2"):
        r = bot.http.request("GET", 
                            f"{bot.url}{bot.tg_token}/{method_of_response}", 
                            fields={"chat_id": user.user_id, "text": "Post created successfully", "reply_to_message_id": reply_to_message_id})
        print(f'{r.status} create_post_command succeful, sending to blogcalc:', r_blogcalc.status, r_blogcalc.data)
    else:
        r = bot.http.request("GET", 
                            f"{bot.url}{bot.tg_token}/{method_of_response}", 
                            fields={"chat_id": user.user_id, "text": "Post not created. If this result unexpect for you - use /my_credentials command to set correct credentials", 
                            "reply_to_message_id": reply_to_message_id})
        print(f'{r.status} create_post_command succeful, sending to blogcalc: did not send')
    
    user.reset_credentials_info()
    user.reset_post_info()


def _check_new_comments_command(bot, user, text, reply_to_message_id, method_of_response):
    """ Check new comments. NOT FINISHED """
    r = bot.http.request("GET", 
                            f"{bot.url}{bot.tg_token}/{method_of_response}", 
                            fields={"chat_id": user.user_id, "text": text, "reply_to_message_id": reply_to_message_id})
    print(f'{r.status} check_new_comments_command succeful')


def command_handler(bot, user, text_of_message, reply_to_message_id, method_of_response="sendMessage"):
    """ Handle commands from user and choose right way to proceed """
    if text_of_message in ["/start", "/help"]:
        answer_text = 'Available commands:\
        \n/start, /help - show help note\
        \n/my_credentials - input your credentials for blogcal website\
        \n/create_post - start process for creating new post. Ask to input title, content for new post, check them after input and confirm sending\
        \n/check_new_comments  - send titles of blogposts with new comments or "no new comments" '
        _start_or_unknown_command(bot, user, answer_text, reply_to_message_id, method_of_response=method_of_response)
    elif text_of_message == "/create_post":
        answer_text = "Please input title for your new post"
        _create_post_command(bot, user, answer_text, reply_to_message_id, method_of_response=method_of_response)
    elif text_of_message == "/check_new_comments":
        answer_text = "New comments to your post here"
        _check_new_comments_command(bot, user, answer_text, reply_to_message_id, method_of_response=method_of_response)
    elif text_of_message == "/my_credentials":
        username, password = ask_credentials(bot, user)
        insert_or_update_db(bot.name_of_db, user.user_id, username, password)
    else:
        answer_text = "Unknown command. Please use /start or /help to check all commands"
        _start_or_unknown_command(bot, user, answer_text, reply_to_message_id, method_of_response=method_of_response)