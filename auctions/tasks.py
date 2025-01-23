# auctions/tasks.py

from celery import shared_task
from django.utils import timezone
from .models import Auction
from .signals import determine_winner

@shared_task
def close_expired_auctions():
    now = timezone.now()
    expired_auctions = Auction.objects.filter(is_active=True, end_time__lte=now)
    for auction in expired_auctions:
        auction.is_active = False
        auction.save()
        determine_winner(auction)
