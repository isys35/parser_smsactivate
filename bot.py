import telebot
from config import BOT_TOKEN
from scaner import load_json, save_json
from telebot.apihelper import ApiTelegramException

bot = telebot.TeleBot(BOT_TOKEN)


def send_info(text):
    users = load_json('users_bot.json')
    for update in bot.get_updates():
        if update.message.chat.id not in users:
            users.append(update.message.chat.id)
            save_json(users, 'users_bot.json')
    for user in users:
        try:
            bot.send_message(user, text)
        except ApiTelegramException:
            continue

