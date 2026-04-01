from django.views.generic import TemplateView, ListView
from django.shortcuts import render, get_object_or_404
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

@login_required
def get_book_by_id(request, id):
    book = get_object_or_404(Book, id=id)
    return render(request, 'libraryapp/book_detail.html', {'book': book})

@login_required
def borrow_book(request, stock_id):
    book = get_object_or_404(Stock, id=stock_id)
    
    #if book

    Borrow.objects.create(
        book=book,
        user=request.user,
        due_date=timezone.now().date() + timedelta(days=14)
    )

    book.is_borrowed = True
    book.save()