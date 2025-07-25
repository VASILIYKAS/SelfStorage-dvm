from django.contrib import admin
from adminsortable2.admin import SortableStackedInline

from storageapp.models import Storage, StorageUser, Box, UserItem, Order


@admin.register(StorageUser)
class StorageUser(admin.ModelAdmin):
    search_fields = ['email']
    list_display = [
        'first_name',
        'last_name',
        'phone_number'
    ]

class BoxInline(admin.StackedInline):
    model = Box
    extra = 1

@admin.register(Storage)
class Storage(admin.ModelAdmin):
    inlines = [BoxInline]
    list_display = [
        'location',
        'available_boxes_count',
        'total_boxes_count',
        'temperature', 
        'height',
        ]

@admin.register(Box)
class Box(admin.ModelAdmin):
    pass
    

@admin.register(Order)
class Order(admin.ModelAdmin):
    pass


@admin.register(UserItem)
class UserItem(admin.ModelAdmin):
    pass

