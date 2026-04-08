from django.contrib import admin
from .models import Book, Stock, Location, Borrow, Reservation, HoldStock
from .services import fetch_book_by_isbn

# Register your models here.
admin.site.register(Book)
admin.site.register(Stock)
admin.site.register(Location)
admin.site.register(Borrow)
admin.site.register(Reservation)
admin.site.register(HoldStock)

@admin.register(Book)
