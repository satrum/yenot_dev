from django.db import models
from django.contrib.auth.models import User #for voting in News, UserVotes and BookInstance
'''
# Create your models here.
class Genre(models.Model):
    name = models.CharField(max_length=200, help_text="Enter a book genre (e.g. Science Fiction, French Poetry etc.)")
    def __str__(self):
        return self.name
'''
from django.urls import reverse #Used to generate URLs by reversing the URL patterns
'''
class Language(models.Model):#Model representing a Language (e.g. English, French, Japanese, etc.)
    name = models.CharField(max_length=200, help_text="Enter a the book's natural language (e.g. English, French, Japanese etc.)")
    
    def __str__(self):#String for representing the Model object (in Admin site etc.)
        return self.name
'''
'''
class Book(models.Model):#    Model representing a book (but not a specific copy of a book).
    title = models.CharField(max_length=200)
    author = models.ForeignKey('Author', on_delete=models.SET_NULL, null=True)
    # Foreign Key used because book can only have one author, but authors can have multiple books
    # Author as a string rather than object because it hasn't been declared yet in the file.
    summary = models.TextField(max_length=1000, help_text="Enter a brief description of the book")
    isbn = models.CharField('ISBN',max_length=13, help_text='13 Character <a href="https://www.isbn-international.org/content/what-isbn">ISBN number</a>')
    genre = models.ManyToManyField(Genre, help_text="Select a genre for this book")
    # ManyToManyField used because genre can contain many books. Books can cover many genres.
    # Genre class has already been defined so we can specify the object above.
    language = models.ForeignKey('Language', on_delete=models.SET_NULL, null=True)
	
    def __str__(self):
        return self.title

    def get_absolute_url(self):#        Returns the url to access a particular book instance.
        return reverse('book-detail', args=[str(self.id)])

    def display_genre(self):#Creates a string for the Genre. This is required to display genre in Admin.
        return ', '.join([ genre.name for genre in self.genre.all()[:3] ])
    display_genre.short_description = 'Genre'
'''
import uuid # Required for unique book instances
from datetime import date #property that we can call from our templates to tell if a particular book instance is overdue.

'''
class BookInstance(models.Model): #    Model representing a specific copy of a book (i.e. that can be borrowed from the library).
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, help_text="Unique ID for this particular book across whole library")
    book = models.ForeignKey('Book', on_delete=models.SET_NULL, null=True) 
    imprint = models.CharField(max_length=200)
    due_back = models.DateField(null=True, blank=True)

    LOAN_STATUS = (
        ('m', 'Maintenance'),
        ('o', 'On loan'),
        ('a', 'Available'),
        ('r', 'Reserved'),
    )

    status = models.CharField(max_length=1, choices=LOAN_STATUS, blank=True, default='d', help_text='Book availability')
    borrower = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
	
    class Meta:
        ordering = ["due_back"]
        permissions = (("can_mark_returned", "Set book as returned"),)

    def __str__(self):#String for representing the Model object
        return '%s (%s)' % (self.id,self.book.title)
    
    @property
    def is_overdue(self):
        if self.due_back and date.today() > self.due_back:
            return True
        return False
'''

'''
class Author(models.Model):#Model representing an author.
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField(null=True, blank=True)
    date_of_death = models.DateField('Died', null=True, blank=True)
    
    def get_absolute_url(self):#Returns the url to access a particular author instance.
        return reverse('author-detail', args=[str(self.id)])

    def __str__(self):
        return '%s, %s' % (self.last_name, self.first_name)
'''

#-----------------------------------------		
#Project: ENOT Channels
# blank=True - field not nessesary for edit

