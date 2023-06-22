from django.shortcuts import render
from shop.models import Book, Author, Category
from django.http import HttpResponseRedirect
def home_page(request, template_name = 'index.html'):
    featured_books = Book.objects.filter(is_featured = True, is_active = True)
    featured_authors = Author.objects.filter(is_featured = True , is_active = True)
    featured_category = Category.objects.filter(is_active = True)[0]
    featured_category_books = Book.objects.filter(categories = featured_category, is_active = True)
    input_data = request.GET
    next = input_data.get('next', '')
    if next != '':
        if(request.user.is_authenticated):
            """
            Navigate if user login successfully
            """
            return HttpResponseRedirect(next)
        else:
            """
            Pop up login side bar in the home page
            """
            login_required = True
            error_login = "Vui lòng đăng nhập để tiếp tục!"
    return render(request, template_name, locals())