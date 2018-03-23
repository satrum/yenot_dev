from django.shortcuts import render, render_to_response
from django.template import RequestContext

# Create your views here.

#first test:
'''
from django.http import HttpResponse
def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")
'''
from .models import Book, Author, BookInstance, Genre
from .models import News, Source, Banner, Coin
from random import randint
from django.contrib.auth.models import User
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
def index(request, template='index.html', page_template='index_page.html'):#Функция отображения для домашней страницы сайта.
    # Генерация "количеств" некоторых главных объектов
    num_books=Book.objects.all().count()
    num_instances=BookInstance.objects.all().count()
    # Доступные книги (статус = 'a')
    num_instances_available=BookInstance.objects.filter(status__exact='a').count()
    num_authors=Author.objects.count()  # Метод 'all()' применен по умолчанию.
    #ENOT
    num_news=News.objects.count()
    num_sources=Source.objects.count()
    num_votes=UserVotes.objects.count()
	# Number of visits to this view, as counted in the session variable.
    num_visits=request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits+1
    
    #get parameters for filter and sort
    # time - sort by time, rating - sort by rating

    
    #select one banner with status=True
    banners = Banner.objects.filter(status=True, place='t')
    bannerlen=len(banners)
    if bannerlen>0:
        banner = banners[randint(1,bannerlen)-1]
        #banner = Banner.objects.filter(status=True)[randint(1,bannerlen)-1]
        #print(banner.id, banner.status, banner.count_view, banner.image.url)
        banner.count_view += 1
        banner.save()
    else:
        banner=''
    
    banners = Banner.objects.filter(status=True, place='l')
    bannerlen=len(banners)
    if bannerlen>0:
        banner_left = banners[randint(1,bannerlen)-1]
        banner_left.count_view += 1
        banner_left.save()
    else:
        banner_left=''	

    banners = Banner.objects.filter(status=True, place='r')
    bannerlen=len(banners)
    if bannerlen>0:
        banner_right = banners[randint(1,bannerlen)-1]
        banner_right.count_view += 1
        banner_right.save()
    else:
        banner_right=''
    
	#get news_list &coin=BTC&source=ENOT
    rget = request.GET
    #print(rget)
    coin = rget.get('coin')
    source = rget.get('source')
    if coin == '': coin=None
    if source == '': source=None
    #print(coin, source)
    if coin is None:
        if source is None: #coin=None, source=None
            news_list = News.objects.order_by('-time')
        else: #coin=None, source='source.name'
            sourceid=Source.objects.get(name=source)
            news_list = News.objects.order_by('-time').filter(sourceid=sourceid)
    elif source is None: #coin='coin.symbol', source=None
        coinid=Coin.objects.get(symbol=coin)
        news_list = News.objects.order_by('-time').filter(coinid=coinid)
    else: #coin='coin.symbol' , source='source.name'
        coinid=Coin.objects.get(symbol=coin)
        sourceid=Source.objects.get(name=source)
        news_list = News.objects.order_by('-time').filter(coinid=coinid,sourceid=sourceid)
    #print(coinid, sourceid)

	#get set of coins from news_list 
    coins = set([Coin.objects.get(id=v['coinid']).symbol for v in News.objects.values('coinid')])
    #print(coins)
	
	#get set of titles from news_list 
    sources = set([Source.objects.get(sourceid=v['sourceid']).name for v in News.objects.values('sourceid')])
    #print(sources)
	
	#get paginator object from news_list -> news
    page = request.GET.get('page', 1)

    paginator = Paginator(news_list, 7)
    try:
        news = paginator.page(page)
    except PageNotAnInteger:
        news = paginator.page(1)
    except EmptyPage:
        news = paginator.page(paginator.num_pages)
    
	#get votes
    if request.user.is_authenticated:
        view_newslist_block=request.user.profile.view_newslist_block
        for new in news:
            votes=UserVotes.objects.filter(news=new, user=request.user)
            if votes.exists()==0:
                new.enable_vote=True
            else:
                new.enable_vote=False
    else:
        view_newslist_block = 'table'
		
    context={
    'num_books':num_books,
    'num_instances':num_instances,
    'num_instances_available':num_instances_available,
    'num_authors':num_authors,
    'num_news':num_news,
    'num_sources':num_sources,
    'num_visits':num_visits,
    'num_votes':num_votes,
    'allnews':news,
    'view_newslist_block':view_newslist_block,
    'banner':banner,'banner_left':banner_left,'banner_right':banner_right,
    'page_template': page_template,
	'coins': coins,
	'sources': sources,
	'rget': rget}

	# Отрисовка HTML-шаблона index.html с данными внутри 
    # переменной контекста context
    
    return render(request, template, context)

