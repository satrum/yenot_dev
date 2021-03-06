from django.shortcuts import render, render_to_response
from django.template import RequestContext

# Create your views here.
##from .models import Book, Author, BookInstance, Genre

from .models import News, Source, Banner, Coin, YeenotSettings, Profile, CoinCryptocompare, Exchange, CoinGecko
from random import randint
from django.contrib.auth.models import User
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

def page_banners():
    #select one banner with status=True
    banners = Banner.objects.filter(status=True, place='t')
    bannerlen=len(banners)
    if bannerlen>0:
        banner = banners[randint(1,bannerlen)-1]
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
    return banner, banner_left, banner_right

def index(request, template='index.html', page_template='index_page.html'):#Функция отображения для домашней страницы сайта.
    #ENOT
    news_rate_max = YeenotSettings.objects.get(name='news_rate_max').num_value
    news_rate_min = YeenotSettings.objects.get(name='news_rate_min').num_value
    num_news=News.objects.count()
    num_sources=Source.objects.count()
    num_votes=UserVotes.objects.count()
	# Number of visits to this view, as counted in the session variable.
    num_visits=request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits+1
    
    #setup banners:
    banner, banner_left, banner_right = page_banners()
    
    #get parameters for filter and sort    
	#get news_list &coin=BTC&source=ENOT
    rget = request.GET
    #print(rget)
    date = rget.get('date')
    coin = rget.get('coin')
    source = rget.get('source')
    direction = rget.get('direction')
    if date == '' or date == 'MM/DD/YYYY' : date=None
    if coin == '': coin=None
    if source == '': source=None
    if direction == '': direction=None
    print(coin, source, direction) #debug only
    #news list filter: Approved for view order: -time
    news_list = News.objects.filter(moderation_status='p').order_by('-time')
    if date is not None:
        news_list = news_list.filter(time__contains=date)
    if coin is not None:
        coinid=Coin.objects.get(symbol=coin)
        news_list = news_list.filter(coinid=coinid)
    if source is not None:
        sourceid=Source.objects.get(name=source)
        news_list = news_list.filter(sourceid=sourceid)
    if direction is not None:
        news_list = news_list.filter(direction=direction)
    '''
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
    '''
    #print(coinid, sourceid)

	#get set of coins from news_list 
    coins = sorted(set([Coin.objects.get(id=v['coinid']).symbol for v in News.objects.values('coinid')]))
    print(coins)
	
	#get set of titles from news_list 
    sources = set([Source.objects.get(sourceid=v['sourceid']).name for v in News.objects.values('sourceid')])
    #print(sources)
	
	#get paginator object from news_list -> news
    page = request.GET.get('page', 1)

    paginator = Paginator(news_list, 20)
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
    'news_rate_max':news_rate_max,
    'news_rate_min':news_rate_min,
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

from django.db.models import Avg, Max, Min, Sum, Q

def profile(request, template='profile.html'):
	if request.user.is_authenticated:
		profile=request.user.profile
		news = News.objects.filter(user=request.user).order_by('-time') #current user news
		profile.news_count = news.count()
		profile.sum_negative = profile.sum_all-profile.sum_positive
		profile.sum_today_negative = profile.sum_today-profile.sum_today_positive
		aggr = news.aggregate(Min('rating'), Avg('rating'), Max('rating'), Sum('like'), Sum('dislike'), Sum('count_link_click'))
		profile.rating_max = aggr['rating__max']
		profile.rating_min = aggr['rating__min']
		profile.rating_avg = aggr['rating__avg']
		profile.likes = aggr['like__sum']
		profile.dislikes = aggr['dislike__sum']
		profile.link_clicks = aggr['count_link_click__sum']
		sources = Source.objects.filter(user=request.user) #current user sources
		context={
		'profile':profile,
		'allnews':news,
		'allsources':sources,
		}
		return render(request, template, context)
	else:
		return redirect('index')
	