#create profile end-to-end:
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=30, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    view_newslist_block = models.CharField(max_length = 10, default = 'table', help_text = 'table or blocked view for news list') #see class NewsListView(generic.ListView)
    #stats:
    sum_all = models.DecimalField(default=0.0, blank=True, max_digits=10, decimal_places=2, help_text = 'sum of all vote_rate')
    sum_positive = models.DecimalField(default=0.0, blank=True, max_digits=10, decimal_places=2, help_text = 'sum of all positive vote_rate')
    sum_today = models.DecimalField(default=0.0, blank=True, max_digits=10, decimal_places=2, help_text = 'sum of all vote_rate last day')
    sum_today_positive = models.DecimalField(default=0.0, blank=True, max_digits=10, decimal_places=2, help_text = 'sum of all positive vote_rate last day')
    sum_likes=models.IntegerField(default=0, blank=True, help_text='likes of user')
    sum_dislikes=models.IntegerField(default=0, blank=True, help_text='dislikes of user')
    sum_right=models.IntegerField(default=0, blank=True, help_text='right votes (vote_rate>0)')
    sum_news_rating=models.DecimalField(default=0.0, blank=True, max_digits=10, decimal_places=2, help_text = 'sum of user news rating')
    sum_news=models.IntegerField(default=0, blank=True, help_text='sum of user news')
    #first stage: point = sum_positive
    point=models.DecimalField(default=0.0, blank=True, max_digits=10, decimal_places=2, help_text = 'user points')
    rank=models.IntegerField(default=0, blank=True, help_text='place of user sorted by points')
	
    @receiver(post_save, sender=User)
    def create_user_profile(sender, instance, created, **kwargs):
        if created:
            Profile.objects.create(user=instance)

    @receiver(post_save, sender=User)
    def save_user_profile(sender, instance, **kwargs):
        instance.profile.save()

    def change_vnb(self):
        if self.view_newslist_block == 'table':
            self.view_newslist_block = 'block'
        else:
            self.view_newslist_block = 'table'
        self.save()
		

from  django.utils import timezone
from django.core.validators import MinLengthValidator
from django.template.defaultfilters import truncatechars

class News(models.Model):
    newsid = models.AutoField(primary_key=True, help_text="news id")
    text = models.TextField(max_length=2000,verbose_name="DESCRIPTION OF NEWS",validators=[MinLengthValidator(20)], help_text="YOUR MESSAGE MUST HAVE MORE THAN 20 CHARACTERS")
    title = models.CharField(max_length=100,verbose_name="TITLE OF NEWS:") # резервирую название на будущее, для сигналов нет
    link =  models.URLField(default="https://yeenot.today", max_length=200,verbose_name="REFERENCE ON NEWS:") # link to source of news
    count_link_click = models.IntegerField(default=0, blank=True, null=True, help_text='count of clicks to news link')
    count_details_view = models.IntegerField(default=0, blank=True, null=True, help_text='count of views of news detail')
    #share counters:
    cs_gp = models.IntegerField(default=0, blank=True, null=True, help_text='Count of clicks to Share news on Goggle Plus')
    cs_tw = models.IntegerField(default=0, blank=True, null=True, help_text='count of clicks to share news on twitter')
    cs_tg = models.IntegerField(default=0, blank=True, null=True, help_text='count of clicks to share news on telegram')
    cs_rd = models.IntegerField(default=0, blank=True, null=True, help_text='count of clicks to share news on reddit')
    cs_fb = models.IntegerField(default=0, blank=True, null=True, help_text='count of clicks to share news on facebook')
    cs_po = models.IntegerField(default=0, blank=True, null=True, help_text='count of clicks to share news on pocket')
    cs_ln = models.IntegerField(default=0, blank=True, null=True, help_text='count of clicks to share news on linkedin')
    cs_sum= models.IntegerField(default=0, blank=True, null=True, help_text='count of clicks to share news on all social')
	
    time = models.DateTimeField(default=timezone.now) #set time of add news
    proof_image = models.ImageField(upload_to='news_images/', max_length=100, blank=True,verbose_name="SCREENSHOT OF THE NEWS" ) #image of proof height_field=200, width_field=200
    MODERATE_STATUS = (
        ('a', 'Added and sended for moderate'),
        ('p', 'Approved for view'),
        ('d', 'Deleted from view'),
    )
    moderation_status = models.CharField(max_length=1, choices=MODERATE_STATUS, blank=True, default='a', help_text='Moderation status of news')
    PROMO_STATUS = (
        ('n', 'No promo'),
        ('y', 'Promoted'),
    )
    promo_status = models.CharField(max_length=1, choices=PROMO_STATUS, blank=True, default='n', help_text='Promotion status of news')
    DIRECTION = (
        ('b', 'Buy'),
        ('s', 'Sell'),
	#	('h', 'HODL'),
    )
    direction = models.CharField(max_length=1, choices=DIRECTION, blank=True, default='b', verbose_name='DIRECTION OF TRADE')
    rating = models.DecimalField(default=0.0, blank=True, max_digits=10, decimal_places=2) #rate news up to 99 with store 2 for example 100.02
    
    #timeframe duration forecast prediction:
    TIMEFRAME = ( ('4h', '4 hours'),('1d', '1 day'),('1w', '1 week'),('2w', '2 week'),('3w', '3 week'),('1m', '1 month'), )
    duration = models.CharField(max_length=2, choices=TIMEFRAME, default='1w', verbose_name='DURATION TIME OF FORECAST')
    
    #keys:
    #sourceid = models.ForeignKey('Source', on_delete=models.SET_NULL, null=True)
    sourceid = models.ForeignKey('Source', on_delete=models.SET_DEFAULT, default = 1,verbose_name="SOURCE")
	#SET_DEFAULT
	#Set the ForeignKey to its default value; a default for the ForeignKey must be set.
	#https://docs.djangoproject.com/en/2.0/ref/models/fields/#django.db.models.ForeignKey
    coinid = models.ForeignKey('Coin', on_delete=models.SET_NULL, null=True, verbose_name="COIN")
    class Meta:
        ordering = ["-time"]
		
    def __str__(self):
        return '%s, %s' % (self.newsid, self.title)
        #return self.title
    def get_absolute_url(self):#        Returns the url to access a particular news instance.
        return reverse('news-detail', args=[str(self.newsid)])
    def get_like_url(self):
        return reverse('news-like', args=[str(self.newsid)])
    def get_dislike_url(self):
        return reverse('news-dislike', args=[str(self.newsid)])
    def get_change_view(self):
        return reverse('change-view', args=[str(self.newsid)])
    def short_text(self):
        return truncatechars(self.text, 50)
