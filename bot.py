import json
import requests
from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, Bot
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler

TOKEN = "6663550850:AAG7srmdEyyz-YOpAcRA1aSqMNGwd-2GOP4"
API_KEY = "5be3e6f7ef37395377151dba9cdbd552"
ADMIN_ID = 5581457665

app = Flask(__name__)
bot = Bot(token=TOKEN)

# قائمة بالخدمات (أمثلة)
SERVICES = {
    "13021": "مشاهدات تيك توك رخيصه 😎",
    "13400": "مشاهدات انستا رخيصه 🅰️",
    "14527": "مشاهدات تلي ✅",
    "15007": "لايكات تيك توك جوده عاليه 💎",
    "14676": "لايكات انستا سريعه وقويه 😎👍"
}

# تخزين المستخدمين الذين أرسلوا /start لتجنب التكرار
seen_users = set()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = update.effective_user.username or "مستخدم"

    if user_id == ADMIN_ID:
        keyboard = [
            [InlineKeyboardButton("📋 إدارة الخدمات", callback_data="manage_services"),
             InlineKeyboardButton("📝 الطلبات الأخيرة", callback_data="recent_orders")],
            [InlineKeyboardButton("🚫 حظر مستخدم", callback_data="ban_user"),
             InlineKeyboardButton("🟢 فك الحظر", callback_data="unban_user")],
            [InlineKeyboardButton("✏️ تعديل الترحيب", callback_data="edit_welcome"),
             InlineKeyboardButton("➕ إضافة مشرف", callback_data="add_admin")],
            [InlineKeyboardButton("📢 رسالة جماعية", callback_data="broadcast")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            f"🔧 أهلاً بك يا مدير {username}!\n👇 هذه لوحة تحكم البوت:",
            reply_markup=reply_markup
        )
    else:
        await update.message.reply_text(
            f"أهلاً وسهلاً أخي الكريم {username}!\n👋 يسعدني خدمتك من خلال هذا البوت."
        )

@app.post(f"/webhook/{TOKEN}")
async def webhook(request):
    data = await request.json()
    update = Update.de_json(data, bot)
    await application.process_update(update)
    return {"ok": True}

def main():
    global application
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.run_webhook(
        listen="0.0.0.0",
        port=10000,
        webhook_url=f"https://your-render-url.onrender.com/webhook/{TOKEN}"
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(f"👷‍♂️ تم الضغط على: {query.data}")

if __name__ == "__main__":
    main()
