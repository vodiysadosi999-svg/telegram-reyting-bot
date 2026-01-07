import telebot
from telebot import types

# BOT TOKEN
TOKEN = "8158074203:AAFo0T07IdDOYeOlsrWf1atkjeW2h4AN40k"
bot = telebot.TeleBot(TOKEN)
bot.remove_webhook()

# Bot holati
bot_active = False  # boshlanishda o‘chirilgan

# Har guruh uchun ballar
group_scores = {}

# Admin va ball beruvchilar
admin_id = 2117076791  # sizning ID
score_givers = {admin_id}

# Telegram suggested commands
commands = [
    types.BotCommand("start", "Bot holatini ko‘rsatadi"),
    types.BotCommand("botstart", "Botni yoqish"),
    types.BotCommand("botstop", "Botni o‘chirish"),
    types.BotCommand("reyting", "Reytingni ko‘rsatish"),
    types.BotCommand("setscoregiver", "Yangi ball beruvchi tayinlash"),
    types.BotCommand("setadmin", "Boshqa foydalanuvchini admin qilish"),
    types.BotCommand("clear", "Hammani ballini 0 ga teng qiladi")
]
bot.set_my_commands(commands)

# /start
@bot.message_handler(commands=['start'])
def start(message):
    status = "ishlayapti ✅" if bot_active else "o‘chirilgan ❌"
    bot.send_message(message.chat.id,
                     f"👋 Salom! Bot holati: {status}\n"
                     "💫 Ball berish/ayirish: +10, -5 yozish kifoya\n"
                     "✍ Foydalanuvchiga reply qilishingiz shart emas\n"
                     "/reyting — Reytingni ko‘rsatish\n"
                     "/setscoregiver — Yangi ball beruvchi tayinlash\n"
                     "/setadmin — Boshqa foydalanuvchini admin qilish\n"
                     "/botstart — Botni yoqish\n"
                     "/botstop — Botni o‘chirish\n"
                     "/clear — Hammani ballini 0 ga teng qilish\n"
                     "/help — Barcha buyruqlar ro‘yxati")

# /help
@bot.message_handler(commands=['help'])
def show_help(message):
    help_text = (
        "📌 Bot buyruqlari:\n\n"
        "👋 /start — Bot holatini ko‘rsatadi\n"
        "🚀 /botstart — Botni yoqish\n"
        "❌ /botstop — Botni o‘chirish\n"
        "🏆 /reyting — Reytingni ko‘rsatish\n"
        "⭐ /setscoregiver — Yangi ball beruvchi tayinlash (reply qilgan foydalanuvchiga)\n"
        "👑 /setadmin — Boshqa foydalanuvchini admin qilish\n"
        "🧹 /clear — Hammani ballini 0 ga teng qiladi\n"
        "➕ +10 yoki -5 — Ball qo‘shish/ayirish\n"
        "ℹ /help — Barcha buyruqlar ro‘yxati"
    )
    bot.send_message(message.chat.id, help_text)

# /botstart
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

# /botstop
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

# + / - ball
@bot.message_handler(func=lambda message: message.text.startswith(('+', '-')))
def change_score(message):
    if not bot_active:
        bot.send_message(message.chat.id, "❌ Bot hozir o‘chirilgan. Iltimos, /botstart bilan ishga tushiring.")
        return
    if message.from_user.id not in score_givers:
        bot.send_message(message.chat.id, "❌ Siz ball beruvchi emassiz.")
        return

    chat_id = message.chat.id
    if chat_id not in group_scores:
        group_scores[chat_id] = {}

    try:
        points = int(message.text)
        user = message.reply_to_message.from_user.first_name if message.reply_to_message else message.from_user.first_name

        if user in group_scores[chat_id]:
            group_scores[chat_id][user] += points
        else:
            group_scores[chat_id][user] = points

        bot.send_message(chat_id,
                         f"🎉 {user} ga {points} ball qo‘shildi! ✅\n"
                         f"Jami ball: {group_scores[chat_id][user]}")

        # Reytingni yangilash
        ranking = sorted(group_scores[chat_id].items(), key=lambda x: x[1], reverse=True)
        text = "🏆🎖 Reyting:\n"
        for i, (u, score) in enumerate(ranking, start=1):
            medal = "🥇" if i==1 else "🥈" if i==2 else "🥉" if i==3 else f"{i}."
            text += f"{medal} {u} — {score} ball\n"
        bot.send_message(chat_id, text)

    except ValueError:
        bot.send_message(chat_id, "❌ Iltimos, +raqam yoki -raqam formatida yozing. Misol: +10 yoki -5")

# /reyting
@bot.message_handler(commands=['reyting'])
def show_ranking(message):
    chat_id = message.chat.id
    if chat_id not in group_scores or not group_scores[chat_id]:
        bot.send_message(chat_id, "Hali ball qo‘shilmagan.")
        return

    ranking = sorted(group_scores[chat_id].items(), key=lambda x: x[1], reverse=True)
    text = "🏆🎖 Reyting:\n"
    for i, (u, score) in enumerate(ranking, start=1):
        medal = "🥇" if i==1 else "🥈" if i==2 else "🥉" if i==3 else f"{i}."
        text += f"{medal} {u} — {score} ball\n"
    bot.send_message(chat_id, text)

# /setscoregiver
@bot.message_handler(commands=['setscoregiver'])
def set_score_giver(message):
    global score_givers
    if message.from_user.id != admin_id:
        bot.send_message(message.chat.id, "❌ Siz admin emassiz.")
        return
    if not message.reply_to_message:
        bot.send_message(message.chat.id, "Yangi ball beruvchi qilish uchun foydalanuvchiga reply qilishingiz kerak.")
        return
    new_giver_id = message.reply_to_message.from_user.id
    score_givers.add(new_giver_id)
    bot.send_message(message.chat.id,
                     f"⭐ {message.reply_to_message.from_user.first_name} endi ball beruvchi bo‘ldi ✅")

# /setadmin
@bot.message_handler(commands=['setadmin'])
def set_admin(message):
    global admin_id
    if message.from_user.id != admin_id:
        bot.send_message(message.chat.id, "❌ Siz admin emassiz.")
        return
    if not message.reply_to_message:
        bot.send_message(message.chat.id, "Adminni o‘zgartirish uchun foydalanuvchiga reply qiling.")
        return
    new_admin_id = message.reply_to_message.from_user.id
    admin_id = new_admin_id
    bot.send_message(message.chat.id, f"👑 {message.reply_to_message.from_user.first_name} endi admin bo‘ldi ✅")

# /clear
@bot.message_handler(commands=['clear'])
def clear_scores(message):
    global group_scores
    if message.from_user.id not in score_givers:
        bot.send_message(message.chat.id, "❌ Siz ball beruvchi emassiz.")
        return

    chat_id = message.chat.id
    group_scores[chat_id] = {}  # Hammani ballini 0 ga teng qilamiz
    bot.send_message(chat_id, "🧹 Hammani ballari 0 ga teng qilindi!")

bot.polling(none_stop=True)