#voting:
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="user_posts")
    coinprice = models.DecimalField(default=0, max_digits=20, decimal_places=8, help_text="price of coin when news create")
    #votes = models.IntegerField(default = 0)
    #нужно переделать: (сделать отдельную таблицу vote с состояниями: newsid, like(0,1), userid)
    like = models.IntegerField(default=0, blank=True, help_text='likes for new')
    dislike = models.IntegerField(default=0, blank=True, help_text='likes for new')

    def vote_like(self, user):
        try:
            self.news_votes.create(user=user, news=self.newsid, vote_type="like")
            self.like += 1
            self.save()                
        except Exception:#IntegrityError:
            return 'already_like'
        return 'ok'

    def vote_dislike(self, user):
        try:
            self.news_votes.create(user=user, news=self.newsid, vote_type="dislike")
            self.dislike += 1
            self.save()                
        except Exception:#IntegrityError:
            return 'already_dislike'
        return 'ok'		
		
class UserVotes(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="user_votes")
    news = models.ForeignKey(News, on_delete=models.SET_NULL, null=True, related_name="news_votes")
    vote_type = models.CharField(max_length=10)
    vote_time = models.DateTimeField(default=timezone.now) #set time of like/dislike
    vote_rate = models.DecimalField(default=0.0, blank=True, max_digits=10, decimal_places=2, help_text='rate of vote')
    vote_rate_status = models.BooleanField(default=False, blank=True, help_text='status of recalculation. If True - not change by rate_users.')
	
    class Meta:
        unique_together = ('user', 'news', 'vote_type') #index for all votes
		
