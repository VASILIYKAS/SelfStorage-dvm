# admin.py
from django.contrib import admin
from storageapp.models import Storage, StorageUser, Box, UserItem, Order, SentNotification, Discount


@admin.register(StorageUser)
class StorageUserAdmin(admin.ModelAdmin):
    search_fields = ['email', 'first_name', 'last_name', 'phone_number',]
    list_display = [
        'first_name',
        'last_name',
        'email',
        'phone_number',
        'date_joined'
    ]
    list_filter = ['date_joined']
    ordering = ['-date_joined']


class BoxInline(admin.StackedInline):
    model = Box
    extra = 1


@admin.register(Storage)
class StorageAdmin(admin.ModelAdmin):
    inlines = [BoxInline]
    list_display = [
        'location',
        'adress',
        'available_boxes_count',
        'total_boxes_count',
        'temperature',
        'height',
    ]
    search_fields = ['location', 'adress']


@admin.register(Box)
class BoxAdmin(admin.ModelAdmin):
    list_display = [
        'number',
        'storage',
        'user',
        'price',
        'floor',
        'area'
    ]
    list_filter = ['storage', 'floor']
    search_fields = ['number', 'user__email']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'storage_user',
        'box',
        'status',
        'rental_start_date',
        'end_rental_date',
    ]
    list_filter = [
        'status',
        'rental_start_date',
        'discounts__promo_code',
    ]
    search_fields = [
        'storage_user__email',
        'storage_user__phone_number',
        'box__number',
    ]

    def delete_queryset(self, request, queryset):
        for order in queryset:
            if order.box:
                order.box.user = None
                order.box.save()
        super().delete_queryset(request, queryset)

    def delete_model(self, request, obj):
        if obj.box:
            obj.box.user = None
            obj.box.save()
        super().delete_model(request, obj)


@admin.register(UserItem)
class UserItemAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'boxes',
        'area',
        'height'
    ]
    search_fields = ['user__email', 'boxes__number']

    
@admin.register(SentNotification)
class SentNotificationAdmin(admin.ModelAdmin):
    list_display = ('order', 'user_email', 'notification_type', 'sent_at')
    list_filter = ('notification_type', 'sent_at')
    search_fields = ('order__id', 'order__storage_user__email')
    readonly_fields = ('sent_at',)
    
    def user_email(self, obj):
        return obj.order.storage_user.email
    user_email.short_description = 'Email пользователя'
    
    
@admin.register(Discount)
class DiscountAdmin(admin.ModelAdmin):
    pass

