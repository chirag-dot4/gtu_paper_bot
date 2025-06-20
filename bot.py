import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from ranker_scraper import get_courses, get_next_level, get_pdf

TOKEN = "YOUR_BOT_TOKEN_HERE"

logging.basicConfig(level=logging.INFO)
user_state = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_state[user_id] = {"step": 0, "path": []}
    courses = get_courses()
    keyboard = [[InlineKeyboardButton(text, callback_data=url)] for text, url in courses]
    await update.message.reply_text("📚 Select your course:", reply_markup=InlineKeyboardMarkup(keyboard))

async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    url = query.data

    if user_id not in user_state:
        user_state[user_id] = {"step": 0, "path": []}

    user_state[user_id]["path"].append(url)
    next_options = get_next_level(url)

    if isinstance(next_options, list):
        keyboard = [[InlineKeyboardButton(text, callback_data=link)] for text, link in next_options]
        await query.edit_message_text("➡️ Select an option:", reply_markup=InlineKeyboardMarkup(keyboard))
    elif isinstance(next_options, str):
        await query.edit_message_text("📥 Downloading paper...")
        file_path = get_pdf(next_options)
        if file_path:
            with open(file_path, "rb") as f:
                await query.message.reply_document(f)
            os.remove(file_path)
        else:
            await query.message.reply_text("❌ Failed to download the paper.")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_button))
    app.run_polling()

if __name__ == "__main__":
    main()
