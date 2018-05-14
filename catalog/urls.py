from django.urls import path

from . import views
from . import views_ajax_vote
from . import views_promo

urlpatterns = [
    path('', views.index, name='index'),
	#path('books/', views.BookListView.as_view(), name='books'),
	#path('book/<int:pk>', views.BookDetailView.as_view(), name='book-detail'),
	#path('mybooks/', views.LoanedBooksByUserListView.as_view(), name='my-borrowed'),
	#path('book/<uuid:pk>/renew/', views.renew_book_librarian, name='renew-book-librarian'),
]

#ENOT

urlpatterns += [   
    path('news/', views.NewsListView.as_view(), name='news'),
    path('news/<int:pk>', views.NewsDetailView.as_view(), name='news-detail'),
	path('news/<int:pk>/like', views.news_like, name='news-like'),
	path('news/<int:pk>/dislike', views.news_dislike, name='news-dislike'),
	path('change_view/', views.change_view, name='change-view'), #?
	path('source/', views.SourceListView.as_view(), name='source'), #dev
	path('source/<int:pk>', views.SourceDetailView.as_view(), name='source-detail'),  #dev
	path('signup/', views.signup, name='signup'),
	path('addnews/', views.addnews, name='addnews'),#form add news - in production
	path('banner/<int:pk>', views.banner_click, name='banner-click'),
	path('news/like_news_ajax/', views_ajax_vote.news_like_ajax, name='news-like-ajax'),
	path('news/dislike_news_ajax/', views_ajax_vote.news_dislike_ajax, name='news-dislike-ajax'),
	path('rules/', views.rules, name='rules'),
	path('news/<str:time>/', views.NewsListView.as_view(), name='news'),
	path('profile/', views.profile, name='profile'), #need extend info about profile
	path('profile/addsource/', views.addsource, name='addsource'),
	path('profile/user_update/', views.user_update, name='user_update'),
	path('profile/addpromo/', views_promo.addpromo, name='addpromo'),
	path('news_click/<int:pk>', views.news_click, name='news-click'),
	path('topusers/', views.topusers, name='topusers'),
	#need:
	#coins - table of coins, market data, social stats
	#coin/<int:pk> - all info about coin with external links
	#coin/news - news about coin, stats
	#stats/ - project stats: graphs with news/day, activity(likes, dislikes, profiles)/day total_points
	#profile/portfolio
	#profile/promo_tasks
	#profile/balance - balance + transactions
]
