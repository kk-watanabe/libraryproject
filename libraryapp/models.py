from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

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
    
    def is_reserved(self):
        return self.reservation_set.filter(is_active=True).exists()

class Borrow(models.Model):
    stock = models.ForeignKey(
        Stock,
        on_delete=models.CASCADE,
        related_name="borrows"
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    borrowed_at = models.DateTimeField(default=timezone.now)
    due_date = models.DateField()
    returned_at = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.due_date:
            self.due_date = timezone.now().date() + timedelta(days=14)
        super().save(*args, **kwargs)
        
    def __str__(self):
        return f"{self.stock.book.title} - {self.user.username}"
    
class Reservation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    reserved_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["reserved_at"]
        unique_together = ("user", "stock")

    def __str__(self):
        return f"{self.user.username} - {self.stock.book.title}" 