import telebot
import requests
import os

# اطلاعات اصلی
BOT_TOKEN = '8570625605:AAG2y-8wtDuYv0AS4Egb6j_fx6rhCyVwiO0'
ADMIN_ID = 7937070748
PUBLIC_KEY = "b7a92b4cd1a2ced29e06059c61f624be"

bot = telebot.TeleBot(BOT_TOKEN)
USER_FILE = "users.txt"

# تابع برای ذخیره آیدی کاربرها
def save_user(user_id):
    if not os.path.exists(USER_FILE):
        open(USER_FILE, "w").close()
    
    with open(USER_FILE, "r") as f:
        users = f.read().splitlines()
    
    if str(user_id) not in users:
        with open(USER_FILE, "a") as f:
            f.write(str(user_id) + "\n")

# کیبوردها
def main_markup(user_id):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🚀 دریافت کانفیگ رایگان")
    if user_id == ADMIN_ID:
        markup.add("⚙️ پنل مدیریت")
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    save_user(message.from_user.id) # ذخیره آیدی کاربر جدید
    bot.reply_to(message, "سلام! به ربات خودت خوش اومدی.", reply_markup=main_markup(message.from_user.id))

@bot.message_handler(func=lambda message: message.text == "🚀 دریافت کانفیگ رایگان")
def get_config(message):
    bot.send_message(message.chat.id, "در حال دریافت کانفیگ از سرور...")
    try:
        payload = {"public_key": PUBLIC_KEY, "user_tg_id": message.from_user.id}
        response = requests.post("https://vpn-telegram.com/api/v1/key-activate/free-key", json=payload)
        data = response.json()
        
        if data.get("result"):
            config = data["data"]["config_url"]
            bot.send_message(message.chat.id, f"✅ خدمت شما:\n\n`{config}`", parse_mode="Markdown")
        else:
            bot.send_message(message.chat.id, "❌ خطا: احتمالاً قبلاً دریافت کردید یا ظرفیت پره.")
    except:
        bot.send_message(message.chat.id, "⚠️ خطای اتصال به سرور.")

# بخش ادمین
@bot.message_handler(func=lambda message: message.text == "⚙️ پنل مدیریت")
def admin_panel(message):
    if message.from_user.id == ADMIN_ID:
        markup = telebot.types.InlineKeyboardMarkup()
        btn = telebot.types.InlineKeyboardButton("📣 ارسال پیام همگانی", callback_data="broadcast")
        markup.add(btn)
        
        with open(USER_FILE, "r") as f:
            count = len(f.read().splitlines())
            
        bot.send_message(message.chat.id, f"📊 آمار ربات:\nتعداد کل کاربران: {count}", reply_markup=markup)

# هندلر کلیک روی دکمه شیشه‌ای
@bot.callback_query_handler(func=lambda call: call.data == "broadcast")
def ask_broadcast(call):
    msg = bot.send_message(call.message.chat.id, "لطفاً پیامی که می‌خوای به همه ارسال بشه رو بنویس:")
    bot.register_next_step_handler(msg, send_to_all)

def send_to_all(message):
    with open(USER_FILE, "r") as f:
        users = f.read().splitlines()
    
    success = 0
    for user in users:
        try:
            bot.send_message(user, message.text)
            success += 1
        except:
            pass
    
    bot.send_message(ADMIN_ID, f"✅ پیام شما با موفقیت به {success} نفر ارسال شد.")

print("ربات با دیتابیس فعال شد...")
bot.infinity_polling()
