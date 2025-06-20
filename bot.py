import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters
from gtu_scraper import fetch_pdf

TOKEN = "YOUR_BOT_TOKEN_HERE"

COURSES = ['AF', 'RA', 'BB', 'RC', 'BD', 'RE', 'BESP', 'RH', 'BI', 'RI', 'BIM', 'RN', 'BP', 'RBSP', 'BS', 'BT', 'BV', 'CI', 'CS', 'DA', 'DB', 'DH', 'DI', 'DISP', 'DM', 'DP', 'DS', 'DV', 'EP', 'FD', 'HM', 'IB', 'IC', 'IM', 'MA', 'MB', 'MC', 'MCSP', 'MD', 'ME', 'MH', 'MI', 'MN', 'MP', 'MR', 'MS', 'MT', 'MV', 'PB', 'PD', 'PH', 'PM', 'PP', 'PR', 'TE', 'VP']
SESSIONS = ['W2024', 'W2023', 'W2022', 'W2021', 'W2020', 'W2018', 'W2017', 'S2025', 'S2024', 'S2023', 'S2022', 'S2021', 'S2020', 'S2019', 'S2018']
user_data = {}

logging.basicConfig(level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton(c, callback_data=f"course|{c}")] for c in COURSES]
    await update.message.reply_text("📚 Select Course:", reply_markup=InlineKeyboardMarkup(keyboard))

async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    data = query.data
    if data.startswith("course|"):
        course = data.split("|")[1]
        user_data[user_id] = {"course": course}
        keyboard = [[InlineKeyboardButton(s, callback_data=f"session|{s}")] for s in SESSIONS]
        await query.edit_message_text(f"📘 Course: {course}\n📅 Select Session:", reply_markup=InlineKeyboardMarkup(keyboard))

    elif data.startswith("session|"):
        session = data.split("|")[1]
        user_data[user_id]["session"] = session
        await query.edit_message_text(f"📘 Course: {user_data[user_id]['course']}\n📅 Session: {session}\n✍️ Now enter subject code:")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id not in user_data or "session" not in user_data[user_id]:
        await update.message.reply_text("Please start with /start and select course/session.")
        return

    subject_code = update.message.text.strip()
    course = user_data[user_id]["course"]
    session = user_data[user_id]["session"]

    await update.message.reply_text("🔍 Searching... Please wait...")
    pdf_path = fetch_pdf(course, session, subject_code)
    if pdf_path:
        await update.message.reply_document(document=open(pdf_path, "rb"))
    else:
        await update.message.reply_text("❌ No papers found. Please check the subject code.")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.run_polling()

if __name__ == "__main__":
    main()
