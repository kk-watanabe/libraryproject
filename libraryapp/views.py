from django.views.generic import TemplateView, ListView, DetailView, View
from django.shortcuts import render, get_object_or_404, redirect
from .models import Book, Stock, Borrow
from django.db.models import Q
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from datetime import timedelta

# Create your views here.
class SearchView(LoginRequiredMixin, TemplateView):
    template_name="libraryapp/search.html"

class SearchResultsView(LoginRequiredMixin, ListView):
    model = Book
    template_name = "libraryapp/search_results.html"
    context_object_name = "book_list"
    paginate_by = 5

    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get('q', '')

        # 検索フィルタリング
        return queryset.filter(
                Q(title__icontains=query) |
                Q(author__icontains=query)
        )

    # ページネーションの設定
    #paginator = Paginator(book_list, 5) # 1ページに5件表示
    #page_number = request.GET.get('page')
    #page_obj = paginator.get_page(page_number)

    #return render(request, 'library/search_results.html', {
    #    'page_obj': page_obj,
    #    'query': query # 検索キーワード保持
    #})

class BookDetailView(LoginRequiredMixin, DetailView):
    model = Book
    template_name = "libraryapp/book_detail.html"
    context_object_name = "book"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        available_stock = self.object.stocks.filter(
            is_available=True
        ).first()
        
        context["available_stock"] = available_stock
        context["is_available"] = available_stock is not None
        
        return context

class BorrowConfirmView(LoginRequiredMixin, View):
    template_name = "libraryapp/borrow_confirm.html"
    
    def get(self, request, *args, **kwargs):
        stock = get_object_or_404(Stock, pk=kwargs["stock_id"])

        return render(
            request,
            self.template_name,
            {"stock": stock}
        )
    
    def post(self, request, *args, **kwargs):
        stock = get_object_or_404(Stock, pk=kwargs["stock_id"])
        
        if not stock.is_available:
            return redirect('book_detail', pk=stock.book.pk)
        
        Borrow.objects.create(
            stock=stock,
            user=request.user
        )
        
        stock.is_available = False
        stock.save()
        
        return redirect('borrow_complete', stock_id=stock.pk)

class BorrowCompleteView(LoginRequiredMixin, TemplateView):
    template_name = "libraryapp/borrow_complete.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["stock"] = get_object_or_404(
            Stock,
            pk=self.kwargs["stock_id"]
        )
        return context

class ReturnView(LoginRequiredMixin, View):
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
    
    def post(self, request, borrow_id):
        borrow = get_object_or_404(
            Borrow,
            pk=borrow_id,
            returned_at__isnull=True
        )
        
        borrow.returned_at = timezone.now()
        borrow.save()
        
        borrow.stock.is_available = True
        borrow.stock.save()
        