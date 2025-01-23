from django.contrib.auth import views as auth_views
from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth import login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction, IntegrityError
from django.utils.timezone import now
from django.http import JsonResponse
from django.urls import reverse
from decimal import Decimal, InvalidOperation
from .models import Auction, Lot, Bid, UserProfile, Deposit
from .forms import AddBalanceForm, PlaceBidForm
from .utils import send_whatsapp_message, send_telegram_message
from .signals import determine_winner, notify_bid_placed

User = get_user_model()



@login_required
def connect_telegram(request):
    if request.method == 'POST':
        chat_id = request.POST.get('chat_id')
        if chat_id:
            user_profile = request.user.userprofile
            user_profile.telegram_chat_id = chat_id
            user_profile.save()
            messages.success(request, 'Telegram успешно подключён.')
            return redirect('profile')
        else:
            messages.error(request, 'Введите действительный chat_id.')
    return render(request, 'auctions/connect_telegram.html')

def home(request):
    active_auctions = Auction.objects.filter(is_active=True)
    for auction in active_auctions:
        if auction.is_closed():
            determine_winner(auction)
            auction.is_active = False
            auction.save()

    return render(request, 'auctions/home.html', {
        'active_auctions': Auction.objects.filter(is_active=True),
        'completed_auctions': Auction.objects.filter(is_active=False),
    })

def lots_by_auction(request, auction_id):
    auction = get_object_or_404(Auction, id=auction_id)
    return render(request, 'auctions/lots_by_auction.html', {
        'auction': auction,
        'lots': auction.lots.all(),
    })

from django.db import IntegrityError

def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        phone_number = request.POST.get('phone_number')
        full_name = request.POST.get('full_name')  # Извлекаем full_name
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if password1 != password2:
            messages.error(request, 'Пароли не совпадают.')
            return render(request, 'auctions/register.html')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Это имя пользователя уже занято.')
            return render(request, 'auctions/register.html')

        if User.objects.filter(phone_number=phone_number).exists():
            messages.error(request, 'Этот номер телефона уже используется.')
            return render(request, 'auctions/register.html')

        try:
            user = User.objects.create_user(username=username, password=password1)
            user.save()
            UserProfile.objects.get_or_create(user=user, defaults={'phone_number': phone_number, 'full_name': full_name})
            messages.success(request, 'Регистрация прошла успешно. Вы можете войти в свой аккаунт.')
            login(request, user)
            return redirect('home')
        except IntegrityError as e:
            messages.error(request, 'Ошибка при создании профиля. Попробуйте ещё раз.')
            print(f"Ошибка: {e}")

    return render(request, 'auctions/register.html')


def auction_list(request):
    return render(request, 'auctions/auction_list.html', {
        'auctions': Auction.objects.all(),
    })

def lot_list(request):
    return render(request, 'auctions/lot_list.html', {
        'lots': Lot.objects.all(),
    })

def lot_detail(request, lot_id):
    lot = get_object_or_404(Lot, id=lot_id)
    bids = lot.bids.all().order_by('-bid_amount')
    user_deposits = Deposit.objects.filter(user=request.user, lot=lot, status='pending') if request.user.is_authenticated else Deposit.objects.none()

    if request.method == 'POST':
        if not request.user.is_authenticated:
            return redirect(f"{reverse('login')}?next={request.path}")

        if not user_deposits.exists():
            messages.error(request, "Вы должны оплатить депозит перед ставкой.")
            return redirect('pay_deposit', lot_id=lot.id)

        bid_amount = request.POST.get('bid_amount')
        try:
            bid_amount = Decimal(bid_amount)
        except InvalidOperation:
            messages.error(request, 'Некорректная сумма ставки.')
            return redirect('lot_detail', lot_id=lot.id)

        min_bid = (lot.current_price + lot.auction.min_bid_increment) if lot.current_price else lot.start_price
        if bid_amount < min_bid:
            messages.error(request, f'Ставка должна быть не менее {min_bid} KZT.')
            return redirect('lot_detail', lot_id=lot.id)

        with transaction.atomic():
            Bid.objects.create(lot=lot, user=request.user, bid_amount=bid_amount)
            lot.current_price = bid_amount
            lot.save()

        if request.user.userprofile.telegram_chat_id:
            send_telegram_message(request.user.userprofile.telegram_chat_id, f"Вы сделали ставку на лот '{lot.title}' на сумму {bid_amount} KZT.")

        if request.user.userprofile.phone_number:
            send_whatsapp_message(f"whatsapp:{request.user.userprofile.phone_number}", f"Вы сделали ставку на лот '{lot.title}' на сумму {bid_amount} KZT.")

        messages.success(request, 'Ставка успешно сделана.')
        return redirect('lot_detail', lot_id=lot_id)

    return render(request, 'auctions/lot_detail.html', {
        'lot': lot,
        'bids': bids,
        'user_deposits': user_deposits,
    })

