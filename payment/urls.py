from django.urls import path
from . import views

urlpatterns = [
    path('checkout/', views.checkout, name = 'checkout'),
    path('address/district/', views.get_district, name='address_district'),
    path('address/town/', views.get_town, name = 'address_town'),
    path('shipping-fee/', views.get_shipping_fee, name= 'shipping_fee'),
    path('services/', views.get_services, name='services'),
    path('payment_return/', views.payment_return, name = 'payment_return'),
    path('payment_ipn/', views.payment_ipn, name = 'payment_ipn'),
    path('order_tracking/', views.order_tracking, name='order_tracking')
]