def topusers(request, template='topusers.html'):
	#!!!! need: 
	#days on site, 
	#check bio to remove yeenot in test1 rate_users
	#change point calc with news_count (news.rating*k + news.count_link_click + news.count_details_view + news.like(dislike) for all user news)
	#achivements images
	#sum stats about all yeenot points
	#
	#setup banners:
	banner, banner_left, banner_right = page_banners()
	#
	#search:
	search = request.GET.get('search')
	if search == None: search=''
	#print(search)
	
	#list top 3
	topprofiles = Profile.objects.filter(rank__gt=0).order_by('rank')[0:3]
	#add info to top 3 profiles:
	for profile in topprofiles:
		profile.name = profile.user.first_name
		profile.news_count = News.objects.filter(user=profile.user).count()
		if profile.name=='':
			profile.name = profile.user
		#print(profile.rank, profile.sum_positive, profile.sum_likes, profile.sum_dislikes, profile.news_count, profile.point, profile.name)
	#print('-----------------')
	#list top after top 3:
	allprofiles = Profile.objects.filter(rank__gt=3,user__first_name__contains=search).order_by('rank')[0:47]
	#paginator:
	page = request.GET.get('page', 1)
	paginator = Paginator(allprofiles, 12)
	try:
		profiles = paginator.page(page)
	except PageNotAnInteger:
		profiles = paginator.page(1)
	except EmptyPage:
		profiles = paginator.page(paginator.num_pages)
	#add info to profiles:
	for profile in profiles:
		profile.name = profile.user.first_name
		profile.news_count = News.objects.filter(user=profile.user).count()
		if profile.name=='':
			profile.name = profile.user
		#print(profile.rank, profile.sum_positive, profile.sum_likes, profile.sum_dislikes, profile.news_count, profile.point, profile.name)
		#rank, positive vote rate, likes, dislikes, news_count, points, name
	#user place:
	if request.user.is_authenticated:
		userprofile=request.user.profile
		userprofile.name = userprofile.user.first_name
		userprofile.news_count = News.objects.filter(user=request.user).count()
		if userprofile.name=='':
			userprofile.name = userprofile.user
		#print('---------------')
		#print(userprofile.rank, userprofile.sum_positive, userprofile.sum_likes, userprofile.sum_dislikes, userprofile.news_count, userprofile.point, userprofile.name)
		context={'topprofiles':topprofiles,'profiles':profiles, 'userprofile':userprofile,'banner_left':banner_left,'banner_right':banner_right}
		return render(request, template, context)
	else:
		context={'topprofiles':topprofiles,'profiles':profiles,'banner_left':banner_left,'banner_right':banner_right}
		return render(request, template, context)
	
