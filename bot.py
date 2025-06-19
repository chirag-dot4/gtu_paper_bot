import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from gtu_scraper import download_paper

# Full session list
sessions = [
    "W2024", "W2023", "W2022", "W2021", "W2020", "W2018", "W2017",
    "S2025", "S2024", "S2023", "S2022", "S2021", "S2020", "S2019", "S2018"
]

# Full course list
courses = [
    "AF", "RA", "BB", "RC", "BD", "RF", "BESP", "RH", "BI", "RI", "BIM", "RN", "BP", "RBSP",
    "BS", "RT", "BV", "CI", "CS", "DA", "DB", "DH", "DI", "DISP", "DM", "DP", "DS", "DV",
    "EP", "FD", "HM", "IB", "IC", "IM", "MA", "MB", "MC", "MCSP", "MD", "ME", "MH", "MI",
    "MN", "MP", "MR", "MS", "MT", "MV", "PB", "PD", "PH", "PM", "PP", "PR", "TE", "VP"
]

user_state = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_state[user_id] = {}

    keyboard = [[InlineKeyboardButton(c, callback_data=f"course|{c}")] for c in courses[:10]]
    await update.message.reply_text("📘 Please select your course (first 10 shown):", reply_markup=InlineKeyboardMarkup(keyboard))

    # Save pagination index
    user_state[user_id]["course_index"] = 0

async def handle_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()
    data = query.data

    if data.startswith("course|"):
        course = data.split("|")[1]
        user_state[user_id]["course"] = course
        keyboard = [[InlineKeyboardButton(s, callback_data=f"session|{s}")] for s in sessions]
        await query.edit_message_text(f"✅ Course: {course}\n📅 Now select session:", reply_markup=InlineKeyboardMarkup(keyboard))

    elif data.startswith("session|"):
        session = data.split("|")[1]
        user_state[user_id]["session"] = session
        await query.edit_message_text(f"✅ Session: {session}\n✏️ Please enter subject code:")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in user_state or "course" not in user_state[user_id] or "session" not in user_state[user_id]:
        await update.message.reply_text("❗ Please start with /start and follow the steps.")
        return

    subject_code = update.message.text.strip()
    course = user_state[user_id]["course"]
    session = user_state[user_id]["session"]

    await update.message.reply_text(f"🔍 Searching for subject code `{subject_code}` in {course}, {session}...")

    file_path = download_paper(session, course, subject_code)
    if file_path:
        with open(file_path, "rb") as f:
            await update.message.reply_document(f)
        os.remove(file_path)
    else:
        await update.message.reply_text("❌ No paper found. Please try again.")

def main():
    TOKEN = os.getenv("API_TOKEN")
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_query))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()

if __name__ == "__main__":
    main()
