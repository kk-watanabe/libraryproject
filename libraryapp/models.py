from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Book(models.Model):
    isbn = models.CharField(
        max_length=17,
        help_text='ISBN-10 または ISBN-13（ハイフン可）',
        verbose_name='ISBN'
    )
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=200)
    publication_date = models.DateField()
    cover_image = models.ImageField(null=True, blank=True)
    edition_number = models.IntegerField()
    is_borrowed = models.BooleanField(default=False, verbose_name="貸出可")

    def __str__(self):
        return self.title

class BookShelf(models.Model):
    bookshelf_name = models.CharField(max_length=200)

    def __str__(self):
        return self.bookshelf_name

class Stock(models.Model):
    isbn = models.ForeignKey(Book,
        on_delete=models.CASCADE,
        related_name="Stocks",
        default=1
    )
    bookshelf_name = models.ForeignKey(
        BookShelf,
        on_delete=models.CASCADE,
        related_name="Stocks",
        default=1
    )

    def __str__(self):
        return self.isbn.title

class Borrow(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(
        Stock,
        on_delete=models.CASCADE,
        related_name="borrows"
    )
    borrowed_at = models.DateTimeField(auto_now_add=True)
    due_date = models.DateField()
    returned_at = models.DateTimeField(null=True, blank=True)
    is_returned = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.book.title} - {self.user.username}"