@login_required
def pay_deposit(request, lot_id):
    lot = get_object_or_404(Lot, id=lot_id)
    user_profile = request.user.userprofile

    if Deposit.objects.filter(user=request.user, lot=lot, status='pending').exists():
        messages.info(request, "Вы уже внесли депозит за этот лот.")
        return redirect('lot_detail', lot_id=lot.id)

    deposit_amount = lot.deposit_amount
    if request.method == 'POST':
        if user_profile.balance < deposit_amount:
            messages.error(request, f"Недостаточно средств. Нужно {deposit_amount} KZT.")
            return redirect('pay_deposit', lot_id=lot.id)

        with transaction.atomic():
            user_profile.balance -= deposit_amount
            user_profile.save()
            Deposit.objects.create(user=request.user, lot=lot, amount=deposit_amount, status='pending')

        messages.success(request, f"Вы внесли депозит за лот '{lot.title}'.")
        return redirect('lot_detail', lot_id=lot.id)

    return render(request, 'auctions/pay_deposit.html', {
        'lot': lot,
        'deposit_amount': deposit_amount,
    })

@login_required
def profile(request):
    user_profile = request.user.userprofile
    return render(request, 'auctions/profile.html', {
        'user_profile': user_profile,
        'active_bids': Bid.objects.filter(user=request.user, status='active').select_related('lot__auction'),
        'winning_bids': Bid.objects.filter(user=request.user, status='winner').select_related('lot__auction'),
        'losing_bids': Bid.objects.filter(user=request.user, status='lost').select_related('lot__auction'),
        'deposits': Deposit.objects.filter(user=request.user).select_related('lot__auction'),
        'purchase_history': Lot.objects.filter(winner=request.user, is_sold=True).select_related('auction'),
    })

@login_required
def add_balance(request):
    if request.method == 'POST':
        form = AddBalanceForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            user_profile = request.user.userprofile
            user_profile.balance += amount
            user_profile.save()
            messages.success(request, f"Баланс пополнен на {amount} KZT.")
            return redirect('profile')
    else:
        form = AddBalanceForm()
    return render(request, 'auctions/add_balance.html', {'form': form})

class CustomLoginView(auth_views.LoginView):
    template_name = 'auctions/login.html'
    redirect_authenticated_user = True

    def form_invalid(self, form):
        messages.error(self.request, "Неверные имя пользователя или пароль.")
        return super().form_invalid(form)

    def form_valid(self, form):
        messages.success(self.request, "Вы успешно вошли в систему.")
        return super().form_valid(form)

@login_required
def cancel_bid(request, bid_id):
    bid = get_object_or_404(Bid, id=bid_id, user=request.user, status='active')

    if bid.lot.auction.is_closed():
        messages.error(request, "Аукцион завершён. Отмена невозможна.")
        return redirect('profile')

    with transaction.atomic():
        bid.status
