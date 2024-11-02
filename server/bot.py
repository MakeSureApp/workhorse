import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
import threading
from common.pereferences import BOT_TOKEN


# Настройка логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Уникальный идентификатор сессии для результатов
waiting_events = {}
waiting_results = {}

# Файл для хранения chat_id
CHAT_ID_FILE = 'chat_id.txt'

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Hello! Waiting for photo to be sent.')

async def handle_callback_query(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    callback_data = query.data
    response_type, unique_id = callback_data.split('_')

    # Сохраняем ответ в словаре
    waiting_results[unique_id] = response_type

    # Уведомляем, что результат получен
    if unique_id in waiting_events:
        waiting_events[unique_id].set()

    await context.bot.send_message(chat_id=user_id, text=f"You selected: {response_type}")

async def makesure(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id

    # Сохраняем chat_id в файл
    with open(CHAT_ID_FILE, 'a') as f:
        f.write(f"{user_id}\n")
    
    await update.message.reply_text('Your chat_id has been saved!')

def run_bot():
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("makesure2024", makesure))
    application.add_handler(CallbackQueryHandler(handle_callback_query))

    application.run_polling()

if __name__ == '__main__':
    run_bot()
