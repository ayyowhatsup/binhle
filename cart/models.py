from django.db import models
from shop.models import Book
#
# (ﾉ◕ヮ◕)ﾉ*:･ﾟ✧
#
# Create your models here.
class CartItem(models.Model):

    class Meta:
        db_table = 'CartItem'
        verbose_name = 'CartItem'
        verbose_name_plural = 'CartItems'


    product = models.ForeignKey(Book, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)
    cart_id = models.CharField(max_length=100, blank=True)

    @property
    def total(self):
        return self.product.price * self.quantity