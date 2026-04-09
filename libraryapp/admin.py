from django.contrib import admin
from django import forms
from .models import Book, Stock, Location, Borrow, Reservation, HoldStock
import requests
from datetime import datetime

# Register your models here.
#admin.site.register(Book)
admin.site.register(Stock)
admin.site.register(Location)
admin.site.register(Borrow)
admin.site.register(Reservation)
admin.site.register(HoldStock)

class BookAdminForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = "__all__"
    
    def clean(self):
        cleaned_data = super().clean()
        isbn = cleaned_data.get("isbn")

        if not isbn:
            return cleaned_data
        
        normalized_isbn = isbn.replace("-", "")

        url = f"https://api.openbd.jp/v1/get?isbn={normalized_isbn}"
        response = requests.get(url, timeout=5)
        data = response.json()

        if not data or data[0] is None:
            return cleaned_data
        
        book_data = data[0]

        summary = book_data.get("summary", {})
        onix = book_data.get("onix", {})

        # タイトル
        if not cleaned_data.get("title"):
            cleaned_data["title"] = summary.get("title", "")

        # 著者
        if not cleaned_data.get("author"):
            cleaned_data["author"] = summary.get("author", "")

        # 出版社
        if not cleaned_data.get("publisher"):
            cleaned_data["publisher"] = summary.get("publisher", "")

        # 出版日
        pubdate = summary.get("pubdate")
        if pubdate and not cleaned_data.get("publication_date"):
            try:
                cleaned_data["publication_date"] = datetime.strptime(
                    pubdate, "%Y%m%d"
                ).date()
            except ValueError:
                pass
        
        # 表紙画像
        if not cleaned_data.get("cover_image"):
            cleaned_data["cover_image"] = summary.get("cover", "")
        
        # 説明
        if not cleaned_data.get("description"):
            try:
                text_contens = (
                    onix["CollateralDetail"]["TextContent"]
                )
                cleaned_data["description"] = text_contens[0].get(
                    "Text", ""
                )
            except Exception:
                pass

        return cleaned_data
    

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "publisher", "isbn")
    search_fields = ("title", "author", "isbn")
