from django.contrib import admin
from .models import *
# Register your models here.
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
    pass

admin.site.register(Category, CategoryAdmin)


class BookAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
    pass

admin.site.register(Book, BookAdmin)

class AuthorAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
    pass
admin.site.register(Author, AuthorAdmin)


class FavoriteAdmin(admin.ModelAdmin):
    pass
admin.site.register(Favorite, FavoriteAdmin)