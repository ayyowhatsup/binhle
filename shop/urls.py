from django.urls import path
from . import views
urlpatterns = [
    path('', views.shop, {}, 'shop'),
    path('<slug:category_slug>/', views.category_single, name = 'category_single'),
    path('product/<slug:book_slug>/', views.product_single, name='product_single'),
    path('author/<slug:author_slug>/', views.author_single, name='author_single'),
]