from django.shortcuts import render
from shop.models import Book, Author, Category, Favorite
# Create your views here.
def shop(request, template_name = "shop/shop.html"):
    books = Book.objects.filter(is_active = True)
    input_data = request.GET
    q = input_data.get('q', '')
    if q != '':
        books = books.filter(name__contains = q)
    orderby = input_data.get('orderby', '')
    if orderby != '':
        books = books.order_by(orderby)
    authors = Author.objects.filter(is_active = True)
    featured_books = Book.objects.filter(is_featured = True, is_active = True)[:3]
    return render(request, template_name, locals())

def category_single(request, category_slug, template_name = 'shop/shop.html'):
    category = Category.objects.get(slug = category_slug, is_active = True)
    books = Book.objects.filter(categories = category, is_active = True)
    input_data = request.GET
    title = category.name
    q = input_data.get('q', '')
    if q != '':
        books = books.filter(name__contains = q)
    orderby = input_data.get('orderby', '')
    if orderby != '':
        books = books.order_by(orderby)
    authors = Author.objects.filter(is_active = True)
    featured_books = Book.objects.filter(is_featured = True, is_active = True)[:3]
    return render(request, template_name, locals())

def product_single(request, book_slug, template_name = 'shop/product_single.html'):
    featured_books = Book.objects.filter(is_featured = True)[:3]
    book = Book.objects.get(slug = book_slug)
    title = book.name
    if request.user.is_authenticated :
        user = request.user
        try:
            favorite = Favorite.objects.get(user = user, product = book)
            setattr(book, 'on_wishlist', True)
        except Favorite.DoesNotExist:
            pass
    return render(request, template_name, locals())


def author_single(request, author_slug, template_name = 'shop/author_single.html'):
    author = Author.objects.get(slug = author_slug)
    title = author.name
    books = Book.objects.filter(authors = author, is_active = True)
    featured_books = books.filter(is_featured = True, is_active = True)
    return render(request, template_name, locals())