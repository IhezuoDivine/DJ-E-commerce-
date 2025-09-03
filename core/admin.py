from django.contrib import admin

from .models import Item, OrderItem, Order

class ItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'price', 'category', 'label')  
    list_filter = ('category', 'label') 
    search_fields = ('title',) 

admin.site.register(Item, ItemAdmin)
admin.site.register(OrderItem)
admin.site.register(Order)
