from django.db import models
from authentication.models import User
from shop.models import Book
# Create your models here.

class Order(models.Model):
    class Meta:
        db_table = 'Orders'
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'
        ordering = ['-created_at']
        
    SUBMITTED = 1
    PROCESSED = 2
    SHIPPED = 3
    CANCELLED = 4
    ORDER_STATUSES=((SUBMITTED,'Submitted'),
                    (PROCESSED,'Processed'),
                    (SHIPPED,'Shipped'),
                    (CANCELLED,'Cancelled'),)

    id = models.CharField(primary_key=True,max_length=50)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    transaction_id = models.CharField(max_length=30)
    status = models.IntegerField(choices=ORDER_STATUSES, default=SUBMITTED)
    product_price = models.DecimalField(max_digits=12, decimal_places=3)
    shipping_fee = models.DecimalField(max_digits=9, decimal_places=3)
    total = models.DecimalField(max_digits=12, decimal_places=3)

    name = models.CharField(max_length=50)
    email = models.EmailField()
    phone_number = models.CharField(max_length=15)

    shipping_province = models.CharField(max_length=100)
    shipping_district = models.CharField(max_length=100)
    shipping_ward = models.CharField(max_length=100)
    shipping_address = models.CharField(max_length=150, blank=True)

    additional_note = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)
    

class OrderItem(models.Model):
    class Meta:
        db_table = 'OrderItems'
        verbose_name = 'OrderItem'
        verbose_name_plural = 'OrderItems'
    product = models.ForeignKey(Book, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    price = models.DecimalField(max_digits=9,decimal_places=3)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items')

    @property
    def total(self):
        return self.product.price * self.quantity