from django.urls import path
from . import views

urlpatterns = [
    path('search/', views.SearchView.as_view(), name='search'),
    path('search/results/', views.SearchResultsView.as_view(), name='search_results'),
    path('book/<int:id>', views.get_book_by_id, name='book_detail'),
]
