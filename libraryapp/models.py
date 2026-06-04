from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

# Create your models here.
class Book(models.Model):
    isbn = models.CharField(
        max_length=17,
        help_text='ISBN-10 または ISBN-13（ハイフン可）',
        verbose_name='ISBN',
        unique=True,
    )
    title = models.CharField(max_length=200, blank=True)
    author = models.CharField(max_length=200, null=True, blank=True)
    publisher = models.CharField(max_length=200, null=True, blank=True)
    publication_date = models.DateField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    cover_url = models.URLField(null=True, blank=True)
    edition_number = models.IntegerField(default=1)

    def __str__(self):
        return self.title


class Location(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Stock(models.Model):
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name="stocks"
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.PROTECT,
        related_name="stocks"
    )
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.book.title} ({self.id})"
    

class Borrow(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    stock = models.ForeignKey(
        Stock,
        on_delete=models.PROTECT,
        related_name="borrows"
    )
    borrowed_at = models.DateTimeField(default=timezone.now)
    due_date = models.DateField()
    returned_at = models.DateTimeField(null=True, blank=True)
        
    def __str__(self):
        return f"{self.stock.book.title} - {self.user.username}"


class Reservation(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="reservations")
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name="reservations")
    reserved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["reserved_at"] # 先着順
        unique_together = ("user", "book")

    def __str__(self):
        return f"{self.user.username} - {self.book.title}" 


class HoldStock(models.Model):
    """
    返却後、予約者への取り置き
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)
    is_pickedup = models.BooleanField(default=False) # 受取済みか
    
    def __str__(self):
        return f"{self.user.username} hold {self.stock.book.title}"
    

class Review(models.Model):
    RATING_CHOICES = [
        (1, "★☆☆☆☆"),
        (2, "★★☆☆☆"),
        (3, "★★★☆☆"),
        (4, "★★★★☆"),
        (5, "★★★★★"),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="reviews"
    )

    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name="reviews"
    )

    rating = models.PositiveSmallIntegerField(
        choices=RATING_CHOICES
    )

    comment = models.TextField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        unique_together = ("user", "book")
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.book.title} - {self.user.username}"