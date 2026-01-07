import telebot
from telebot import types
import json
import os

TOKEN = "8158074203:AAFo0T07IdDOYeOlsrWf1atkjeW2h4AN40k"
bot = telebot.TeleBot(TOKEN)
bot.remove_webhook()

bot_active = False  # Bot boshlanishda o‘chirilgan

GROUP_SCORES_FILE = "group_scores.json"
group_scores = {}  # {chat_id: {user_id: {'score': int, 'name': str}}}

admin_id = 2117076791
score_givers = {admin_id}

# ===== JSON FUNKSIYALARI =====
def load_scores():
    global group_scores
    if os.path.exists(GROUP_SCORES_FILE):
        try:
            with open(GROUP_SCORES_FILE, "r") as f:
                group_scores = json.load(f)
        except:
            group_scores = {}
    else:
        group_scores = {}

def save_scores():
    with open(GROUP_SCORES_FILE, "w") as f:
        json.dump(group_scores, f)

load_scores()

# ===== Reyting funksiyasi =====
def generate_ranking(chat_id):
    if chat_id not in group_scores or not group_scores[chat_id]:
        return "Hali ball qo‘shilmagan."
    filtered = {uid: data for uid, data in group_scores[chat_id].items() if data['score'] > 0}
    if not filtered:
        return "Hali ball qo‘shilmagan."
    ranking = sorted(filtered.items(), key=lambda x: x[1]['score'], reverse=True)
    text = "🏆🎖 Reyting (bu guruh):\n"
    for i, (uid, data) in enumerate(ranking, start=1):
        if i == 1:
            medal = "🥇"
        elif i == 2:
            medal = "🥈"
        elif i == 3:
            medal = "🥉"
        else:
            medal = f"{i}."
        text += f"{medal} {data['name']} — {data['score']} ball\n"
    return text

# ===== Komandalar =====
commands = [
    types.BotCommand("start", "Bot holatini ko‘rsatadi"),
    types.BotCommand("botstart", "Botni yoqish"),
    types.BotCommand("botstop", "Botni o‘chirish"),
    types.BotCommand("reyting", "Reytingni ko‘rsatish"),
    types.BotCommand("setscoregiver", "Yangi ball beruvchi tayinlash"),
    types.BotCommand("setadmin", "Boshqa foydalanuvchini admin qilish"),
    types.BotCommand("clear", "Barcha ballarni 0 ga teng qiladi")
]
bot.set_my_commands(commands)

# ===== /start =====
@bot.message_handler(commands=['start'])
def start(message):
    status = "ishlayapti ✅" if bot_active else "o‘chirilgan ❌"
    # Inline tugma yaratamiz
    markup = types.InlineKeyboardMarkup()
    clear_btn = types.InlineKeyboardButton("🗑 Clear ballar", callback_data="clear_scores")
    markup.add(clear_btn)
    bot.send_message(message.chat.id,
                     f"👋 Salom! Bot holati: {status}\n"
                     "💫 Ball berish/ayirish: +10, -5 yozish kifoya\n"
                     "✍ Foydalanuvchiga reply qilishingiz shart emas\n"
                     "/reyting — Reytingni ko‘rsatish\n"
                     "/setscoregiver — Yangi ball beruvchi tayinlash\n"
                     "/setadmin — Boshqa foydalanuvchini admin qilish\n"
                     "/botstart — Botni yoqish\n"
                     "/botstop — Botni o‘chirish\n"
                     "/clear — Barcha ballarni 0 ga teng qiladi\n"
                     "/help — Barcha buyruqlar ro‘yxati",
                     reply_markup=markup)

# ===== /help =====
@bot.message_handler(commands=['help'])
def show_help(message):
    help_text = (
        "📌 Bot buyruqlari:\n\n"
        "👋 /start — Bot holatini ko‘rsatadi\n"
        "🚀 /botstart — Botni yoqish\n"
        "❌ /botstop — Botni o‘chirish\n"
        "🏆 /reyting — Reytingni ko‘rsatish (har guruh alohida)\n"
        "⭐ /setscoregiver — Yangi ball beruvchi tayinlash (reply qilgan foydalanuvchiga)\n"
        "👑 /setadmin — Boshqa foydalanuvchini admin qilish\n"
        "➕ +10 yoki -5 — Ball qo‘shish/ayirish\n"
        "🗑 /clear — Barcha ballarni 0 ga teng qiladi\n"
        "ℹ /help — Barcha buyruqlar ro‘yxati"
    )
    bot.send_message(message.chat.id, help_text)

# ===== /botstart =====
@bot.message_handler(commands=['botstart'])
def bot_start(message):
    global bot_active
    if message.from_user.id not in score_givers:
        bot.send_message(message.chat.id, "❌ Siz ball beruvchi emassiz.")
        return
    if bot_active:
        bot.send_message(message.chat.id, "✅ Bot allaqachon ishlayapti")
        return
    bot_active = True
    bot.send_message(message.chat.id, "🚀 Bot ishga tushirildi!")

