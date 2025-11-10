import json
import os
from telebot import TeleBot
from flask import Flask
from threading import Thread

BOT_TOKEN = os.environ.get(8308068186:AAHC-RfwPrNERgzwv7X2NNtatNnJClQWUWw)
ADMIN_ID = 7364995914
DATA_FILE = "videos.json"

bot = TeleBot(BOT_TOKEN)

if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump({}, f)

def load_data():
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(d):
    with open(DATA_FILE, "w") as f:
        json.dump(d, f, indent=2)

@bot.message_handler(commands=['addvideo'])
def addvideo_cmd(message):
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "You are not authorized.")
        return
    parts = message.text.split()
    if len(parts) < 2:
        bot.reply_to(message, "Use: /addvideo <key> (reply to video)", parse_mode="Markdown")
        return
    payload = parts[1].strip()
    if not message.reply_to_message or (not message.reply_to_message.video and not message.reply_to_message.document):
        bot.reply_to(message, "Reply to a video.")
        return
    file_id = message.reply_to_message.video.file_id if message.reply_to_message.video else message.reply_to_message.document.file_id
    data = load_data()
    data[payload] = file_id
    save_data(data)
    link = f"https://t.me/{bot.get_me().username}?start={payload}"
    bot.reply_to(message, f"Video saved!\nKey: {payload}\nLink: {link}", parse_mode="Markdown")

@bot.message_handler(commands=['start'])
def start_handler(message):
    args = message.text.split(maxsplit=1)
    if len(args) == 1:
        bot.send_message(message.chat.id, "Welcome! Get your video link.")
        return
    payload = args[1].strip()
    data = load_data()
    if payload not in data:
        bot.send_message(message.chat.id, "Video not found.")
        return
    bot.send_video(message.chat.id, data[payload], supports_streaming=True, protect_content=True, caption="Your video!")

app = Flask('')
@app.route('/')
def home():
    return "Bot is alive!"

def run():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

keep_alive()
print("Bot running 24/7...")
bot.infinity_polling()
