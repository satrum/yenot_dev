from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from .models import News

@login_required
def news_like_ajax(request):
	#get news id from ajax
	newsid = None
	if request.method == 'GET':
		newsid = request.GET['news_id']
	#voting and get like count
	like=0
	if newsid:
		current_new = News.objects.get(pk=int(newsid))
		current_new.vote_like(request.user)
		like = current_new.like
	#return like to ajax
	print(like)
	return HttpResponse(like)

@login_required
def news_dislike_ajax(request):
	#get news id from ajax
	newsid = None
	if request.method == 'GET':
		newsid = request.GET['news_id']
	#voting and get like count
	dislike=0
	if newsid:
		current_new = News.objects.get(pk=int(newsid))
		current_new.vote_dislike(request.user)
		dislike = current_new.dislike
	#return like to ajax
	return HttpResponse(dislike)