class Source(models.Model):
    sourceid = models.AutoField(primary_key=True, help_text="source id")
    name = models.CharField(max_length=100,help_text="name of source/channel")
    text = models.TextField(default='', max_length=1000,help_text="description of source")
    telegram = 	models.URLField(blank=True, max_length=100) # link to source channel (telegram channel)
    link =  models.URLField(default="https://yeenot.today", max_length=100) # link to source channel (site)
    rating = models.DecimalField(default=0.0, blank=True, max_digits=10, decimal_places=2) #rate source up to 99 with store 2 for example 100.02
    stats_max      = models.DecimalField(default=0.0, blank=True, max_digits=10, decimal_places=2, help_text='maximum rating of news from source') 
    stats_min      = models.DecimalField(default=0.0, blank=True, max_digits=10, decimal_places=2, help_text='minimum rating of news from source') 
    stats_sum      = models.DecimalField(default=0.0, blank=True, max_digits=10, decimal_places=2, help_text='sum of  rating of news from source') 
    stats_avg      = models.DecimalField(default=0.0, blank=True, max_digits=10, decimal_places=2, help_text='average rating of news from source') 
    #stats_median   = models.DecimalField(default=0.0, blank=True, max_digits=10, decimal_places=2, help_text='median  rating of news from source') 
    stats_likes    = models.IntegerField(default=0, blank=True, help_text='sum of likes all news from source')
    stats_dislikes = models.IntegerField(default=0, blank=True, help_text='sum of dislikes all news from source')
	#stats: news_count_all
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="user_sources") #owner(manager) of added Source
	
    MODERATE_STATUS = (
        ('a', 'Added and sended for moderate'),
        ('p', 'Approved for view without owner'),
        ('o', 'Approved for view with owner'),
        ('d', 'Deleted from view'),
    )
    moderation_status = models.CharField(max_length=1, choices=MODERATE_STATUS, blank=True, default='a', help_text='Moderation status of source')
    PROMO_STATUS = (
        ('n', 'No promo'),
        ('y', 'Promoted'),
    )
    promo_status = models.CharField(max_length=1, choices=PROMO_STATUS, blank=True, default='n', help_text='Promotion status of source')
    
    def __str__(self):
        return self.name
    def get_absolute_url(self):#        Returns the url to access a particular source instance.
        return reverse('source-detail', args=[str(self.sourceid)])

class Banner(models.Model):
	id = models.AutoField(primary_key=True, help_text="banner id")
	image = models.ImageField(upload_to='banner_images/', max_length=100) # !!!! need size , height_field=300, width_field=400
	title = models.CharField(max_length=20)
	text = models.TextField(max_length=100,help_text="description of banner")
	link = models.URLField(max_length=100)
	count_view = models.IntegerField(default=0, blank=True, null=True, help_text='count of views')
	count_click = models.IntegerField(default=0, blank=True, null=True, help_text='count of clicks to link')
	status = models.BooleanField(default=False, blank=True, help_text='status of promo - enabled, disabled')
	#time_from = 
	#time_to = 
	#priority = 
	#max_count_view = 
	#max_count_click = 
	PLACE_NAME = (
        ('t', 'Top horizontal'),
        ('l', 'Under Top on Left'),
        ('r', 'Under Top on Right'),
        ('4', 'NewsDetails on Left'),
        ('5', 'NewsDetails on Right'),
    )
	place = models.CharField(max_length=1, choices=PLACE_NAME, blank=True, default='t', help_text='Banner place on site')
	def __str__(self):
		return self.title