# ===== /botstop =====
@bot.message_handler(commands=['botstop'])
def bot_stop(message):
    global bot_active
    if message.from_user.id not in score_givers:
        bot.send_message(message.chat.id, "❌ Siz ball beruvchi emassiz.")
        return
    if not bot_active:
        bot.send_message(message.chat.id, "❌ Bot allaqachon o‘chirilgan")
        return
    bot_active = False
    bot.send_message(message.chat.id, "❌ Bot o‘chirilmoqda...")

# ===== + / - ball =====
@bot.message_handler(func=lambda message: message.text.startswith(('+', '-')))
def change_score(message):
    if not bot_active:
        bot.send_message(message.chat.id, "❌ Bot hozir o‘chirilgan. Iltimos, /botstart bilan ishga tushiring.")
        return
    if message.from_user.id not in score_givers:
        bot.send_message(message.chat.id, "❌ Siz ball beruvchi emassiz.")
        return
    try:
        points = int(message.text)
        chat_id = str(message.chat.id)
        user_id = str(message.reply_to_message.from_user.id) if message.reply_to_message else str(message.from_user.id)
        user_name = message.reply_to_message.from_user.first_name if message.reply_to_message else message.from_user.first_name

        if chat_id not in group_scores:
            group_scores[chat_id] = {}

        if user_id in group_scores[chat_id]:
            group_scores[chat_id][user_id]['score'] += points
        else:
            group_scores[chat_id][user_id] = {'score': points, 'name': user_name}

        save_scores()

        bot.send_message(message.chat.id,
                         f"🎉 {user_name} ga {points} ball qo‘shildi! ✅\n"
                         f"Jami ball: {group_scores[chat_id][user_id]['score']}")

        text = generate_ranking(chat_id)
        bot.send_message(message.chat.id, text)

    except ValueError:
        bot.send_message(message.chat.id, "❌ Iltimos, +raqam yoki -raqam formatida yozing. Misol: +10 yoki -5")

# ===== /reyting =====
@bot.message_handler(commands=['reyting'])
def show_ranking(message):
    chat_id = str(message.chat.id)
    text = generate_ranking(chat_id)
    bot.send_message(message.chat.id, text)

# ===== /setscoregiver =====
@bot.message_handler(commands=['setscoregiver'])
def set_score_giver(message):
    global score_givers
    if message.from_user.id != admin_id:
        bot.send_message(message.chat.id, "❌ Siz admin emassiz.")
        return
    if not message.reply_to_message:
        bot.send_message(message.chat.id, "Yangi ball beruvchi qilish uchun foydalanuvchiga reply qiling va /setscoregiver yozing.")
        return
    new_giver_id = message.reply_to_message.from_user.id
    score_givers.add(new_giver_id)
    bot.send_message(message.chat.id,
                     f"⭐ {message.reply_to_message.from_user.first_name} endi ball beruvchi bo‘ldi ✅")

# ===== /setadmin =====
@bot.message_handler(commands=['setadmin'])
def set_admin(message):
    global admin_id
    if message.from_user.id != admin_id:
        bot.send_message(message.chat.id, "❌ Siz admin emassiz.")
        return
    if not message.reply_to_message:
        bot.send_message(message.chat.id, "Adminni o‘zgartirish uchun foydalanuvchiga reply qiling va /setadmin yozing.")
        return
    new_admin_id = message.reply_to_message.from_user.id
    admin_id = new_admin_id
    bot.send_message(message.chat.id, f"👑 {message.reply_to_message.from_user.first_name} endi admin bo‘ldi ✅")

# ===== /clear =====
@bot.message_handler(commands=['clear'])
def clear_scores(message):
    chat_id = str(message.chat.id)
    if message.from_user.id not in score_givers:
        bot.send_message(message.chat.id, "❌ Siz ball beruvchi emassiz.")
        return
    if chat_id in group_scores:
        for user_id in group_scores[chat_id]:
            group_scores[chat_id][user_id]['score'] = 0
        save_scores()
    bot.send_message(message.chat.id, "🗑 Barcha foydalanuvchilar ballari 0 ga tenglandi!")
    bot.send_message(message.chat.id, "🏆🎖 Reyting bo‘sh...")

# ===== Inline tugma clear =====
@bot.callback_query_handler(func=lambda call: call.data == "clear_scores")
def inline_clear(call):
    chat_id = str(call.message.chat.id)
    if call.from_user.id not in score_givers:
        bot.answer_callback_query(call.id, "❌ Siz ball beruvchi emassiz.")
        return
    if chat_id in group_scores:
        for user_id in group_scores[chat_id]:
            group_scores[chat_id][user_id]['score'] = 0
        save_scores()
    bot.answer_callback_query(call.id, "🗑 Barcha ballar 0 ga tenglandi!")
    bot.edit_message_text("🏆🎖 Reyting bo‘sh...", chat_id, call.message.message_id)

bot.polling(none_stop=True