from django.views import generic

class BookListView(generic.ListView):
    model = Book
	#templates: /locallibrary/catalog/templates/catalog/book_list.html
	#help: https://docs.djangoproject.com/en/2.0/topics/class-based-views/
    '''
    context_object_name = 'my_book_list'   # ваше собственное имя переменной контекста в шаблоне
    queryset = Book.objects.filter(title__icontains='war')[:5] # Получение 5 книг, содержащих слово 'war' в заголовке
    template_name = 'books/my_arbitrary_template_name_list.html'  # Определение имени вашего шаблона и его расположения
	'''
class BookDetailView(generic.DetailView):
    model = Book #/locallibrary/catalog/templates/catalog/book_detail.html

from django.contrib.auth.mixins import LoginRequiredMixin #for view only to auth user

class LoanedBooksByUserListView(LoginRequiredMixin,generic.ListView):
    """
    Generic class-based view listing books on loan to current user. 
    """
    model = BookInstance
    template_name ='catalog/bookinstance_list_borrowed_user.html'
    paginate_by = 10
    
    def get_queryset(self):
        return BookInstance.objects.filter(borrower=self.request.user).filter(status__exact='o').order_by('due_back')

#form test:
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
import datetime
from django.contrib.auth.decorators import permission_required

from .forms import RenewBookForm

def renew_book_librarian(request, pk):
    book_inst=get_object_or_404(BookInstance, pk = pk)

    # Если данный запрос типа POST, тогда
    if request.method == 'POST':

        # Создаем экземпляр формы и заполняем данными из запроса (связывание, binding):
        form = RenewBookForm(request.POST)

        # Проверка валидности данных формы:
        if form.is_valid():
            # Обработка данных из form.cleaned_data 
            #(здесь мы просто присваиваем их полю due_back)
            book_inst.due_back = form.cleaned_data['renewal_date']
            book_inst.save()

            # Переход по адресу 'all-borrowed':
            return HttpResponseRedirect(reverse('my-borrowed') ) #all-borrowed

    # Если это GET (или какой-либо еще), создать форму по умолчанию.
    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewBookForm(initial={'renewal_date': proposed_renewal_date,})

    return render(request, 'catalog/book_renew_librarian.html', {'form': form, 'bookinst':book_inst})
	
#------------------------------------------------------
#ENOT Project:

from django.utils import timezone

class NewsListView(generic.ListView):
	template_name = 'catalog/news_list.html'
	model = News
	context_object_name = 'allnews' #name of context in file news_list.html
	paginate_by = 20
	def get_queryset(self):
		#get parameter from kwargs url 'news/<str:time>/'
		if 'time' in self.kwargs:
			time = self.kwargs['time']
		else:
			time = None
		#select range of time - all, day, week, month:
		if time=='' or time==None:
			return News.objects.order_by('-rating')
		else:
			now = timezone.now()
			if time=='day': #day
				delta = datetime.timedelta(days=1)
			elif time=='week': #week
				delta = datetime.timedelta(days=7)
			else: #month
				delta = datetime.timedelta(days=30)
			return News.objects.order_by('-rating').filter(time__range=(now-delta,now)) #example filtered News.objects.filter(title__icontains='BTC')[:4]
		#Добавить атрибут queryset в вашей реализации класса отображения, определяющего order_by().
		#Добавить метод get_queryset в вашу реализацию класса отображения и также определить метод order_by().
	def get_context_data(self, **kwargs):
		# Call the base implementation first to get a context
		context = super(NewsListView, self).get_context_data(**kwargs)
		# Add in a QuerySet of all the books
		#context['book_list'] = Source.objects.all()
		context['num_news']=News.objects.count()
		if self.request.user.is_authenticated:
			context['view_newslist_block']=self.request.user.profile.view_newslist_block
			for news in context['allnews']:
				votes=UserVotes.objects.filter(news=news, user=self.request.user)
				if votes.exists()==0:
					news.enable_vote=True
				else:
					news.enable_vote=False
				#print(news, len(votes), news.like, news.dislike, news.enable_vote)
		for news in context['allnews']:
			coinid = news.coinid
			if coinid:
				coin = Coin.objects.get(symbol=coinid)
				news.symbol = coin.symbol
				news.price = coin.price
				news.change = coin.change
		return context