import datetime
def coinlist(request, template='coinlist.html'):
	rget=request.GET
	print(rget)
	#setup banners:
	banner, banner_left, banner_right = page_banners()
	#max and min:
	coins_volume_max = YeenotSettings.objects.get(name='coins_volume_max').num_value
	coins_mktcap_max = YeenotSettings.objects.get(name='coins_mktcap_max').num_value
	coins_change24h_min = YeenotSettings.objects.get(name='coins_change24h_min').num_value
	coins_change24h_max = YeenotSettings.objects.get(name='coins_change24h_max').num_value
	#search:
	search = request.GET.get('search')
	if search == None: search=''
	
	#today:
	today = datetime.date.today() - datetime.timedelta(days=1)
	
	top = rget.get('top')
	if top==None or top=='':
		allcoins = Coin.objects.filter(Q(volume__gt=0,updatetime__gte=today,symbol__icontains=search)|Q(volume__gt=0,updatetime__gte=today,name__icontains=search))#[0:500]#(mktcap__gt=0)#[0:500]
	else:
		allcoins = Coin.objects.all()[0:int(top)]
		print(allcoins)
	
	#Algorithm filter:
	get_algo = request.GET.get('algo')
	if get_algo == '': get_algo = None
	if get_algo is not None:
		allcoins = Coin.objects.filter(pk__in = allcoins,Algorithm__icontains=get_algo) #need after slice
	
	#ProofType filter:
	get_cons = request.GET.get('consensus')
	if get_cons == '': get_cons = None
	if get_cons is not None:
		allcoins = Coin.objects.filter(pk__in = allcoins,ProofType__icontains=get_cons) #need after slice
		
	#exchanges filter:
	exchanges = request.GET.getlist('exchanges')
	print(exchanges, type(exchanges))
	if exchanges == []: exchanges = None
	if exchanges is not None:
		#exlist = exchanges.split(',')
		#exquery = Exchange.objects.filter(exchange__in = exlist)
		exquery = Exchange.objects.filter(exchange__in = exchanges)
		#print(exquery)
		#excoins = set()
		join = rget.get('join') # None - (| OR full join), '1' - (& AND inner join)
		print('number of exchanges:',len(exquery),'join:', join)
		for i in range(len(exquery)):
			ex = exquery[i]
			if i==0:
				excoins = set(ex.get_coinlist())
			else:
			#print( len( ex.get_coinlist() ) )
				if join == '1':
					excoins = excoins & set(ex.get_coinlist()) #inner join & AND
				else:
					excoins = excoins | set(ex.get_coinlist()) #full join | OR
		#excoins = excoins | set(ex.get_coinlist()) # intersection &
		#print(len(excoins))
		allcoins = Coin.objects.filter(pk__in = allcoins,symbol__in=excoins) #need after slice ,
		#print(len(allcoins))
	
	#vol_min=0&vol_max=3484598928&mc_min=0&mc_max=66949548217&ch_min=-99&ch_max=1900&sup_min=0&sup_max=1
	if rget.get('vol_min') is not None: #all range parameter together
		vol_min = float(rget.get('vol_min'))
		vol_max = float(rget.get('vol_max'))+1
		mc_min = float(rget.get('mc_min'))
		mc_max = float(rget.get('mc_max'))+1
		ch_min = float(rget.get('ch_min'))
		ch_max = float(rget.get('ch_max'))
		sup_min = float(rget.get('sup_min'))
		sup_max = float(rget.get('sup_max'))
		#print(type(vol_max), vol_max)
		allcoins = Coin.objects.filter(pk__in = allcoins, volume__gte=vol_min, volume__lte=vol_max, mktcap__gte=mc_min, mktcap__lte=mc_max, change__gte=ch_min, change__lte=ch_max, supply_share__gte=sup_min, supply_share__lte=sup_max)
	
	
	#filter lists:
	algo = Coin.objects.order_by('Algorithm').values_list('Algorithm', flat=True).distinct()
	consensus = Coin.objects.order_by('ProofType').values_list('ProofType', flat=True).distinct()
	#algo = set(allcoins.values_list('Algorithm', flat=True))
	#consensus = set(allcoins.values_list('ProofType', flat=True))
	exchangelist = Exchange.objects.filter(count__gt=0)
	
	coin_counter = allcoins.count()
	for coin in allcoins:
		#coin.news_count = News.objects.filter(coinid = coin).count() # count already in Coin model
		#supply % calculate:
		supply = coin.TotalCoinSupply
		if supply == 'N/A' or supply == '0' or supply == '':
			coin.TotalCoinSupply = ''
		else:
			coin.TotalCoinSupply = supply.split('.')[0].replace(',','').replace(' ','')
			#coin.TotalCoinSupply = int(coin.TotalCoinSupply)
			#coin.supply_share = 100*coin.supply/int(coin.TotalCoinSupply)
		#get coingecko if marketcap = 0 (!!! need change test1 coinadd for faster work)
		if coin.mktcap == 0:
			try:
				coingecko = CoinGecko.objects.get(coinid=coin)
				coin.mktcap = coingecko.market_cap
				#print('found mrkcap in coingecko for coin {} mrkcap={}'.format(coin,coin.mktcap))
			except:
				pass
				#print('mrkcap not found in coingecko for coin {}'.format(coin))
		#get cryptocompare:
		try:
			cc_coin = CoinCryptocompare.objects.get(Id_cc = coin.Id_cc)
			coin.StartDate = cc_coin.StartDate
			if coin.StartDate == datetime.date(1,1,1):
				coin.StartDate = ''
			coin.twitter_posts = cc_coin.twitter_posts
			coin.twitter_followers = cc_coin.twitter_followers
			coin.reddit_subscribers = cc_coin.reddit_subscribers
			coin.reddit_active_users = cc_coin.reddit_active_users
			coin.reddit_posts_per_day = cc_coin.reddit_posts_per_day
		except:
			continue
	'''
	page = request.GET.get('page', 1)
	paginator = Paginator(allcoins, 100)
	try:
		coins = paginator.page(page)
	except PageNotAnInteger:
		coins = paginator.page(1)
	except EmptyPage:
		coins = paginator.page(paginator.num_pages)
	'''
	context = {
	'coins_volume_max':coins_volume_max,
	'coins_mktcap_max':coins_mktcap_max,
	'coins_change24h_min':coins_change24h_min,
	'coins_change24h_max':coins_change24h_max,
	'coins':allcoins, #'coins':coins,
	'coin_counter':coin_counter,
	'algo':algo,
	'consensus':consensus,
	'exchangelist':exchangelist,
	'banner_left':banner_left,
	'banner_right':banner_right,
	'rget':rget,
	}
	if 'exquery' in locals():
		context['exquery']=exquery
		#print(exquery)
	return render(request, template, context)
	
