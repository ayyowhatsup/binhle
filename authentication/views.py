from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.urls import resolve, reverse
from urllib.parse import urlparse
from django.http import HttpResponse
from payment.models import Order
from .models import User
from shop.models import Favorite, Book
import json
from django.conf import settings
from google.oauth2 import id_token
from google.auth.transport import requests
import uuid
# Create your views here.
def login(request):
    if request.method == 'POST':
        email = request.POST["email"]
        password = request.POST["password"]
        res = {}
        user = authenticate(request, email = email, password=password)
        if user is not None:
            auth_login(request, user)
            res['message'] = "Đăng nhập thành công!"
            return HttpResponse(json.dumps(res), content_type = 'application/json')
        else:
            res['message'] = "Thông tin email hoặc mật khẩu không chính xác!"
            return HttpResponse(json.dumps(res), content_type = 'application/json', status=401)                
    else:
        return redirect("/")

def register(request):
    # :))
    if request.method == 'POST':
        email = request.POST["email"]
        password = request.POST["password"]
        confirm_password = request.POST["confirm_password"]
        res = {}
        if password and confirm_password and email:
            if confirm_password == password:
                try:
                    user = User.objects.get(email = email)
                    res['message'] = "Email đã được sử dụng!"
                    return HttpResponse(json.dumps(res), content_type = 'application/json', status = 400)
                except User.DoesNotExist:
                    user = User.objects.create_user(email=email, password=password)
                    res['message'] = "Tạo tài khoản thành công!"
                    return HttpResponse(json.dumps(res), content_type = 'application/json')
            else:
                res['message'] = "Mật khẩu không giống nhau!"
                return HttpResponse(json.dumps(res), content_type = 'application/json', status=400)  
        else:
            res['message'] = "Vui lòng nhập đầy đủ thông tin!"
            return HttpResponse(json.dumps(res), content_type = 'application/json', status=400)            
    else:
        return redirect("/")

@login_required(login_url="/")
def account(request, template_name = "authentication/account.html"):

    return redirect('account_dashboard')

def logout(request):
    auth_logout(request)
    return redirect("/")

@login_required(login_url="/")
def dashboard(request, template_name = 'authentication/dashboard.html'):

    return render(request, template_name, locals())

@login_required(login_url="/")
def account_detail(request, template_name = 'authentication/account_detail.html'):
    if request.method == 'POST':
        user = request.user
        data = request.POST
        # :))
        name = data.get('name', '')
        phone_number = data.get('phone_number', '')
        email = data.get('email', '')
        current_password = data.get('current_password', '')
        new_password = data.get('new_password', '')
        confirm_new_password = data.get('confirm_new_password','')
        change = False
        if name:
            user.name = name
            change = True
        if phone_number:
            user.phone_number = phone_number
            change = True
        if email:
            try:
                user2 = User.objects.get(email = email)
                error = "Email đã tồn tại trong hệ thống!"
                render(request, template_name, locals())
            except User.DoesNotExist:
                user.email = email
                change = True
        if current_password and new_password and confirm_new_password:
            if not new_password == confirm_new_password:
                error = "Mật khẩu cần phải giống nhau!"
                render(request, template_name, locals())
            elif not user.check_password(current_password):
                error = "Mật khẩu không đúng!"
                render(request, template_name, locals())
            else:
                user.set_password(new_password)
                change = True
        elif current_password or new_password or confirm_new_password:
            error = "Vui lòng điền đầy đủ các trường mật khẩu!"
            render(request, template_name, locals())
        else:
            pass
        if change:
            user.save()
            error = "Thay đổi thông tin thành công!"
    return render(request, template_name, locals())

@login_required(login_url="/")
def order(request, template_name = 'authentication/order.html'):
    orders = Order.objects.filter(user = request.user)
    ORDER_STATUSES = Order.ORDER_STATUSES
    return render(request, template_name, locals())

@login_required(login_url="/")
def wishlist(request, template_name = 'authentication/wishlist.html'):
    if(request.method == 'POST'):
        product_slug = request.POST['product_slug']
        operation = request.POST['operation']
        user = request.user
        book = Book.objects.get(slug = product_slug)
        if operation == 'remove':
            try:
                fav = Favorite.objects.get(user = user, product = book)
                fav.delete()
            except Favorite.DoesNotExist:
                pass
        if operation == 'add':
            try:
                fav = Favorite.objects.get(user = user, product = book)
            except Favorite.DoesNotExist:
                Favorite.objects.create(user = user, product = book)
    wishlist = Favorite.objects.filter(user = request.user)
    return render(request, template_name, locals())

def order_detail(request, order_id,  template_name = 'authentication/order_detail.html'):
    try:
        order = Order.objects.get(id = order_id)
        ORDER_STATUSES = Order.ORDER_STATUSES
    except Order.DoesNotExist:
        return redirect('home_page')
    return render(request, template_name, locals())

@csrf_exempt
def validate_token(request):
    csrf_token_cookie = request.COOKIES.get('g_csrf_token')
    if not csrf_token_cookie:
        return HttpResponse(status=500)
    csrf_token_body = request.POST['g_csrf_token']
    if not csrf_token_body:
        return HttpResponse(status=500)
    if csrf_token_cookie != csrf_token_body:
        return HttpResponse(status=500)

    credential = request.POST['credential']

    idinfo = id_token.verify_oauth2_token(credential, requests.Request(), settings.GOOGLE_CLIENT_ID)

    audience = idinfo['aud']

    if audience != settings.GOOGLE_CLIENT_ID:
        return HttpResponse(status=500)
    
    email = idinfo['email']
    name = idinfo['given_name']

    try:
        user = User.objects.get(email = email)
    except User.DoesNotExist:
        user = User.objects.create_user(email, ''.join(str(uuid.uuid4()).split('-')), is_oauth = True, name = name)

    auth_login(request, user)
    return redirect("home_page")