@login_required
def lot_payment(request, lot_id):
    """Оформление покупки выигранного лота"""
    lot = get_object_or_404(Lot, id=lot_id, winner=request.user, is_sold=False)
    user_profile = request.user.userprofile

    # Рассчитываем сумму к оплате
    final_price = lot.current_price or lot.start_price
    deposit_amount = lot.deposit_amount
    remaining_amount = final_price - deposit_amount

    if request.method == "POST":
        if user_profile.balance < remaining_amount:
            messages.error(request, "Недостаточно средств для оплаты остатка.")
            return redirect('lot_payment', lot_id=lot.id)

        with transaction.atomic():
            # Списание остатка с баланса
            user_profile.balance -= remaining_amount
            user_profile.save()

            # Помечаем лот как проданный
            lot.is_sold = True
            lot.save()

        messages.success(
            request,
            f'Вы успешно оплатили лот "{lot.title}". Полная сумма: {final_price} KZT, остаток {remaining_amount} KZT вычтен с вашего баланса.',
        )
        return redirect('profile')

    return render(
        request,
        'auctions/lot_payment.html',
        {
            'lot': lot,
            'final_price': final_price,
            'deposit_amount': deposit_amount,
            'remaining_amount': remaining_amount,
        },
    )
@login_required
def my_bids(request):
    """Отображает все текущие ставки пользователя на активных аукционах"""
    active_bids = Bid.objects.filter(user=request.user, status='active', lot__auction__is_active=True).select_related('lot__auction')

    # Собираем депозиты для каждого лота
    bids_with_deposits = []
    for bid in active_bids:
        deposit = Deposit.objects.filter(user=request.user, lot=bid.lot, status='pending').first()
        bids_with_deposits.append((bid, deposit))

    return render(request, "auctions/my_bids.html", {"bids_with_deposits": bids_with_deposits})
@login_required
def my_bids_history(request):
    """Отображает исторические ставки пользователя на завершённых аукционах"""
    user_bids = Bid.objects.filter(
        user=request.user, lot__auction__is_active=False
    ).order_by("-bid_time").select_related('lot__auction')

    # Собираем депозиты для каждого лота
    bids_with_deposits = []
    for bid in user_bids:
        deposit = Deposit.objects.filter(user=request.user, lot=bid.lot, status__in=['completed', 'refunded']).first()
        bids_with_deposits.append((bid, deposit))

    return render(request, "auctions/my_bids_history.html", {"bids_with_deposits": bids_with_deposits})

@login_required
def place_bid(request, lot_id):
    lot = get_object_or_404(Lot, id=lot_id, is_sold=False)

    # Проверка, завершён ли аукцион
    if lot.auction.is_closed():
        messages.error(request, "Аукцион завершён. Ставки больше не принимаются.")
        return redirect('lot_detail', lot_id=lot.id)

    user_profile = request.user.userprofile
    form = PlaceBidForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            bid_amount = form.cleaned_data['bid_amount']
            min_bid = (lot.current_price + lot.auction.min_bid_increment) if lot.current_price else lot.start_price

            if bid_amount < min_bid:
                messages.error(request, f"Ставка должна быть не менее {min_bid} KZT.")
                return render(request, 'auctions/place_bid.html', {'lot': lot, 'form': form})

            # Проверка наличия депозита
            pending_deposit = Deposit.objects.filter(user=request.user, lot=lot, status='pending').first()
            if not pending_deposit:
                messages.error(request, "Вы должны оплатить депозит перед ставкой.")
                return redirect('pay_deposit', lot_id=lot.id)

            with transaction.atomic():
                # Создание ставки
                bid = Bid.objects.create(lot=lot, user=request.user, bid_amount=bid_amount, status='active')

                # Обновление текущей цены лота
                lot.current_price = bid_amount
                lot.save()

            # Уведомление через Telegram (если подключён chat_id)
            if request.user.userprofile.telegram_chat_id:
                telegram_message = f"Вы сделали ставку на лот '{lot.title}' на сумму {bid_amount} KZT."
                send_telegram_message(chat_id=request.user.userprofile.telegram_chat_id, message=telegram_message)

            # Уведомление через WhatsApp (если указан номер телефона)
            if request.user.userprofile.phone_number:
                whatsapp_message = f"Вы сделали ставку на лот '{lot.title}' на сумму {bid_amount} KZT."
                send_whatsapp_message(
                    to=f"whatsapp:{request.user.userprofile.phone_number}",
                    message=whatsapp_message
                )

            messages.success(request, 'Ставка успешно сделана.')
            return redirect('lot_detail', lot_id=lot_id)
        else:
            messages.error(request, "Ошибка валидации данных. Проверьте введённую сумму.")

    return render(request, 'auctions/place_bid.html', {'lot': lot, 'form': form})
