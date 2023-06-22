from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login, name='login'),
    path('account/', views.account, name='account'),
    path('logout/', views.logout, name =  'logout'),
    path('register/', views.register, name = 'register'),
    path('validate/', views.validate_token, name='validate'),
    path('account/dashboard/', views.dashboard, name = 'account_dashboard'),
    path('account/detail/', views.account_detail, name = 'account_detail'),
    path('account/order/', views.order, name = 'account_order'),
    path('account/wishlist/', views.wishlist, name = 'account_wishlist'),
    path('account/order/<str:order_id>/', views.order_detail, name = 'order_detail'),
]