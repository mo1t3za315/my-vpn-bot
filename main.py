import telebot
import requests
import os

# --- تنظیمات اصلی ---
BOT_TOKEN = "8570625605:AAEtaZx0dn-SamESnMPX7EmsWM_6ccU5VHo"
PUBLIC_KEY = "b7a92b4cd1a2ced29e06059c61f624be"
API_URL = "https://vpn-telegram.com/api/v1/key-activate/free-key"
ADMIN_ID = 7937070748  # آیدی خودت

bot = telebot.TeleBot(BOT_TOKEN)

# --- توابع کمکی ---

# ذخیره آیدی کاربران در فایل برای پنل ادمین
def save_user(user_id):
    if not os.path.exists("users.txt"):
        with open("users.txt", "w") as f: pass
    
    with open("users.txt", "r") as f:
        users = f.read().splitlines()
    
    if str(user_id) not in users:
        with open("users.txt", "a") as f:
            f.write(str(user_id) + "\n")

# کیبورد اصلی (دکمه شیشه‌ای)
def main_markup():
    markup = telebot.types.InlineKeyboardMarkup()
    btn = telebot.types.InlineKeyboardButton("🚀 دریافت کانفیگ رایگان", callback_data="get_config")
    markup.add(btn)
    return markup

# --- بخش دستورات کاربر ---

@bot.message_handler(commands=['start'])
def start(message):
    save_user(message.from_user.id)
    welcome_text = (
        f"سلام {message.from_user.first_name} عزیز! ❤️\n\n"
        "به ربات دریافت VPN پرسرعت خوش اومدی.\n"
        "برای دریافت اشتراک رایگان (5 گیگابایت) روی دکمه زیر کلیک کن 👇"
    )
    bot.send_message(message.chat.id, welcome_text, reply_markup=main_markup())

# مدیریت کلیک روی دکمه دریافت کانفیگ
@bot.callback_query_handler(func=lambda call: call.data == "get_config")
def callback_config(call):
    bot.answer_callback_query(call.id, "در حال استخراج لینک... ⚡")
    
    payload = {
        "public_key": PUBLIC_KEY,
        "user_tg_id": call.from_user.id
    }
    
    try:
        response = requests.post(API_URL, json=payload)
        res_data = response.json()
        
        if res_data.get("result") == True:
            data = res_data["data"]
            # حذف فاصله‌های احتمالی از ابتدا و انتهای لینک
            clean_link = data['config_url'].strip()
            
            # چیدمان پیام به شکلی که لینک در یک خط کاملاً مجزا و بدون کاراکتر اضافه باشد
            text = (
                "🎁 **اشتراک شما با موفقیت ساخته شد**\n\n"
                "برای کپی کردن، روی لینک زیر بزنید:\n\n"
                f"`{clean_link}`\n\n"
                f"📊 حجم: {data['traffic_limit_gb']} GB\n"
                "━━━━━━━━━━━━━━\n"
                "⚠️ لینک کپی شده را در اپلیکیشن V2Ray وارد کنید."
            )
            bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode="Markdown")
        else:
            bot.send_message(call.message.chat.id, "❌ خطا: سهمیه شما تمام شده یا سرور اجازه نمی‌دهد.")
            
    except Exception as e:
        bot.send_message(call.message.chat.id, "📡 خطا در اتصال! مطمئن شو فیلترشکن بات روشنه.")

# --- بخش پنل ادمین ---

@bot.message_handler(commands=['admin'])
def admin_panel(message):
    if message.from_user.id == ADMIN_ID:
        markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("📊 آمار کاربران", "📢 ارسال پیام همگانی")
        bot.send_message(message.chat.id, "خوش اومدی رئیس! دستور رو انتخاب کن:", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == "📊 آمار کاربران")
def user_stats(message):
    if message.from_user.id == ADMIN_ID:
        if os.path.exists("users.txt"):
            with open("users.txt", "r") as f:
                users = f.readlines()
            bot.send_message(message.chat.id, f"👥 تعداد کل کاربران: {len(users)}")
        else:
            bot.send_message(message.chat.id, "هنوز کاربری ثبت نشده.")

@bot.message_handler(func=lambda m: m.text == "📢 ارسال پیام همگانی")
def broadcast_step1(message):
    if message.from_user.id == ADMIN_ID:
        msg = bot.send_message(message.chat.id, "متن پیامت رو بفرست (یا برای لغو بنویس 'انصراف'):")
        bot.register_next_step_handler(msg, broadcast_step2)

def broadcast_step2(message):
    if message.text == "انصراف": return
    if os.path.exists("users.txt"):
        with open("users.txt", "r") as f:
            users = f.read().splitlines()
        
        count = 0
        for user in users:
            try:
                bot.send_message(user, message.text)
                count += 1
            except: pass
        bot.send_message(ADMIN_ID, f"✅ پیام به {count} نفر ارسال شد.")

# شروع به کار بات
print("Bot is running... 🚀")
bot.infinity_polling()
