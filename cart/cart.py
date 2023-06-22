import uuid
from .models import CartItem
from shop.models import Book
from django.shortcuts import get_object_or_404
import decimal
from django.forms.models import model_to_dict
from payment.models import Order
CART_ID_SESSION_KEY = 'cart_id'

def _cart_id(request):
    cart_id = request.session.get(CART_ID_SESSION_KEY,'')
    if cart_id == '':
        request.session[CART_ID_SESSION_KEY] = _generate_cart_id()
    else:
        try:
            order = Order.objects.get(id = cart_id)
            request.session[CART_ID_SESSION_KEY] = _generate_cart_id()
        except Order.DoesNotExist:
            pass
    return request.session[CART_ID_SESSION_KEY]

def _generate_cart_id():
    return str(uuid.uuid4()).replace('-', '')

def get_cart_items(request):
    return CartItem.objects.filter(cart_id=_cart_id(request))

def get_cart_items_dict(request):
    cart_items = get_cart_items(request)
    resp = {}
    cart_item_list = []
    for cart_item in cart_items:
        cart_item_dict = model_to_dict(cart_item)
        product = cart_item.product
        product_dict = model_to_dict(product)
        product_dict['image'] = request.build_absolute_uri(product.image.url)
        authors = product_dict.pop('authors')
        product_dict['authors'] = []
        for author in authors:
            temp_author = model_to_dict(author)
            temp_author['image'] = request.build_absolute_uri(author.image.url)
            product_dict['authors'].append(temp_author)
        categories = product_dict.pop('categories')
        product_dict['categories'] = []
        for category in categories:
            temp_category = model_to_dict(category)
            product_dict['categories'].append(temp_category)
        cart_item_dict['product'] = product_dict
        cart_item_list.append(cart_item_dict)
    resp['cart_items'] = cart_item_list
    resp['cart_subtotal'] = cart_subtotal(request)
    resp['cart_items_count'] = cart_item_count(request)

    return resp
def add_to_cart(request):
    post_data = request.POST.copy()
    product_slug = post_data.get('product_slug','')
    quantity = post_data.get('quantity',1)
    book = Book.objects.get(slug = product_slug)
    current_cart_items = get_cart_items(request)
    is_in_cart = False
    for cart_item in current_cart_items:
        if cart_item.product.id == book.id:
            cart_item.quantity = cart_item.quantity + int(quantity)
            cart_item.save()
            is_in_cart = True
    if not is_in_cart:
        ci = CartItem(product = book, quantity = quantity, cart_id = _cart_id(request))
        ci.save()

def cart_distinct_item_count(request):
    return get_cart_items(request).count()

def cart_item_count(request):
    res = 0
    cart_items = get_cart_items(request)
    for cart_item in cart_items:
        res += cart_item.quantity
    return res

def get_single_item(request, product_slug):
    book = get_object_or_404(Book,slug = product_slug)
    return get_object_or_404(CartItem, product = book, cart_id = _cart_id(request))

def update_cart(request):
    post_data = request.POST.copy()
    product_slug = post_data['product_slug']
    quantity = post_data['quantity']
    cart_item = get_single_item(request, product_slug)
    if cart_item:
        if int(quantity) > 0:
            cart_item.quantity = int(quantity)
            cart_item.save()
        else:
            remove_from_cart(request)

def remove_from_cart(request):
    post_data = request.POST.copy()
    product_slug = post_data['product_slug']
    cart_item = get_single_item(request, product_slug)
    if cart_item:
        cart_item.delete()

def cart_subtotal(request):
    cart_total = decimal.Decimal('0.00')
    cart_products = get_cart_items(request)
    for cart_item in cart_products:
        cart_total += cart_item.total
    return cart_total

def is_empty(request):
    return cart_distinct_item_count(request) == 0

def empty_cart(request):
    user_cart = get_cart_items(request)
    user_cart.delete()