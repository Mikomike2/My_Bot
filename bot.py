from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import os

BOT_TOKEN = "7347792005:AAEYlLgpsbU7iNvPugBr7rVdRZD9kkM7TrI"  # Hardcoded token

user_state = {}

def reset_state(user_id):
    user_state[user_id] = {"step": "year"}

# /start command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reset_state(update.effective_user.id)
    keyboard = [['1st Year', '2nd Year'], ['3rd Year', '4th Year', '5th Year']]
    await update.message.reply_text(
        "📚 Welcome to the Software Engineering Material Bot!\nChoose your year:",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )

# Main handler
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.lower()

    if user_id not in user_state:
        await start(update, context)
        return

    if text in ["menu", "start over", "/start"]:
        return await start(update, context)

    state = user_state[user_id]

    # Step 1: Select Year
    if state["step"] == "year":
        year_map = {
            "1st year": "year1",
            "2nd year": "year2",
            "3rd year": "year3",
            "4th year": "year4",
            "5th year": "year5"
        }
        if text in year_map:
            state["year"] = year_map[text]
            state["step"] = "semester"
            keyboard = [['1st Semester', '2nd Semester'], ['🔙 Back to Year Menu', '🔄 Start Over']]
            await update.message.reply_text(
                f"📘 You chose {text.title()}.\nNow select a semester:",
                reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
            )
        else:
            await update.message.reply_text("❗ Please choose a valid year.")
        return

    # Step 2: Select Semester
    elif state["step"] == "semester":
        if text == "🔙 back to year menu":
            reset_state(user_id)
            return await start(update, context)

        if text == "🔄 start over":
            return await start(update, context)

        sem_map = {
            "1st semester": "1st_semester",
            "2nd semester": "2nd_semester"
        }
        if text in sem_map:
            semester = sem_map[text]
            year = state["year"]
            folder = f"materials/{year}/{semester}"

            if not os.path.exists(folder):
                await update.message.reply_text("📂 No materials found.")
                return

            allowed_extensions = (".pdf", ".pptx", ".docx")
            files = [f for f in os.listdir(folder) if f.lower().endswith(allowed_extensions)]

            if not files:
                await update.message.reply_text("📂 No supported files found in this semester.")
                return

            await update.message.reply_text(f"📥 Sending materials for {year.replace('year', 'Year ').title()}, {text.title()}:")

            for file in files:
                path = os.path.join(folder, file)
                await update.message.reply_document(open(path, "rb"))

            keyboard = [['🔙 Back to Year Menu', '🔄 Start Over']]
            await update.message.reply_text(
                "✅ Done! You can go back to the menu:",
                reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
            )
        else:
            await update.message.reply_text("❗ Please choose a valid semester or option.")
        return

# Build and run the bot
app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

print("✅ Bot is running...")
app.run_polling()
