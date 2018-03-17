from django.db import models
from django.contrib.auth.models import User #for voting in News, UserVotes and BookInstance

# Create your models here.
class Genre(models.Model):
    name = models.CharField(max_length=200, help_text="Enter a book genre (e.g. Science Fiction, French Poetry etc.)")
    def __str__(self):
        return self.name

from django.urls import reverse #Used to generate URLs by reversing the URL patterns

class Language(models.Model):#Model representing a Language (e.g. English, French, Japanese, etc.)
    name = models.CharField(max_length=200, help_text="Enter a the book's natural language (e.g. English, French, Japanese etc.)")
    
    def __str__(self):#String for representing the Model object (in Admin site etc.)
        return self.name

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

import uuid # Required for unique book instances
from datetime import date #property that we can call from our templates to tell if a particular book instance is overdue.

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

class Author(models.Model):#Model representing an author.
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField(null=True, blank=True)
    date_of_death = models.DateField('Died', null=True, blank=True)
    
    def get_absolute_url(self):#Returns the url to access a particular author instance.
        return reverse('author-detail', args=[str(self.id)])

    def __str__(self):
        return '%s, %s' % (self.last_name, self.first_name)

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

class News(models.Model):
    newsid = models.AutoField(primary_key=True, help_text="news id")
    text = models.TextField(max_length=1000,help_text="description of news")
    title = models.CharField(max_length=100) # резервирую название на будущее, для сигналов нет
    link =  models.URLField(default="https://enot.channel", max_length=100) # link to source of news
    time = models.DateTimeField(default=timezone.now) #set time of add news
    proof_image = models.ImageField(upload_to='news_images/', max_length=100, blank=True ) #image of proof height_field=200, width_field=200
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
		('h', 'HODL'),
    )
    direction = models.CharField(max_length=1, choices=DIRECTION, blank=True, default='b', help_text='Direction of trade')
    rating = models.DecimalField(default=0.0, blank=True, max_digits=10, decimal_places=2) #rate news up to 99 with store 2 for example 100.02
    
    #timeframe duration forecast prediction:
    TIMEFRAME = ( ('4h', '4 hours'),('1d', '1 day'),('1w', '1 week'), )
    duration = models.CharField(max_length=2, choices=TIMEFRAME, default='1w', help_text='signal forecast duration')
    
    #keys:
    #sourceid = models.ForeignKey('Source', on_delete=models.SET_NULL, null=True)
    sourceid = models.ForeignKey('Source', on_delete=models.SET_DEFAULT, default = 1)
	#SET_DEFAULT
	#Set the ForeignKey to its default value; a default for the ForeignKey must be set.
	#https://docs.djangoproject.com/en/2.0/ref/models/fields/#django.db.models.ForeignKey
    coinid = models.ForeignKey('Coin', on_delete=models.SET_NULL, null=True)
    class Meta:
        ordering = ["time"]
		
    def __str__(self):
        return '%s, %s' % (self.newsid, self.title)
    def get_absolute_url(self):#        Returns the url to access a particular news instance.
        return reverse('news-detail', args=[str(self.newsid)])
    def get_like_url(self):
        return reverse('news-like', args=[str(self.newsid)])
    def get_dislike_url(self):
        return reverse('news-dislike', args=[str(self.newsid)])
    def get_change_view(self):
        return reverse('change-view', args=[str(self.newsid)])
#voting:
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="user_posts")
    coinprice = models.DecimalField(default=0, max_digits=20, decimal_places=8, help_text="price of coin when news create")
    #votes = models.IntegerField(default = 0)
    #нужно переделать: (сделать отдельную таблицу vote с состояниями: newsid, like(0,1), userid)
    like = models.IntegerField(default=0, blank=True, help_text='likes for new')
    dislike = models.IntegerField(default=0, blank=True, help_text='likes for new')

    def vote_like(self, user):
        try:
            self.news_votes.create(user=user, news=self, vote_type="like")
            self.like += 1
            self.save()                
        except Exception:#IntegrityError:
            return 'already_like'
        return 'ok'

    def vote_dislike(self, user):
        try:
            self.news_votes.create(user=user, news=self, vote_type="dislike")
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

    class Meta:
        unique_together = ('user', 'news', 'vote_type') #index for all votes
		
class Source(models.Model):
    sourceid = models.AutoField(primary_key=True, help_text="source id")
    name = models.CharField(max_length=100,help_text="name of source/channel")
    text = models.TextField(default='', max_length=1000,help_text="description of source")
    telegram = 	models.URLField(blank=True, max_length=100) # link to source channel (telegram channel)
    link =  models.URLField(default="https://enot.channel", max_length=100) # link to source channel (site)
    rating = models.DecimalField(default=0.0, blank=True, max_digits=10, decimal_places=2) #rate source up to 99 with store 2 for example 100.02
    stats_max      = models.DecimalField(default=0.0, blank=True, max_digits=10, decimal_places=2, help_text='maximum rating of news from source') 
    stats_min      = models.DecimalField(default=0.0, blank=True, max_digits=10, decimal_places=2, help_text='minimum rating of news from source') 
    stats_sum      = models.DecimalField(default=0.0, blank=True, max_digits=10, decimal_places=2, help_text='sum of  rating of news from source') 
    stats_avg      = models.DecimalField(default=0.0, blank=True, max_digits=10, decimal_places=2, help_text='average rating of news from source') 
    #stats_median   = models.DecimalField(default=0.0, blank=True, max_digits=10, decimal_places=2, help_text='median  rating of news from source') 
    stats_likes    = models.IntegerField(default=0, blank=True, help_text='sum of likes all news from source')
    stats_dislikes = models.IntegerField(default=0, blank=True, help_text='sum of dislikes all news from source')
	#stats: news_count_all
	
	#owner = models.ForeignKey('User', on_delete=models.SET_NULL, null=True)
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
	count_click = models.IntegerField(default=0, blank=True, null=True, help_text='count of views')
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
    )
	place = models.CharField(max_length=1, choices=PLACE_NAME, blank=True, default='t', help_text='Banner place on site')

class Coin(models.Model):
	id = models.AutoField(primary_key=True, help_text="coin id")
	symbol = models.CharField(max_length=10,help_text="coin ticker")
	name = models.CharField(max_length=100)
	price = models.DecimalField(max_digits=20, decimal_places=8, help_text="current price of coin")
	change = models.DecimalField(max_digits=20, decimal_places=8, help_text="change of price 24 hour in perecents")
	volume = models.DecimalField(max_digits=20, decimal_places=8, help_text="total volume in USD")
	mktcap = models.DecimalField(max_digits=20, decimal_places=8, help_text="market cap in USD")
	image = models.ImageField(upload_to='coin_images/', max_length=100, blank=True)
	
	class Meta:
		ordering = ["-volume"]
		
	def __str__(self):
		return self.symbol

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
addnews
listnews
likenews
dislikenews
approvwnews
removenews
changenews
ratenews

Source (channel of news):
 !sourceid
 name
 text
owner
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