from django.views import generic

'''
class BookListView(generic.ListView):
    model = Book
	#templates: /locallibrary/catalog/templates/catalog/book_list.html
	#help: https://docs.djangoproject.com/en/2.0/topics/class-based-views/
    
    #context_object_name = 'my_book_list'   # ваше собственное имя переменной контекста в шаблоне
    #queryset = Book.objects.filter(title__icontains='war')[:5] # Получение 5 книг, содержащих слово 'war' в заголовке
    #template_name = 'books/my_arbitrary_template_name_list.html'  # Определение имени вашего шаблона и его расположения
'''	

'''
class BookDetailView(generic.DetailView):
    model = Book #/locallibrary/catalog/templates/catalog/book_detail.html
'''
from django.contrib.auth.mixins import LoginRequiredMixin #for view only to auth user
'''
class LoanedBooksByUserListView(LoginRequiredMixin,generic.ListView):
    """
    Generic class-based view listing books on loan to current user. 
    """
    model = BookInstance
    template_name ='catalog/bookinstance_list_borrowed_user.html'
    paginate_by = 10
    
    def get_queryset(self):
        return BookInstance.objects.filter(borrower=self.request.user).filter(status__exact='o').order_by('due_back')
'''

#form test:
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
import datetime
from django.contrib.auth.decorators import permission_required

'''
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
'''
	
#------------------------------------------------------
#ENOT Project:

from django.utils import timezone

class NewsListView(generic.ListView):
	template_name = 'catalog/news_list.html'
	model = News
	context_object_name = 'allnews' #name of context in file news_list.html
	paginate_by = 20
	def get_queryset(self):
		#news moderation filter:
		news = News.objects.filter(moderation_status='p').order_by('-rating') #('p', 'Approved for view')
		#news = News.objects.order_by('-rating')
		#get parameter from kwargs url 'news/<str:time>/'
		if 'time' in self.kwargs:
			time = self.kwargs['time']
		else:
			time = None
		#select range of time - all, day, week, month:
		if time=='' or time==None:
			#return News.objects.order_by('-rating')
			return news
		else:
			now = timezone.now()
			if time=='day': #day
				delta = datetime.timedelta(days=1)
			elif time=='week': #week
				delta = datetime.timedelta(days=7)
			else: #month
				delta = datetime.timedelta(days=30)
			return news.filter(time__range=(now-delta,now)) #example filtered News.objects.filter(title__icontains='BTC')[:4]
		#Добавить атрибут queryset в вашей реализации класса отображения, определяющего order_by().
		#Добавить метод get_queryset в вашу реализацию класса отображения и также определить метод order_by().
	def get_context_data(self, **kwargs):
		# Call the base implementation first to get a context
		context = super(NewsListView, self).get_context_data(**kwargs)
		# Add in a QuerySet of all the books
		#context['book_list'] = Source.objects.all()
		context['num_news']=News.objects.count()
		context['banner'], context['banner_left'], context['banner_right'] = page_banners()
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
	
	def get_context_data(self, **kwargs):
		context = super(NewsDetailView, self).get_context_data(**kwargs)
		if self.request.user.is_authenticated:
			#print(self.kwargs.get('pk'))
			votes=UserVotes.objects.filter(news=self.kwargs.get('pk'), user=self.request.user)
			if votes.exists()==0:
				context['enable_vote']=True
			else:
				context['enable_vote']=False
		#print(context)
		#count_details_view + 1
		news = News.objects.get(newsid=self.kwargs.get('pk'))
		news.count_details_view +=1
		news.save()
		#add banners 4
		banners = Banner.objects.filter(status=True, place='4')
		bannerlen=len(banners)
		if bannerlen>0:
			banner = banners[randint(1,bannerlen)-1]
			print(banner.id, banner.status, banner.count_view, banner.image.url)
			banner.count_view += 1
			banner.save()
		else:
			banner=''
			print('no active left banner')
		context['banner_left']=banner
		#add banners 5
		banners = Banner.objects.filter(status=True, place='5')
		bannerlen=len(banners)
		if bannerlen>0:
			banner = banners[randint(1,bannerlen)-1]
			print(banner.id, banner.status, banner.count_view, banner.image.url)
			banner.count_view += 1
			banner.save()
		else:
			banner=''
			print('no active right banner')
		context['banner_right']=banner
		return context

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
    first_name = forms.CharField(max_length=30, required=True, help_text='Required.')
    last_name = forms.CharField(max_length=30, required=False, help_text='Optional.')
    email = forms.EmailField(max_length=254, help_text='Required. Inform a valid email address.')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].help_text = 'Required. 150 characters or fewer. Letters, digits and @ . + - _ only.'
        self.fields['password1'].help_text = 'Your password cannot be too similar to your other personal information. Your password must contain at least 8 characters. Your password cannot be a commonly used password. Your password cannot be entirely numeric.'
        self.fields['password2'].help_text = 'Enter the same password as before, for verification.'
        self.fields['first_name'].label = 'Nickname'
		#for fieldname in ['username', 'password1', 'password2']:
        #    self.fields[fieldname].help_text = None
	
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

    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')
        username = self.cleaned_data.get('username')
        if first_name and User.objects.filter(first_name=first_name).exclude(username=username).exists():
            raise forms.ValidationError(u'Nickname must be unique.')
        return first_name

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
    coinid = forms.ModelChoiceField(queryset=Coin.objects.order_by('symbol'))
    class Meta:
        model = News
        fields = ['title','text','link','direction','duration','sourceid','proof_image','coinid']
    #sources only moderated:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['sourceid'].queryset = Source.objects.filter(moderation_status__in=['o','p'])
        self.fields['coinid'].label = 'COIN'