class Coin(models.Model):
	id = models.AutoField(primary_key=True, help_text="coin id")
	symbol = models.CharField(max_length=10,help_text="coin ticker")
	name = models.CharField(max_length=100)
	price = models.DecimalField(max_digits=20, decimal_places=8, help_text="current price of coin")
	change = models.DecimalField(max_digits=20, decimal_places=8, help_text="change of price 24 hour in perecents")
	volume = models.DecimalField(max_digits=20, decimal_places=8, help_text="total volume in USD")
	mktcap = models.DecimalField(max_digits=20, decimal_places=8, help_text="market cap in USD")
	supply = models.DecimalField(max_digits=20, decimal_places=0, help_text="coin supply", default=0)
	image = models.ImageField(upload_to='coin_images/', max_length=100, blank=True)
	#from cryptocompare coinlist
	Algorithm = models.CharField(max_length=40,default='',help_text="Algorithm from cryptocompare")
	ProofType = models.CharField(max_length=40,default='',help_text="ProofType from cryptocompare")
	#SortOrder = models.IntegerField(default=0,help_text='SortOrder from cryptocompare')
	TotalCoinSupply = models.CharField(max_length=40,default='',help_text="TotalCoinSupply from cryptocompare")
	#TotalCoinSupply = models.DecimalField(max_digits=20, decimal_places=0,help_text="TotalCoinSupply from cryptocompare", default=0)
	supply_share = models.DecimalField(max_digits=20, decimal_places=3, help_text="coin supply share", default=1)
	Id_cc = models.IntegerField(default=0,help_text='ID for cryptocompare calls')
	updatetime = models.DateTimeField(auto_now=True, help_text='last time data save')
	news_count = models.IntegerField(default=0,help_text='count of news on yeenot for coin')
	ath = models.DecimalField(max_digits=20, decimal_places=8, help_text="all time high price of coin", default=0)
	athdate = models.DateField(help_text='date of ATH', default=timezone.now)
	athchange = models.DecimalField(max_digits=20, decimal_places=8, help_text="price/ath if ath>0", default=0)
	volatility30day = models.DecimalField(max_digits=20, decimal_places=8, help_text="30 day volatility from daily DOHLCV in %", default=0)
	volatility7day =  models.DecimalField(max_digits=20, decimal_places=8, help_text="7 day volatility from daily DOHLCV in %", default=0)
	
	class Meta:
		ordering = ["-volume"]
		
	def __str__(self):
		return self.symbol

#https://www.cryptocompare.com/api
#https://www.cryptocompare.com/api/data/coinsnapshotfullbyid/?id=1182 //for BTC
#https://www.cryptocompare.com/api/data/socialstats/?id=1182 //for BTC
class CoinCryptocompare(models.Model):
	Id_cc = models.IntegerField(default=0,help_text='Id for cryptocompare calls')
	#from coinsnapshotfullbyid ['Data']['General']
	symbol = models.CharField(max_length=10, help_text='symbol from coinsnapshot')
	name = models.CharField(max_length=100, help_text='name from coinsnapshot')
	Description = models.TextField(help_text='Description from coinsnapshot')
	WebsiteUrl = models.URLField(default='', max_length=100, help_text='WebsiteUrl from coinsnapshot')
	StartDate = models.DateField(help_text='StartDate from coinsnapshot') #example cloak: "04/05/2014" date(year, month, day) default=timezone.now
	#!blockchain info (later)
	#!ico info (later)
	#social info:
	twitter_link = models.URLField(default='', max_length=100, help_text='Twitter url from socialstats')
	twitter_followers = models.IntegerField(default=0,help_text='Twitter followers from socialstats')
	twitter_posts = models.IntegerField(default=0,help_text='Twitter statuses from socialstats')
	reddit_link = models.URLField(default='', max_length=100, help_text='Reddit url from socialstats')
	reddit_subscribers = models.IntegerField(default=0,help_text='Reddit subscribers from socialstats')
	reddit_active_users = models.IntegerField(default=0,help_text='Reddit active_users from socialstats')
	reddit_posts_per_day = models.DecimalField(max_digits=10, decimal_places=2, default=0,help_text='Reddit posts/day from socialstats')
	reddit_comments_per_day = models.DecimalField(max_digits=10, decimal_places=2, default=0,help_text='Reddit comments/day from socialstats')
	def short_description(self):
		return truncatechars(self.Description, 50)

import json

class Exchange(models.Model):
	exchange = models.CharField(max_length=20, help_text='name of exchange')
	coinlist = models.CharField(max_length=10000, help_text='list of coins symbol')
	coinlist_update = models.CharField(max_length=1000, help_text='list of new coins symbol')
	count = models.IntegerField(default=0,help_text='count of coins')

	def set_coinlist(self, x):
		self.coinlist = json.dumps(x)

	def get_coinlist(self):
		return json.loads(self.coinlist)
	
	class Meta:
		ordering = ["exchange"]
		
