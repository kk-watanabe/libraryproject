from django.views.generic import TemplateView, ListView, DetailView, View, CreateView
from django.shortcuts import render, get_object_or_404, redirect
from .models import Book, Stock, Borrow, Reservation, HoldStock, Review
from django.db.models import Q
from django.db import transaction
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from datetime import timedelta
from .forms import ReviewForm
from django.urls import reverse
from django.http import JsonResponse
from .services import fetch_book_by_isbn
from django.contrib import messages

# Create your views here.
class SearchView(LoginRequiredMixin, TemplateView):
    template_name="libraryapp/search.html"


class SearchResultsView(LoginRequiredMixin, ListView):
    model = Book
    template_name = "libraryapp/search_results.html"
    context_object_name = "book_list"
    paginate_by = 15

    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get('q', '').strip()

        if not query:
            return Book.objects.none()

        keywords = query.split()

        condition = Q()

        for keyword in keywords:
            condition &= (
                Q(title__icontains=keyword) |
                Q(author__icontains=keyword) |
                Q(publisher__icontains=keyword)
            )

        return queryset.filter(condition)


class BookDetailView(LoginRequiredMixin, DetailView):
    model = Book
    template_name = "libraryapp/book_detail.html"
    context_object_name = "book"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        stocks = self.object.stocks
        
        stocks_count = stocks.count()
        available_stock = stocks.filter(
            is_available=True
        ).first()

        available_stocks_count = stocks.filter(
            is_available=True
        ).count()
        reservation_count = self.object.reservations.count()
        
        # 状態判定
        if stocks_count == 0: #蔵書なし
            status = "no_stocks"
            label = "蔵書なし"
        elif reservation_count != 0:
            status = "reservable"
            label = "貸出中（予約あり）"
        elif available_stocks_count == 0:
            status = "borrowed"
            label = "貸出中"
        else:
            status = "available"
            label = "貸出可能"

        my_borrowed = Borrow.objects.filter(
            stock__book=self.object,
            user=self.request.user,
            returned_at__isnull=True,
        ).exists()
        
        my_reserved = self.object.reservations.filter(
            user=self.request.user
        ).exists()
        
        my_hold = HoldStock.objects.filter(
            stock__book=self.object,
            user=self.request.user,
            is_pickedup=False,
        ).exists()
        
        context["stock"] = available_stock
        context["book_status"] = status
        context["status_label"] = label
        context["my_borrowed"] = my_borrowed
        context["my_reserved"] = my_reserved
        context["my_hold"] = my_hold
        context["reviews"] = self.object.reviews.select_related(
            "user"
        )
        context["bookmeter_url"] = (
            f"https://bookmeter.com/search?keyword={self.object.isbn}"
        )
        
        return context
    

class BorrowConfirmView(LoginRequiredMixin, View):
    template_name = "libraryapp/borrow_confirm.html"
    
    def get(self, request, *args, **kwargs):
        stock = get_object_or_404(Stock, pk=kwargs["stock_id"])

        today = timezone.now().date()

        return render(
            request,
            self.template_name,
            {
                "stock": stock,
                "today": today,
                "default_due_date": today + timedelta(days=14),
                "max_due_date": today + timedelta(days=30),
            }
        )
    
    def post(self, request, *args, **kwargs):
        due_date = request.POST.get("due_date")

        with transaction.atomic():
            stock = (
                Stock.objects
                .select_for_update()
                .get(pk=kwargs["stock_id"])
            )

            if not stock.is_available:
                messages.error(request, "この本は既に貸出中です。")
                return redirect("book_detail", pk=stock.book.pk)

            borrow = Borrow.objects.create(
                stock=stock,
                user=request.user,
                due_date=due_date,
            )

            stock.is_available = False
            stock.save()

        return redirect(
            "borrow_complete",
            stock_id=stock.pk,
            borrow_id=borrow.pk,
        )


class BorrowCompleteView(LoginRequiredMixin, TemplateView):
    template_name = "libraryapp/borrow_complete.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["stock"] = get_object_or_404(
            Stock,
            pk=self.kwargs["stock_id"]
        )

        context["borrow"] = get_object_or_404(
            Borrow,
            pk=self.kwargs["borrow_id"]
        )

        return context


class MyPageView(LoginRequiredMixin, ListView):
    model = Borrow
    template_name = "libraryapp/mypage.html"
    context_object_name = "borrows"

    def get_queryset(self):
        return Borrow.objects.filter(
            user=self.request.user,
            returned_at__isnull=True
        ).select_related("stock__book")
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        reservations = Reservation.objects.filter(
            user=self.request.user
        ).select_related("book")
        
        for reservation in reservations:
            reservation.waiting_count = Reservation.objects.filter(
                book=reservation.book,
                reserved_at__lt=reservation.reserved_at
            ).count()
        
        context['reservations'] = reservations
        context['hold_stocks'] = HoldStock.objects.filter(
            user=self.request.user,
            is_pickedup=False
        ).select_related("stock__book")
        
        return context

