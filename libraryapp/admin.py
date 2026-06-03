from django.contrib import admin
from django import forms
from django.utils.html import format_html
from .models import Book, Stock, Location, Borrow, Reservation, HoldStock, Review
import requests
from datetime import datetime
from .services import fetch_book_by_isbn

# Register your models here.
class StockInline(admin.TabularInline):
    model = Stock
    extra = 1


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = (
        "cover_preview",
        "title",
        "author",
        "publisher",
        "isbn",
        "stock_count",
    )

    search_fields = (
        "title",
        "author",
        "isbn",
    )

    list_filter = (
        "publisher",
    )

    inlines = [StockInline]

    fields = (
        "isbn",
        "title",
        "author",
        "publisher",
        "publication_date",
        "description",
        "cover_url",
        "edition_number",
    )

    def save_model(self, request, obj, form, change):

        # ISBNのみ入力された場合に自動取得
        if obj.isbn and not obj.title:

            data = fetch_book_by_isbn(obj.isbn)

            if data:
                obj.title = data["title"]
                obj.author = data["author"]
                obj.publisher = data["publisher"]
                obj.publication_date = data["publication_date"]
                obj.cover_url = data["cover_url"]

        super().save_model(
            request,
            obj,
            form,
            change
        )

    @admin.display(description="表紙")
    def cover_preview(self, obj):

        if obj.cover_url:
            return format_html(
                '<img src="{}" width="50">',
                obj.cover_url
            )

        return "-"

    @admin.display(description="蔵書数")
    def stock_count(self, obj):
        return obj.stocks.count()


@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "book",
        "location",
        "is_available",
    )

    list_filter = (
        "is_available",
        "location",
    )

    search_fields = (
        "book__title",
        "book__isbn",
    )


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ("name",)


@admin.register(Borrow)
class BorrowAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "stock",
        "borrowed_at",
        "due_date",
        "returned_at",
    )

    list_filter = (
        "returned_at",
    )

    search_fields = (
        "user__username",
        "stock__book__title",
    )


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "book",
        "reserved_at",
    )


@admin.register(HoldStock)
class HoldStockAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "stock",
        "created_at",
        "is_pickedup",
    )


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = (
        "book",
        "user",
        "rating",
        "created_at"
    )

