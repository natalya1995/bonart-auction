from django.contrib import admin
from .models import Auction, Lot, Bid, UserProfile, LotImage, Deposit
from django.conf import settings 
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    # Настройте отображение вашей модели в админке
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'phone_number')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'phone_number', 'password1', 'password2'),
        }),
    )
    list_display = ('username', 'email', 'phone_number', 'is_staff')
    search_fields = ('username', 'email', 'phone_number')
    ordering = ('username',)

@admin.action(description='Завершить выбранные аукционы')
def close_selected_auctions(self, request, queryset):
    for auction in queryset:
        if auction.is_closed() and auction.is_active:
            auction.is_active = False
            auction.save()
            print(f"Calling determine_winner for auction {auction.id}")
            determine_winner(auction)  # Вызываем общий метод
    self.message_user(request, 'Выбранные аукционы успешно завершены.')

class LotImageInline(admin.TabularInline):
    model = LotImage
    extra = 1

class DepositInline(admin.TabularInline):
    model = Deposit
    extra = 0
    readonly_fields = ('paid_at', 'status')  # Убедитесь, что 'is_refunded' присутствует
    can_delete = False

class LotAdmin(admin.ModelAdmin):
    inlines = [LotImageInline, DepositInline]
    list_display = ['title', 'start_price', 'current_price', 'is_sold', 'category', 'winner']
    list_filter = ['is_sold', 'category']
    search_fields = ['title', 'description']

class AuctionAdmin(admin.ModelAdmin):
    actions = [close_selected_auctions]
    list_display = ['title', 'start_time', 'end_time', 'is_active', 'owner']
    list_filter = ['is_active', 'owner']
    search_fields = ['title', 'description']

class DepositAdmin(admin.ModelAdmin):
    list_display = ['user', 'lot', 'amount', 'status', 'paid_at']
    list_filter = ['status', 'paid_at']
    search_fields = ['user__username', 'lot__title']

admin.site.register(Auction, AuctionAdmin)
admin.site.register(Lot, LotAdmin)
admin.site.register(Bid)
admin.site.register(UserProfile)
admin.site.register(LotImage)
admin.site.register(Deposit, DepositAdmin)
