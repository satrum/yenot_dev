from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
	path('books/', views.BookListView.as_view(), name='books'),
	path('book/<int:pk>', views.BookDetailView.as_view(), name='book-detail'),
	path('mybooks/', views.LoanedBooksByUserListView.as_view(), name='my-borrowed'),
	path('book/<uuid:pk>/renew/', views.renew_book_librarian, name='renew-book-librarian'),
]

#ENOT

urlpatterns += [   
    path('news/', views.NewsListView.as_view(), name='news'),
    path('news/<int:pk>', views.NewsDetailView.as_view(), name='news-detail'),
	path('news/<int:pk>/like', views.news_like, name='news-like'),
	path('news/<int:pk>/dislike', views.news_dislike, name='news-dislike'),
	path('change_view/', views.change_view, name='change-view'),
	path('source/', views.SourceListView.as_view(), name='source'),
	path('source/<int:pk>', views.SourceDetailView.as_view(), name='source-detail'),
	path('signup/', views.signup, name='signup'),
	path('addnews/', views.addnews, name='addnews'),#form add news
	path('banner/<int:pk>', views.banner_click, name='banner-click'),
	
]