class ReturnBookView(LoginRequiredMixin, View):
    template_name = "libraryapp/book_return.html"
    
    def get(self, request, *args, **kwargs):
        borrow = get_object_or_404(
            Borrow,
            pk=kwargs["borrow_id"],
            returned_at__isnull=True
        )
        
        return render(
            request,
            self.template_name,
            {"borrow": borrow}
        )
    
    @transaction.atomic
    def post(self, request, borrow_id):
        borrow = get_object_or_404(
            Borrow.objects.select_related("stock__book"),
            pk=borrow_id,
            returned_at__isnull=True
        )

        stock = borrow.stock
        
        # 返却処理
        borrow.returned_at = timezone.now()
        borrow.save()

        stock.is_available = True
        stock.save()

        # 先着順予約を取得
        reservation = (
            stock.book.reservations
            .select_for_update()
            .first()
        )
        
        if reservation:
            hold = HoldStock.objects.create(
                user=reservation.user,
                stock=stock
            )
        
            stock.is_available = False
            stock.save()
            
            reservation.delete()

        return redirect(
            'return_complete',
            stock_id=stock.pk,
        )


class ReturnCompleteView(LoginRequiredMixin, TemplateView):
    template_name = "libraryapp/return_complete.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["stock"] = get_object_or_404(
            Stock,
            pk=self.kwargs["stock_id"]
        )

        return context


class ReserveBookView(LoginRequiredMixin, View):
    def post(self, request, book_id):
        book = get_object_or_404(Book, pk=book_id)
    
        Reservation.objects.get_or_create(
            user=request.user,
            book=book
        )

        return redirect('book_detail', pk=book_id)


class PickupBorrowView(LoginRequiredMixin, View):
    def post(self, request, pk):
        hold = get_object_or_404(
            HoldStock,
            pk=pk,
            user=request.user,
            is_pickedup=False
        )
        
        due_date = request.POST.get("due_date")

        borrow = Borrow.objects.create(
            user=request.user,
            stock=hold.stock,
            due_date=due_date,
        )
        
        hold.is_pickedup = True
        hold.delete()
        
        return redirect(
            "borrow_complete",
            stock_id=hold.stock.pk,
            borrow_id=borrow.pk,
        )


class PickupConfirmView(LoginRequiredMixin, View):
    template_name = "libraryapp/pickup_confirm.html"

    def get(self, request, pk):
        hold = get_object_or_404(
            HoldStock,
            pk=pk,
            user=request.user,
            is_pickedup=False
        )

        today = timezone.now().date()

        return render(
            request,
            self.template_name,
            {
                "hold": hold,
                "today": today,
                "default_due_date": today + timedelta(days=14),
                "max_due_date": today + timedelta(days=30),
            }
        )
        
    
class ReviewCreateView(LoginRequiredMixin, CreateView):
    model = Review
    form_class = ReviewForm
    template_name = "libraryapp/review_form.html"

    def dispatch(self, request, *args, **kwargs):
        self.book = get_object_or_404(
            Book,
            pk=self.kwargs["book_id"]
        )

        if Review.objects.filter(
            user=request.user,
            book=self.book
        ).exists():
            return redirect(
                "book_detail",
                pk=self.book.pk
            )

        return super().dispatch(
            request,
            *args,
            **kwargs
        )

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.book = self.book

        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            "book_detail",
            kwargs={"pk": self.book.pk}
        )


class BorrowHistoryView(LoginRequiredMixin, ListView):
    model = Borrow
    template_name = "libraryapp/borrow_history.html"
    context_object_name = "histories"
    paginate_by = 15

    def get_queryset(self):
        return (
            Borrow.objects.filter(
                user=self.request.user,
                returned_at__isnull=False
            )
            .select_related("stock__book")
            .order_by("-returned_at")
        )


def book_info_api(request):

    isbn = request.GET.get("isbn")

    if not isbn:
        return JsonResponse(
            {"error": "ISBNが指定されていません"},
            status=400
        )

    data = fetch_book_by_isbn(isbn)

    if not data:
        return JsonResponse(
            {"error": "書籍情報が見つかりません"},
            status=404
        )

    return JsonResponse(data)


class ReservationCancelView(LoginRequiredMixin, View):
    def post(self, request, pk):
        reservation = get_object_or_404(
            Reservation,
            pk=pk,
            user=request.user
        )

        reservation.delete()

        return redirect("mypage")