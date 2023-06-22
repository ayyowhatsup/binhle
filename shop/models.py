from django.db import models
from authentication.models import User
from cloudinary.models import CloudinaryField
# Create your models here.
class Category(models.Model):
    class Meta:
        db_table = "Categories"
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
    
    name = models.CharField(max_length=90)
    slug = models.SlugField()
    description = models.TextField(blank= True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.name

class Author(models.Model):
    class Meta:
        db_table = 'Authors'
        verbose_name = 'Author'
        verbose_name_plural = 'Authors'
    
    name = models.CharField(max_length=90)
    alias = models.CharField(max_length=90, blank=True)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    image = CloudinaryField('image', default = 'v1683009637/default_klejaw.png')
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.name

class Book(models.Model):
    class Meta:
        db_table = 'Books'
        verbose_name = 'Book'
        verbose_name_plural = 'Books'
    
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    image = CloudinaryField('image')
    price = models.DecimalField(max_digits=10, decimal_places=3)
    publisher = models.CharField(max_length=100)
    publish_year = models.IntegerField()
    language = models.CharField(max_length=80, blank=True)
    weight = models.IntegerField(null=True)
    inventory = models.IntegerField()
    is_active = models.BooleanField(default=True)
    authors = models.ManyToManyField(Author, related_name='books')
    categories = models.ManyToManyField(Category)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.name
    
class Favorite(models.Model):

    class Meta:
        db_table = "Favorite"
        verbose_name = "Favorite"
        verbose_name_plural = "Favorites"
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'product'], name='user_product'
            )
        ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Book, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
