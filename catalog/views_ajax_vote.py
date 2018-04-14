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

#################
#from django.shortcuts import redirect
import json
from django.http import Http404, HttpResponse
#from django.contrib.auth.models import User

@login_required
def user_update(request):
	if request.is_ajax() and request.method == 'POST':
		field = request.POST.get('field')
		print(field)
		item = request.POST.get('item')
		print(item)
		print(request.user, request.user.first_name, request.user.last_name, request.user.email)
		if field == 'first_name':
			#change name
			request.user.first_name = item
			request.user.save()
			#return alert and new name
			data = {'message': "first name changed: {}".format(item), 'item': request.user.first_name}
			print(data)
		return HttpResponse(json.dumps(data), content_type='application/json')
	else:
		raise Http404
		#return redirect('profile')

'''
def more_todo(request):
    if request.is_ajax():
        todo_items = ['Mow Lawn', 'Buy Groceries',]
        data = json.dumps(todo_items)
        return HttpResponse(data, content_type='application/json')
    else:
        raise Http404

$(document).ready(function() {
    $('.first_name').click(function(){
      console.log('am i called');

        $.ajax({
            type: "POST",
            url: "/catalog/profile/user_update/",
            dataType: "json",
            data: { "item": $(".first_name").val() },
            success: function(data) {
                alert(data.message);
            }
        });

    });
});

    // AJAX GET
    $('.get-more').click(function(){

        $.ajax({
            type: "GET",
            url: "/ajax/more/",
            success: function(data) {
            for(i = 0; i < data.length; i++){
                $('ul').append('<li>'+data[i]+'</li>');
            }
        }
        });

    });
'''


