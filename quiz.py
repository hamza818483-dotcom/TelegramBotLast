import csv
from telegram import Update, Poll
from telegram.ext import ContextTypes

# ---------------- CSV to Poll ----------------
async def send_quiz_from_csv(update: Update, csv_path):
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            question = row["questions"]
            options = [row["option1"], row["option2"], row["option3"], row["option4"]]
            try:
                correct = options.index(row["answer"])
            except ValueError:
                correct = 0  # fallback
            await update.message.reply_poll(
                question=question,
                options=options,
                type=Poll.QUIZ,
                correct_option_id=correct,
                is_anonymous=False
            )

# ---------------- Quiz Link Ready ----------------
def generate_quiz_link(csv_path, quiz_name="Quiz", description=""):
    """
    Returns a pseudo URL to your quiz
    On real deploy, you can host a web page or bot deep-link
    """
    base_url = "https://t.me/YourBotUsername?start=quiz_"
    quiz_id = os.path.basename(csv_path).replace(".csv","")
    return f"{base_url}{quiz_id}"
