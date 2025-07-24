from django.contrib import admin
from storageapp.models import Storage, StorageUser


@admin.register(StorageUser)
class StorageUser(admin.ModelAdmin):
    pass
    # search_fields = ['first_name, last_name']
    # list_display = ['first_name, last_name, phone_number']


@admin.register(Storage)
class Storage(admin.ModelAdmin):
    pass
    # list_display = [
    #     # 'location',
    #     # 'available_boxes_count',
    #     # 'total_boxes_count',
    #     # 'temperature, height',
    #     # ]