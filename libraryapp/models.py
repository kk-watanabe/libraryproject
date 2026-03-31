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

    def __str__(self):
        return self.title

class BookShelf(models.Model):
    bookshelf_name = models.CharField(max_length=200)

    def __str__(self):
        return self.bookshelf_name

class Stock(models.Model):
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name="stocks"
    )
    bookshelf_name = models.ForeignKey(
        BookShelf,
        on_delete=models.CASCADE,
        related_name="stocks"
    )

    def __str__(self):
        return f"{self.book.title} ({self.id})"

class Borrow(models.Model):
    stock = models.ForeignKey(
        Stock,
        on_delete=models.CASCADE,
        related_name="borrows"
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    borrowed_at = models.DateTimeField(auto_now_add=True)
    due_date = models.DateField()
    returned_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.stock.book.title} - {self.user.username}"