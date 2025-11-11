from flask import Flask
import telebot
import json
import threading
import os

# আপনার টোকেন + ইউজারনেম
BOT_TOKEN = "8308068186:AAHC-RfwPrNERgzwv7X2NNtatNnJClQWUWw"
BOT_USERNAME = "MS_Tube_Bot"  # আপনার সঠিক ইউজারনেম (@ ছাড়া)

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

DATA_FILE = "data.json"

# ডেটা লোড/সেভ
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f)

data = load_data()

# /addvideo কমান্ড
@bot.message_handler(commands=['addvideo'])
def handle_addvideo(message):
    # শুধু আপনি (7364995914) ব্যবহার করতে পারবেন
    if message.from_user.id != 7364995914:
        bot.reply_to(message, "You are not authorized.")
        return
    
    if not message.reply_to_message or not (message.reply_to_message.video or message.reply_to_message.document):
        bot.reply_to(message, "Please reply to a video with /addvideo <key>")
        return
    
    try:
        payload = message.text.split(maxsplit=1)[1] if len(message.text.split()) > 1 else "default"
        file_id = (
            message.reply_to_message.video.file_id 
            if message.reply_to_message.video 
            else message.reply_to_message.document.file_id
        )
        data[payload] = file_id
        save_data(data)
        
        link = f"https://t.me/{BOT_USERNAME}?start={payload}"
        bot.reply_to(message, 
            f"Video saved!\n"
            f"Key: `{payload}`\n"
            f"Link: {link}", 
            parse_mode="Markdown")
    except Exception as e:
        bot.reply_to(message, f"Error: {str(e)}")

# /start কমান্ড
@bot.message_handler(commands=['start'])
def handle_start(message):
    try:
        args = message.text.split()
        if len(args) > 1:
            payload = args[1]
            if payload in data:
                bot.send_video(
                    message.chat.id,
                    data[payload],
                    supports_streaming=True,
                    protect_content=True,
                    caption="Here's your video!"
                )
                return
        bot.send_message(message.chat.id, 
            "Welcome to MS Tube Bot!\n"
            "Share the link to watch videos.\n"
            "Admin: /addvideo <key> (reply to video)")
    except Exception as e:
        bot.send_message(message.chat.id, f"Error: {str(e)}")

# ওয়েব সার্ভার
@app.route('/')
def index():
    return "Bot is alive!"

# বট চালু
def run_bot():
    try:
        bot.infinity_polling()
    except:
        pass

if __name__ == '__main__':
    threading.Thread(target=run_bot, daemon=True).start()
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
