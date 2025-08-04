import json
import logging
import requests
from fastapi import FastAPI, Request
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler,
    MessageHandler, filters, CallbackQueryHandler,
    ContextTypes
)

from services import SERVICES

# إعدادات البوت
TOKEN = "6663550850:AAG7srmdEyyz-YOpAcRA1aSqMNGwd-2GOP4"
API_KEY = "5be3e6f7ef37395377151dba9cdbd552"
ADMIN_ID = 5581457665

# إعداد FastAPI
app = FastAPI()

# بدء تطبيق تيليجرام
application = ApplicationBuilder().token(TOKEN).build()

# إنشاء أزرار الخدمات
def generate_service_buttons():
    buttons = []
    for service_id, name in SERVICES.items():
        buttons.append([InlineKeyboardButton(name, callback_data=f"service_{service_id}")])
    return InlineKeyboardMarkup(buttons)

# عرض قائمة الخدمات عند /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "مرحباً بك! اختر الخدمة التي تريد طلبها:",
        reply_markup=generate_service_buttons()
    )

# التعامل مع الضغط على زر خدمة
async def handle_service_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    service_id = query.data.split("_")[1]
    context.user_data["service_id"] = service_id
    await query.message.reply_text("أرسل الآن الرابط الذي تريد تنفيذ الخدمة عليه:")

# استقبال الرابط
async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if "service_id" not in context.user_data:
        await update.message.reply_text("اختر الخدمة أولاً من القائمة.")
        return

    context.user_data["link"] = update.text
    await update.message.reply_text("أرسل الآن الكمية المطلوبة:")

# استقبال الكمية وتنفيذ الطلب
async def handle_quantity(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if "link" not in context.user_data:
        await update.message.reply_text("أرسل الرابط أولاً.")
        return

    quantity = update.text
    if not quantity.isdigit():
        await update.message.reply_text("الرجاء إرسال رقم صحيح.")
        return

    service_id = context.user_data["service_id"]
    link = context.user_data["link"]

    # تنفيذ الطلب
    response = requests.post("https://kd1s.com/api/v2", data={
        "key": API_KEY,
        "action": "add",
        "service": service_id,
        "link": link,
        "quantity": quantity
    })

    result = response.json()
    if result.get("status") == "error":
        await update.message.reply_text(f"حدث خطأ: {result.get('message')}")
    else:
        order_id = result.get("order")
        await update.message.reply_text(f"تم تنفيذ طلبك بنجاح ✅\nرقم الطلب: {order_id}")
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"طلب جديد:\nالخدمة: {SERVICES[service_id]}\nالرابط: {link}\nالكمية: {quantity}\nرقم الطلب: {order_id}"
        )

    context.user_data.clear()

# ربط Handlers
application.add_handler(CommandHandler("start", start))
application.add_handler(CallbackQueryHandler(handle_service_selection))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_quantity))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link))

# Webhook endpoint
@app.post(f"/webhook/{TOKEN}")
async def webhook(request: Request):
    data = await request.json()
    update = Update.de_json(data, application.bot)
    await application.process_update(update)
    return {"ok": True}
