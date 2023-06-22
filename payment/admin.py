from django.contrib import admin
from .models import Order, OrderItem
# Register your models here.
class OrderAdmin(admin.ModelAdmin):
    pass
admin.site.register(Order,OrderAdmin)

class OrderItemAdmin(admin.ModelAdmin):
    pass
admin.site.register(OrderItem, OrderItemAdmin)