from django.core.mail import send_mail
from django.conf import settings
from telegram import Bot
from telegram.constants import ParseMode
import asyncio
from twilio.rest import Client

def send_whatsapp_message(to, message):
    """
    Отправка сообщения WhatsApp через Twilio Sandbox
    :param to: Номер получателя в формате 'whatsapp:+77764770878'
    :param message: Текст сообщения
    """
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    
    try:
        message = client.messages.create(
            from_=settings.TWILIO_WHATSAPP_NUMBER,
            body=message,
            to=to
        )
        print(f"Сообщение успешно отправлено на WhatsApp: {to}")
        return message.sid
    except Exception as e:
        print(f"Ошибка при отправке WhatsApp сообщения: {e}")

def send_purchase_confirmation(user, lot):
    subject = f"Подтверждение покупки лота '{lot.title}'"
    message = f"Здравствуйте, {user.username}!\n\nВы успешно оформили покупку лота '{lot.title}' за сумму {lot.current_price} KZT.\n\nСпасибо за участие в аукционе BonArt!"
    recipient_list = [user.email]
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipient_list)

async def send_async_telegram_message(chat_id, message):
    bot = Bot(token="7328241609:AAEykAshzlBpX0CGIkAGcVDLTHtAM_R0Bu8")
    try:
        await bot.send_message(chat_id=chat_id, text=message, parse_mode=ParseMode.HTML)
        print(f"Сообщение успешно отправлено в Telegram: {message}")
    except Exception as e:
        print(f"Ошибка при отправке сообщения: {e}")

def send_telegram_message(chat_id, message):
    asyncio.run(send_async_telegram_message(chat_id, message))
