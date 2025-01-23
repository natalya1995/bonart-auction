from django.core.management.base import BaseCommand
from auctions.models import Auction
from auctions.views import determine_winner
from django.utils.timezone import now

class Command(BaseCommand):
    help = 'Закрывает завершённые аукционы и определяет победителей'

    def handle(self, *args, **kwargs):
        completed_auctions = Auction.objects.filter(end_time__lt=now(), is_active=True)
        for auction in completed_auctions:
            auction.is_active = False
            auction.save()
            determine_winner(auction.id)
        self.stdout.write(self.style.SUCCESS('Успешно завершены все завершённые аукционы'))