class CoinGecko(models.Model):
	#coinid = models.ForeignKey(Coin, unique=True, on_delete=models.CASCADE, null=True, verbose_name="COIN", related_name="coin_gecko")
	coinid = models.OneToOneField(Coin, on_delete=models.CASCADE, null=True, verbose_name="COIN", related_name="coin_gecko")
	coinidname = models.CharField(max_length=100, default='', help_text='name from model Coin')
	symbol = models.CharField(max_length=10, help_text='coingecko symbol')
	name = models.CharField(max_length=100, help_text='coingecko name')
	geckoid = models.CharField(max_length=100, help_text='coingecko id')
	#marketdata:
	p24h = models.DecimalField(max_digits=20, decimal_places=8, default=0)
	p7d  = models.DecimalField(max_digits=20, decimal_places=8, default=0)
	p14d = models.DecimalField(max_digits=20, decimal_places=8, default=0)
	p30d = models.DecimalField(max_digits=20, decimal_places=8, default=0)
	circulating_supply=models.DecimalField(max_digits=20, decimal_places=0, default=0)
	coingecko_score = models.DecimalField(max_digits=6, decimal_places=3, default=0)
	current_price = models.DecimalField(max_digits=20, decimal_places=8, default=0)
	market_cap = models.DecimalField(max_digits=20, decimal_places=8, default=0)
	total_volume = models.DecimalField(max_digits=20, decimal_places=8, default=0)
	
	def __str__(self):
		return self.geckoid
		
class YeenotSettings(models.Model):
	name = models.CharField(max_length=30)
	#text_value = models.CharField(max_length=20, help_text="text value of settings")
	num_value = models.DecimalField(default=0.0, blank=True, max_digits=20, decimal_places=8, help_text="digital value of settings")

class Promo_task(models.Model):
	user     = models.ForeignKey(User,   on_delete=models.SET_NULL, null=True, blank=True, related_name="user_promo") #owner(manager) of Promo_task
	newsid   = models.ForeignKey(News,   on_delete=models.SET_NULL, null=True, blank=True , verbose_name="NEWS")
	sourceid = models.ForeignKey(Source, on_delete=models.SET_NULL, null=True, blank=True , verbose_name="SOURCE")
	bannerid = models.ForeignKey(Banner, on_delete=models.SET_NULL, null=True, blank=True , verbose_name="BANNER")
	TYPE_NAME = (
	     
        ('n', 'News promo'),
        ('s', 'Source promo'),
        ('b', 'Banner promo'),
    )
	type = models.CharField(max_length=1, choices=TYPE_NAME, blank=True, help_text='Type of promo task')
	STATUS_NAME = (
        ('o', 'Ordered'),
        ('p', 'Paid'),
        ('l', 'Launched'),
		('c', 'Completed'),
    )
	status = models.CharField(max_length=1, choices=STATUS_NAME, blank=False, default='o', help_text='Status of promo task')
	PARAM_NAME = (
        ('d', 'Day'),
        ('w', 'Week'),
        ('m', 'Month'),
    )
	#param - for example duration or clicks or views (news - no, source - duration week or month, banner - duration week or month)
	param = models.CharField(max_length=1, choices=PARAM_NAME, blank=False, default='w', help_text='Parameters of promo task')
	#price -calculated in USD (need calculator in views.addpromo)
	price = models.DecimalField(max_digits=20, decimal_places=2, help_text='price of promo task calculated after promo added')
	time = models.DateTimeField(default=timezone.now, help_text='time after promo task added')
	
	def user_email(self):
		try:
			return self.user.email
		except:
			return None

'''
News:
 !newsid
 !sourceid
 !user
 !coinid
 text
 direction
 title - optional
 link
proof_image (нужно разобраться с defautl и storage)
 !time
 !rating
 moderation_status
 promo_status
promo_time_till
like
dislike

news methods:
ок addnews
ок listnews
ок likenews
ок dislikenews
approvwnews moderator
ок removenews
ок changenews
ок ratenews

Source (channel of news):
 !sourceid
 name
 text
 user
 link
 !rating
logo
 moderation_status
 promo_status
promo_time_till
description
telegram_channel_url
telegram_channel_users

user:
!userid
 !username
 !email
!passwordhash
lasttimesignin
!signin_status
logo
eth_address
verify_status

coin:
coinid
name (Bitcoin)
shotname (BTC)
price_current
price_daily[] - 24 hours
price_daychange (p2/p1)
promo_status

'''