'''
    def __init__(self, *args, **kwargs):
        super(AddNewsModelForm, self).__init__(*args, **kwargs)
        # change a widget attribute:
        self.fields['user'].widget.attrs.update({'readonly':'readonly', 'disabled': 'disabled'}) 
'''
from django.contrib.auth.decorators import login_required
from django.core import mail
import requests
import json

@login_required
def addnews(request):
    if request.method == 'POST':
        form = AddNewsModelForm(request.POST, request.FILES)
        if form.is_valid():
            #print(request.FILES['proof_image'])
            extend_form = form.save(commit=False)
            extend_form.user = request.user
            #setup moderation_status default: 'a' Approved for view: 'p'
            try:
                mod_config = YeenotSettings.objects.get(name='addnews_autoapprove').num_value
                if mod_config == 1: #addnews moderation status: 'p' - auto approve
                    extend_form.moderation_status = 'p'
            except Exception:
                print('no addnews_autoapprove setting')
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
            extend_form.coinprice = price
            #save
            extend_form.save()
            #send mail:
            subject = 'News added from user: {} newsid: {}'.format(extend_form.user, extend_form.newsid)
            body = 'news id: {} \n'.format(extend_form.newsid)
            body+= 'time: {} \n'.format(extend_form.time)
            body+= 'coin: {}, coinprice: {} direction: {} duration: {} \n'.format(extend_form.coinid, extend_form.coinprice, extend_form.direction, extend_form.duration)
            body+= 'title: {}, link: {} source: {} \ntext: {} \n'.format(extend_form.title, extend_form.link, extend_form.sourceid, extend_form.text)
            try:
                connection = mail.get_connection()
                mail.send_mail(subject, body, connection.username, [connection.username])
            except Exception:
                mail.send_mail(subject, body, 'admin@localhost', ['moderator@localhost'])
            #time - current time by default
            return redirect('index') #need url for news/pk
    else:
        form = AddNewsModelForm()
    return render(request, 'addnews2.html', {'form': form})	

class AddSourceModelForm(ModelForm):
	class Meta:
		model = Source
		fields = ['name','text','telegram','link',]

