from shop.models import Category
from django.conf import settings
from cart.cart import get_cart_items, cart_subtotal, cart_item_count
def context(request):
    return {
        'cart_items': get_cart_items(request),
        'cart_subtotal': cart_subtotal(request),
        "cart_items_count": cart_item_count(request),
        'categories': Category.objects.filter(is_active = True),
        'request': request,
        'title': settings.SITE_NAME
    }  