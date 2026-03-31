from django.db import models

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
    is_rented = models.BooleanField(default=False, verbose_name="貸出可")

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
    user = models.ForeignKey()
    book = models.ForeignKey(Stock, )
