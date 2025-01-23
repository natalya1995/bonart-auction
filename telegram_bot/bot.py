from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    await update.message.reply_text(
        f"Добро пожаловать в BonArt! Ваш chat_id: {chat_id}.\n"
        f"Используйте этот chat_id для подключения Telegram на нашем сайте."
    )

def main():
    TOKEN = "7328241609:AAEykAshzlBpX0CGIkAGcVDLTHtAM_R0Bu8"
    
    # Создаём объект приложения
    application = Application.builder().token(TOKEN).build()

    # Добавляем обработчик команды /start
    application.add_handler(CommandHandler("start", start))

    # Запускаем бота
    application.run_polling()

if __name__ == "__main__":
    main()