class NewsDetailView(generic.DetailView):
    model = News

class SourceListView(generic.ListView):
	model = Source
	context_object_name = 'allsource' #name of context in file source_list.html
	def get_queryset(self):
		return Source.objects.order_by('-rating')

class SourceDetailView(generic.DetailView):
    model = Source



#signup:
#https://simpleisbetterthancomplex.com/tutorial/2017/02/18/how-to-create-user-sign-up-view.html
#extend form:
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=False, help_text='Optional.')
    last_name = forms.CharField(max_length=30, required=False, help_text='Optional.')
    email = forms.EmailField(max_length=254, help_text='Required. Inform a valid email address.')

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2', )
	
    def clean_email(self):
        email = self.cleaned_data.get('email')
        username = self.cleaned_data.get('username')
        #print (User.objects.filter(email=email).count())
        if email and User.objects.filter(email=email).exclude(username=username).exists():
            raise forms.ValidationError(u'Email addresses must be unique.')
        return email

from django.contrib.auth import login, authenticate
#from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('index')
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})

#create news from base Form:
class addnewsform(forms.Form):
	title = title = forms.CharField(help_text='name of coin')
	text = forms.CharField(help_text='news text detailed',required=False) #textarea need
	link =  forms.URLField(help_text='url link to news article',initial='https://enot.channel/') 
	DIRECTION = (
        ('b', 'Buy'),
        ('s', 'Sell'),
		('h', 'HODL'),
    )
	direction = forms.ChoiceField(help_text='buy, sell, hodl selector',choices=DIRECTION) #ChoiceField
	source_name = forms.CharField(help_text='Source name selector')

#create news from base Modelform:
from django.forms import ModelForm
from .models import News, Coin
class AddNewsModelForm(ModelForm):
    class Meta:
        model = News
        fields = ['title','text','link','direction','duration','sourceid','proof_image','coinid']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['sourceid'].queryset = Source.objects.filter(moderation_status__in=['o','p'])
'''
    def __init__(self, *args, **kwargs):
        super(AddNewsModelForm, self).__init__(*args, **kwargs)
        # change a widget attribute:
        self.fields['user'].widget.attrs.update({'readonly':'readonly', 'disabled': 'disabled'}) 
'''
from django.contrib.auth.decorators import login_required

import requests
import json
@login_required
def addnews(request):
    if request.method == 'POST':
        form = AddNewsModelForm(request.POST, request.FILES)
        if form.is_valid():
            extend_form = form.save(commit=False)
            extend_form.user = request.user
            #get price:
            coin = str(extend_form.coinid)
            url = 'https://min-api.cryptocompare.com/data/pricemulti?fsyms='+coin+'&tsyms=USD'
            try:
                response = requests.get(url)
                price=response.json()[coin]['USD']
                print('coin: {} price from cryptocompare: {}'.format(coin, price))
            except Exception as error:
                print('error:', error)
                dbcoin=Coin.objects.get(symbol=coin)
                price=dbcoin.price
                print('coin: {} price from db without internet: {}'.format(coin, price))
            print(price)
            extend_form.coinprice = price
            #save
            extend_form.save()
			#time - current time by default
            return redirect('index') #need url for news/pk
    else:
        form = AddNewsModelForm()
    return render(request, 'addnews2.html', {'form': form})	

from .models import UserVotes

@login_required
def news_like(request, pk):
	current_new = News.objects.get(pk=pk)
	current_new.vote_like(request.user)
	votes=UserVotes.objects.filter(news=current_new)
	for vote in votes:
		print(vote.user, vote.news, vote.vote_type)
	print(current_new.text, 'likes:', current_new.like)
	#return redirect('news') # No query parameters
	return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@login_required
def news_dislike(request, pk):
	current_new = News.objects.get(pk=pk)
	current_new.vote_dislike(request.user)
	return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@login_required
def change_view(request):
	profile=request.user.profile
	profile.change_vnb()
	return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

from .models import Banner

def banner_click(request, pk):
	banner=Banner.objects.get(pk=pk)
	banner.count_click += 1
	banner.save()
	return HttpResponseRedirect(banner.link)

def rules(request):
	return render(request, 'rules_template.html')
