from django.contrib import admin
from .models import Book, Stock, Location, Borrow

# Register your models here.
admin.site.register(Book)
admin.site.register(Stock)
admin.site.register(Location)
admin.site.register(Borrow)