from django.contrib import admin
from .models import Book, Stock, BookShelf

# Register your models here.
admin.site.register(Book)
admin.site.register(Stock)
admin.site.register(BookShelf)