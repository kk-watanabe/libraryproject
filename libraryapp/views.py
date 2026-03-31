from django.views.generic import TemplateView, ListView
from django.shortcuts import render, get_object_or_404
from .models import Book
from django.db.models import Q
from django.core.paginator import Paginator

# Create your views here.
class SearchView(TemplateView):
    template_name="libraryapp/search.html"

class SearchResultsView(ListView):
    model = Book
    template_name = "libraryapp/search_results.html"
    context_object_name = "book_list"
    paginate_by = 5

    def get_queryset(self):
        query = self.request.GET.get('q')

        # 検索フィルタリング
        return Book.objects.filter(
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

def get_book_by_id(request, id):
    book = get_object_or_404(Book, id=id)
    return render(request, 'libraryapp/book_detail.html', {'book': book})