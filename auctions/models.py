from django.contrib.auth.models import AbstractUser
from decimal import Decimal
from django.db import models
from django.conf import settings 
from django.utils.timezone import now, localtime

class CustomUser(AbstractUser):
    phone_number = models.CharField(max_length=20, unique=True, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    full_name = models.CharField(max_length=255, blank=True, null=True)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['phone_number', 'email']

    def __str__(self):
        return f"{self.username} ({self.phone_number})"

class Auction(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='auctions')
    min_bid_increment = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('10.00'))

    def __str__(self):
        return self.title

    def is_closed(self):
        """Сравнивает текущее (локальное) время с end_time."""
        current_time = localtime(now())
        print(f"Текущее время: {current_time}, Время окончания: {self.end_time}")
        return current_time >= self.end_time

class Lot(models.Model):
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE, related_name='lots')
    title = models.CharField(max_length=255)
    description = models.TextField()
    start_price = models.DecimalField(max_digits=10, decimal_places=2)
    # Удалено: images = models.ManyToManyField('LotImage', related_name='lot_images', blank=True)
    current_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    is_sold = models.BooleanField(default=False)
    winner = models.ForeignKey(
         settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='won_lots'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    category = models.CharField(
        max_length=100,
        choices=[('painting', 'Картина'), ('sculpture', 'Скульптура'),('book','Книга')],
        default='painting'
    )
    deposit_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))

    def save(self, *args, **kwargs):
        """Автоматически устанавливаем 10% от start_price, если deposit_amount пока не установлен."""
        if not self.deposit_amount and self.start_price > 0:
            self.deposit_amount = (self.start_price * Decimal('0.1')).quantize(Decimal('0.01'))
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

class LotImage(models.Model):
    image = models.ImageField(upload_to='lot_images/')
    lot = models.ForeignKey(Lot, on_delete=models.CASCADE, related_name='images')  # Изменено related_name

    def __str__(self):
        return f"Image for {self.lot.title}"

class Bid(models.Model):
    lot = models.ForeignKey(Lot, on_delete=models.CASCADE, related_name='bids')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    bid_amount = models.DecimalField(max_digits=10, decimal_places=2)
    bid_time = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=50,
        choices=[('active', 'Активная'), ('declined', 'Отклонена'), ('winner', 'Победившая')],
        default='active'
    )

    def __str__(self):
        return f'{self.user.username} - {self.bid_amount} KZT'

class Deposit(models.Model):
    STATUS_CHOICES = [
        ('pending', 'В ожидании'),
        ('completed', 'Покупка оформлена'),
        ('refunded', 'Депозит возвращён'),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    lot = models.ForeignKey(Lot, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    paid_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        return f"{self.user.username} - {self.lot.title} - {self.amount} KZT"


class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    telegram_chat_id = models.CharField(max_length=50, blank=True, null=True)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    role = models.CharField(max_length=50, choices=[('user', 'Участник'), ('admin', 'Администратор')], default='user')
    full_name = models.CharField(max_length=255, blank=True, null=True)
    phone_number = models.CharField(max_length=20)
    

    def __str__(self):
        return self.user.username
