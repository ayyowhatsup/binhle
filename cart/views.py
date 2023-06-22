from django.shortcuts import render
from . import cart as cart_handler
from django.http import HttpResponse
import json
from django.core.serializers.json import DjangoJSONEncoder

# Create your views here.
def cart(request, template_name = 'cart/cart.html'):
    if request.method == 'POST':
        post_data = request.POST.copy()
        if post_data['operation'] == 'add':
            cart_handler.add_to_cart(request)
            if post_data.get('type', '') == "ajax":
                resp = cart_handler.get_cart_items_dict(request)
                return HttpResponse(json.dumps(resp, cls=DjangoJSONEncoder), content_type = "application/json")
        if post_data['operation'] == 'remove':
            cart_handler.remove_from_cart(request)
            if post_data.get('type', '') == "ajax":
                resp = cart_handler.get_cart_items_dict(request)
                return HttpResponse(json.dumps(resp, cls=DjangoJSONEncoder), content_type = "application/json")
        if post_data['operation'] == 'update':
            cart_handler.update_cart(request)
    cart_items = cart_handler.get_cart_items(request)
    cart_subtotal = cart_handler.cart_subtotal(request)
    return render(request, template_name, locals())