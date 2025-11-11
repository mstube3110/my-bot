import os
from flask import Flask
import telebot
import json
import threading

BOT_TOKEN = "8308068186:AAHC-RfwPrNERgzwv7X2NNtatNnJClQWUWw"
bot = telebot.TeleBot(BOT_TOKEN)

app = Flask(__name__)

DATA_FILE = "data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f)

data = load_data()

@bot.message_handler(commands=['addvideo'])
def handle_addvideo(message):
    if not message.reply_to_message:
        bot.reply_to(message, "You are not authorized.")
        return
    if not (message.reply_to_message.video or message.reply_to_message.document):
        bot.reply_to(message, "Please reply to a video or document.")
        return
    try:
        payload = message.text.split()[1] if len(message.text.split()) > 1 else "default"
        file_id = (
            message.reply_to_message.video.file_id if message.reply_to_message.video else
            message.reply_to_message.document.file_id if message.reply_to_message.document else None
        )
        if not file_id:
            bot.reply_to(message, "No video or file found.")
            return
        data[payload] = file_id
        save_data(data)
        link = f"https://t.me/{bot.get_me().username}?start={payload}"
        bot.reply_to(message, f"Video saved!\nLink: {link}", parse_mode="Markdown")
    except Exception as e:
        bot.reply_to(message, f"Error: {str(e)}")

@bot.message_handler(commands=['start'])
def handle_start(message):
    try:
        payload = message.text.split()[1] if len(message.text.split()) > 1 else None
        if payload and payload in data:
            bot.send_video(
                message.chat.id,
                data[payload],
                supports_streaming=True,
                protect_content=True,
                caption="Your video!"
            )
        else:
            bot.send_message(message.chat.id, "Video not found.")
    except Exception as e:
        bot.send_message(message.chat.id, f"Error: {str(e)}")

@app.route('/')
def index():
    return "Bot is alive!"

def run_bot():
    try:
        bot.infinity_polling()
    except:
        pass

if __name__ == '__main__':
    threading.Thread(target=run_bot, daemon=True).start()
    port = int(os.environ.get("PORT", 8000))
    app.run(host='0.0.0.0', port=port)
