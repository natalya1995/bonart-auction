from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('auctions/', views.auction_list, name='auction_list'),
    path('auctions/<int:auction_id>/', views.lots_by_auction, name='lots_by_auction'),
    path('lot/<int:lot_id>/', views.lot_detail, name='lot_detail'),
    path('lot/<int:lot_id>/pay_deposit/', views.pay_deposit, name='pay_deposit'),
    path('lot/<int:lot_id>/payment/', views.lot_payment, name='lot_payment'),
    path('my-bids/', views.my_bids, name='my_bids'),
    path('profile/', views.profile, name='profile'),
    path('profile/add_balance/', views.add_balance, name='add_balance'),
    path('my-bids/history/', views.my_bids_history, name='my_bids_history'),
    path('bid/<int:bid_id>/cancel/', views.cancel_bid, name='cancel_bid'),
    path('profile/connect_telegram/', views.connect_telegram, name='connect_telegram'),
    path('lot/<int:lot_id>/place_bid/', views.place_bid, name='place_bid'),

]
