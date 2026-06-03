from django.urls import path
from . import views

urlpatterns = [
    path('home/', views.SearchView.as_view(), name='home'),
    path('search/results/', views.SearchResultsView.as_view(), name='search_results'),
    path('book/<int:pk>/', views.BookDetailView.as_view(), name='book_detail'),
    path('borrow/<int:stock_id>/', views.BorrowConfirmView.as_view(), name='borrow_confirm'),
    path('borrow/complete/<int:stock_id>/', views.BorrowCompleteView.as_view(), name='borrow_complete'),
    path('mypage/', views.MyPageView.as_view(), name='mypage'),
    path('return/<int:borrow_id>/', views.ReturnBookView.as_view(), name='return_book'),
    path('reserve/<int:book_id>/', views.ReserveBookView.as_view(), name='reserve_book'),
    path('pickup/<int:pk>/', views.PickupBorrowView.as_view(), name='pickup_borrow'),
    path('pickup/confirm/<int:pk>/', views.PickupConfirmView.as_view(), name="pickup_confirm"),
    path('book/<int:book_id>/review/', views.ReviewCreateView.as_view(), name="review_create"),
]
