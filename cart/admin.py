from django.contrib import admin
from .models import CartItem
# Register your models here.
class CartItemAdmin(admin.ModelAdmin):
    pass
admin.site.register(CartItem, CartItemAdmin)