@login_required
def addsource(request):	
	if request.method == 'POST':
		form = AddSourceModelForm(request.POST)
		if form.is_valid():
			source = form.save(commit=False)
			source.user = request.user
			source.save()
			#send mail to admin for moderation:
			subject = 'Source added from user: {} sourceid: {}'.format(request.user, source.sourceid)
			body = 'source id: {} \n'.format(source.sourceid, request.user.email)
			body+= ' name: {}\n text: {}\n telegram: {}\n link: {}\n'.format(source.name, source.text, source.telegram, source.link)
			usermail = source.user.email
			userbody = ' New Source(Channel) added for moderation. \n We notify your after this Source change status.'
			connection = mail.get_connection()
			try:
				mail.send_mail(subject, body, connection.username, [connection.username])
				mail.send_mail(subject, body+userbody, connection.username, [usermail])
			except Exception:
				mail.send_mail(subject, body, 'admin@localhost', ['moderator@localhost'])
				mail.send_mail(subject, body+userbody, 'support@localhost', [usermail])
			return redirect('index')
	else:
		form = AddSourceModelForm()
	return render(request, 'addsource2.html', {'form': form})
	
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

def news_click(request, pk):
	new=News.objects.get(pk=pk)
	new.count_link_click += 1
	new.save()
	return HttpResponseRedirect(new.link)
	
def news_share(request):
	if request.method == 'GET':
		newsid = request.GET['id']
		social = request.GET['social']
	new = News.objects.get(pk=int(newsid))
	new.cs_sum+= 1
	if social=='gp':
		new.cs_gp+=1
		url='https://plus.google.com/share?url='+request.build_absolute_uri(new.get_absolute_url())
	if social=='tw':
		new.cs_tw+=1
		#coin = Coin.objects.get(symbol=new.coinid)
		#id = new.coinid.Id_cc
		#twitterurl=CoinCryptocompare.objects.get(Id_cc=id)
		url='https://twitter.com/share?hashtags=YEENOT.TODAY,'+new.coinid.symbol.split('*')[0]+',cryptocurrency,crypto&text='+new.title+'&url='+request.build_absolute_uri(new.get_absolute_url())
	if social=='tg':
		new.cs_tg+=1
		url='https://t.me/share/url?url='+request.build_absolute_uri(new.get_absolute_url())+'&text='+new.title
	if social=='rd':
		new.cs_rd+=1
		url='https://www.reddit.com/submit?title='+new.title+'&url='+request.build_absolute_uri(new.get_absolute_url())
	if social=='fb':
		new.cs_fb+=1
		url='http://www.facebook.com/sharer/sharer.php?s=100&p[url]='+request.build_absolute_uri(new.get_absolute_url())+'&p[images][0]=https://yeenot.today/static/images/YO.png&p[title]='+new.title
	if social=='po':
		new.cs_po+=1
		url='http://profitquery.com/add-to/pocket/?url='+request.build_absolute_uri(new.get_absolute_url())+'&title='+new.title
	if social=='ln':
		new.cs_ln+=1
		url='https://www.linkedin.com/shareArticle?title='+new.title+'&url='+request.build_absolute_uri(new.get_absolute_url())
	new.save()
	print(url)
	return HttpResponseRedirect(url)


from django.http import Http404, HttpResponse
from django.core.validators import validate_email

@login_required
def user_update(request):
	if request.is_ajax() and request.method == 'POST':
		field = request.POST.get('field')
		item = request.POST.get('item')
		print('current user: ',request.user, request.user.first_name, request.user.last_name, request.user.email)
		print('request: ',request.POST.get)
		if field == 'first_name':
			if User.objects.filter(first_name=item).exclude(username=request.user).exists() or item == '': #нужна проверка на соответствие формату почтового адреса и тесты
				print('incorrect nickname')
				item = request.user.first_name
			else:
				print('validate nickname ok')
			#change name
			request.user.first_name = item
			request.user.save()
			#return alert and new name
			data = {'message': "first name changed: {}".format(item), 'item': request.user.first_name}
		elif field == 'last_name':
			request.user.last_name = item
			request.user.save()
			data = {'message': "last name changed: {}".format(item), 'item': request.user.last_name}
		elif field == 'email':
			if User.objects.filter(email=item).exclude(username=request.user).exists() or item == '': #нужна проверка на соответствие формату почтового адреса и тесты
				print('incorrect email')
				item = request.user.email
			try:
				validate_email(item)
				print('validate email ok')
			except:
				print('validate email error')
				item = request.user.email
			request.user.email = item
			request.user.save()
			data = {'message': "email changed: {}".format(item), 'item': request.user.email}			
		print('response: ', data)
		return HttpResponse(json.dumps(data), content_type='application/json')
	else:
		raise Http404
		#return redirect('profile')
