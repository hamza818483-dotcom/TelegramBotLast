import os
import logging
import asyncio
from telegram import Update
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    ContextTypes, filters
)
from config import TELEGRAM_BOT_TOKEN, SUPER_ADMINS, TEMP_DIR
from processor import process_pdf, process_image
from quiz import send_quiz_from_csv

# Logging setup
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# ---------------- Commands ----------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(
        f"Hello {user.first_name}! Send me a PDF or Image to create MCQ polls.\n"
        "Use /permit <user_id> to give access to others."
    )

async def permit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in SUPER_ADMINS:
        await update.message.reply_text("You don't have permission to give access.")
        return
    if len(context.args) != 1:
        await update.message.reply_text("Usage: /permit <user_id>")
        return
    permitted_id = int(context.args[0])
    # Save permitted users
    os.makedirs(TEMP_DIR, exist_ok=True)
    permitted_file = os.path.join(TEMP_DIR, "permitted_users.txt")
    with open(permitted_file, "a") as f:
        f.write(f"{permitted_id}\n")
    await update.message.reply_text(f"User {permitted_id} is now permitted.")

# ---------------- PDF Handler ----------------
async def pdf_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.document:
        await update.message.reply_text("Please send a PDF file.")
        return
    pdf_file = await update.message.document.get_file()
    pdf_path = os.path.join(TEMP_DIR, update.message.document.file_name)
    await pdf_file.download_to_drive(pdf_path)
    await update.message.reply_text("PDF received. Processing...")
    args = context.args
    try:
        result_csv = await process_pdf(pdf_path, args)
        await update.message.reply_text(f"CSV ready: {result_csv}")
    except Exception as e:
        logging.error(f"PDF processing failed: {e}")
        await update.message.reply_text("Error processing PDF.")

# ---------------- Image Handler ----------------
async def image_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.photo:
        await update.message.reply_text("Please send an image with prompt using /image [prompt]")
        return
    args = context.args
    if not args:
        await update.message.reply_text("Please provide a prompt after /image")
        return
    prompt = " ".join(args)
    photo_file = await update.message.photo[-1].get_file()
    image_path = os.path.join(TEMP_DIR, f"{update.message.message_id}.jpg")
    await photo_file.download_to_drive(image_path)
    await update.message.reply_text("Image received. Processing...")
    try:
        result_csv = await process_image(image_path, prompt)
        await update.message.reply_text(f"CSV ready: {result_csv}")
    except Exception as e:
        logging.error(f"Image processing failed: {e}")
        await update.message.reply_text("Error processing image.")

# ---------------- CSV to Quiz Handler ----------------
async def csv_to_quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.document:
        await update.message.reply_text("Please send a CSV file.")
        return
    csv_file = await update.message.document.get_file()
    csv_path = os.path.join(TEMP_DIR, update.message.document.file_name)
    await csv_file.download_to_drive(csv_path)
    try:
        await send_quiz_from_csv(update, csv_path)
    except Exception as e:
        logging.error(f"CSV to Quiz failed: {e}")
        await update.message.reply_text("Error sending quiz from CSV.")

# ---------------- Main Function ----------------
async def main():
    os.makedirs(TEMP_DIR, exist_ok=True)
    
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Command Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("permit", permit))
    app.add_handler(CommandHandler("pdfm", pdf_handler))
    app.add_handler(CommandHandler("qbm", pdf_handler))
    app.add_handler(CommandHandler("image", image_handler))
    
    # CSV Upload Handler
    app.add_handler(MessageHandler(filters.Document.FILE_EXTENSION("csv"), csv_to_quiz))
    
    logging.info("Bot is running...")
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
