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


'''
def more_todo(request):
    if request.is_ajax():
        todo_items = ['Mow Lawn', 'Buy Groceries',]
        data = json.dumps(todo_items)
        return HttpResponse(data, content_type='application/json')
    else:
        raise Http404
'''
'''
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
	
    // CSRF code
    function getCookie(name) {
        var cookieValue = null;
        var i = 0;
        if (document.cookie && document.cookie !== '') {
            var cookies = document.cookie.split(';');
            for (i; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    var csrftoken = getCookie('csrftoken');

    function csrfSafeMethod(method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }
    $.ajaxSetup({
        crossDomain: false, // obviates need for sameOrigin test
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type)) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });
	
'''


