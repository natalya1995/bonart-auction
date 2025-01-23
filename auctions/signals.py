# auctions/signals.py

from decimal import Decimal
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Auction, Bid, Lot, UserProfile, Deposit
from django.db import transaction
import logging
from django.utils.timezone import now as timezone_now
from .utils import send_telegram_message 

logger = logging.getLogger(__name__)



@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Создаёт профиль только если его ещё нет."""
    if created:
        UserProfile.objects.get_or_create(user=instance)

def notify_winner(lot):
    if lot.winner and lot.winner.userprofile.telegram_chat_id:
        message = (
            f"Поздравляем, {lot.winner.username}! Вы выиграли лот '{lot.title}' "
            f"за {lot.current_price} KZT. Оформите покупку в вашем профиле."
        )
        send_telegram_message(chat_id=lot.winner.userprofile.telegram_chat_id, message=message)
        print(f"Уведомление отправлено победителю: {lot.winner.username}")
    else:
        print(f"Не удалось отправить уведомление: у {lot.winner.username} отсутствует chat_id")

# def notify_winnerW(lot):
#     if lot.winner and lot.winner.userprofile.phone_number:
#         message = (
#             f"Поздравляем, {lot.winner.username}! Вы выиграли лот '{lot.title}' "
#             f"за {lot.current_price} KZT.\n"
#             "Перейдите на сайт, чтобы оформить покупку."
#         )
#         send_whatsapp_message(phone_number=lot.winner.userprofile.phone_number, message=message)

def notify_bid_placed(bid):
    if bid.lot.auction.owner.userprofile.telegram_chat_id:
        message = (
            f"На ваш аукцион '{bid.lot.auction.title}' сделана новая ставка: {bid.bid_amount} KZT.\n"
            f"Лот: {bid.lot.title}, Пользователь: {bid.user.username}."
        )
        send_telegram_message(chat_id=bid.lot.auction.owner.userprofile.telegram_chat_id, message=message)
        print(f"Уведомление отправлено владельцу аукциона: {bid.lot.auction.owner.username}")

@transaction.atomic
def determine_winner(auction: Auction):
    lots = auction.lots.filter(is_sold=False)
    if not lots.exists():
        return

    for lot in lots:
        highest_bid = Bid.objects.filter(lot=lot, status='active').order_by('-bid_amount', 'bid_time').first()
        if highest_bid:
            lot.winner = highest_bid.user
            lot.current_price = highest_bid.bid_amount
            lot.save()

            notify_winner(lot)


            # Обновляем статус победившей ставки
            highest_bid.status = 'winner'
            highest_bid.save()

            # Отправляем уведомление победителю
            notify_winner(lot)

            # Отменяем остальные активные ставки
            losing_bids = Bid.objects.filter(lot=lot).exclude(id=highest_bid.id).filter(status='active')
            for bid in losing_bids:
                bid.status = 'lost'
                bid.save()

                # Возвращаем депозиты проигравших участников
                deposit = Deposit.objects.filter(user=bid.user, lot=lot, status='pending').first()
                if deposit:
                    user_profile = bid.user.userprofile
                    user_profile.balance += deposit.amount
                    user_profile.save()

                    deposit.status = 'refunded'
                    deposit.save()




