import telebot
from settings import TG_API_TOKEN
from telebot import types

bot = telebot.TeleBot(TG_API_TOKEN)

"""@bot.message_handler(commands=['start', 'help'])
def start_command(message):
    answ = f"List of comands {'/app', '/start'}"
    bot.send_message(message.chat.id, answ)
"""
user_dict = {}

class User:
    def __init__(self, name):
        self.name = name
        self.post_title = None
        self.post_content = None
        self.confirmation = None

@bot.message_handler(commands=['app'])
def foo(message):
    bot.send_message(message.chat.id, "Hey it is n1")
    bot.send_message(message.chat.id, "And it is n2")


# Handle '/start' and '/help'
@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
    msg = bot.reply_to(message, """\
Please insert your username in the blogcalc app
""")
    bot.register_next_step_handler(msg, process_username_step)


def process_username_step(message):
    try:
        chat_id = message.chat.id
        username = message.text
        user = User(username)
        user_dict[chat_id] = user
        msg = bot.reply_to(message, f'Please insert title of new blog post by {username} for blogcalc app')
        bot.register_next_step_handler(msg, process_post_title_step)
    except Exception as e:
        msg = bot.reply_to(message, 'Something goes wrong. Please try again')
        bot.register_next_step_handler(msg, process_username_step)
        return

def process_post_title_step(message):
    try:
        chat_id = message.chat.id
        post_title = message.text
        user = user_dict[chat_id]
        user.post_title = post_title
        msg = bot.reply_to(message, f'Please insert content for new blog post {post_title} by {user.name} for blogcalc app')
        bot.register_next_step_handler(msg, process_post_content_step)
    except Exception as e:
        msg = bot.reply_to(message, 'Something goes wrong. Please try again')
        bot.register_next_step_handler(msg, process_post_title_step)
        return

def process_post_content_step(message):
    try:
        chat_id = message.chat.id
        post_content = message.text
        user = user_dict[chat_id]
        user.post_content = post_content
        msg = bot.reply_to(message, f'Please check inserted data for new post\n\
Username: {user.name}\nPost title: {user.post_title}\nPost content: {user.post_content}')
        bot.send_message(chat_id, "Please type any symbols if you are checked post and ready to the next step")
        bot.register_next_step_handler(msg, process_confirm_step)
    except Exception as e:
        msg = bot.reply_to(message, 'Something goes wrong. Please try again')
        bot.register_next_step_handler(msg, process_post_content_step)
        return

def process_confirm_step(message):
    try:
        chat_id = message.chat.id
        user = user_dict[chat_id]
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        markup.add('Publish the post', 'Decline')
        msg = bot.send_message(chat_id, "", reply_markup=markup)
        bot.register_next_step_handler(msg, process_final_step)
    except Exception as e:
        bot.reply_to(message, '1Something goes wrong. Please try again')
        bot.register_next_step_handler(message, process_confirm_step)
        return

def process_final_step(message):
    try:
        chat_id = message.chat.id
        answer = message.text
        user = user_dict[chat_id]
        if answer == u'Confirm':
            user.confirmation = True
            bot.send_message(chat_id, 'Post created succesfuly')
        elif answer == u'Decline':
            user.confirmation = False
            bot.send_message(chat_id, 'Post not created')
        else:
            raise Exception("Unknown asnwer. Post not created")
    except Exception as e:
        bot.reply_to(message, 'Something goes wrong. Please try again')


# Enable saving next step handlers to file "./.handlers-saves/step.save".
# Delay=2 means that after any change in next step handlers (e.g. calling register_next_step_handler())
# saving will hapen after delay 2 seconds.
bot.enable_save_next_step_handlers(delay=2)

# Load next_step_handlers from save file (default "./.handlers-saves/step.save")
# WARNING It will work only if enable_save_next_step_handlers was called!
bot.load_next_step_handlers()

bot.infinity_polling()