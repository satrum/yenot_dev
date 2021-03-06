from django.contrib import admin

# Register your models here.
#from .models import Author, Genre, Book, BookInstance, Language

#admin.site.register(Book)
#admin.site.register(Author)
##admin.site.register(Genre)
#admin.site.register(BookInstance)
##admin.site.register(Language)

'''
# Define the admin class
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name', 'date_of_birth', 'date_of_death')
    fields = ['first_name', 'last_name', ('date_of_birth', 'date_of_death')]
'''

# Register the admin class with the associated model
##admin.site.register(Author, AuthorAdmin)
'''
class BooksInstanceInline(admin.TabularInline):
    model = BookInstance
'''
'''
# Register the Admin classes for Book using the decorator
@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'display_genre')
    inlines = [BooksInstanceInline]
'''
'''	
# Register the Admin classes for BookInstance using the decorator
@admin.register(BookInstance) 
class BookInstanceAdmin(admin.ModelAdmin):
    list_display = ('book', 'status', 'borrower', 'due_back', 'id')
    list_filter = ('status', 'due_back')
    fieldsets = (
        (None, {
            'fields': ('book','imprint', 'id')
        }),
        ('Availability', {
            'fields': ('status', 'due_back', 'borrower')
        }),
    )
'''
#-------------------------
#ENOT
from .models import News, Source, UserVotes, Profile, Banner, Coin, YeenotSettings, Promo_task, CoinCryptocompare, Exchange, CoinGecko

#admin.site.register(News)
@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ('newsid', 'title', 'direction', 'duration', 'coinid', 'coinprice', 'short_text', 'time', 'link', 'rating', 'sourceid','like','dislike','user','moderation_status', 'promo_status', 'proof_image','count_link_click', 'count_details_view','cs_sum','cs_gp','cs_tw','cs_tg','cs_rd','cs_fb','cs_po','cs_ln')
    list_filter = ('direction', 'duration', 'moderation_status', 'promo_status', 'time', 'sourceid')
    #fields = [('title', 'direction'), 'text', 'link'] надо сделать разное для add и change, и в зависимости от прав пользователя
    search_fields = ['newsid','title','text','coinid__symbol','sourceid__name']
    
    def make_moderated(self, request, queryset):
        queryset.update(moderation_status='p') #'Approved for view'
    
    make_moderated.short_description = 'make news moderation status - Approved for view'
    actions = [make_moderated]
	
class NewsInline(admin.TabularInline):
    model = News
	
@admin.register(Source)
class SourceAdmin(admin.ModelAdmin):
    list_display = ('sourceid', 'name', 'link', 'rating', 'text', 'telegram', 'moderation_status', 'promo_status', 'user', 'stats_likes', 'stats_dislikes', 'stats_max', 'stats_min', 'stats_sum', 'stats_avg')
    list_filter = ('moderation_status', 'promo_status')
    inlines = [NewsInline]

@admin.register(UserVotes)
class UserVotesAdmin(admin.ModelAdmin):
	list_display = ('id', 'user','news','vote_type', 'vote_time', 'vote_rate', 'vote_rate_status')
	list_filter = ('vote_type', 'user', 'vote_time', 'vote_rate_status', 'news')

@admin.register(Profile)
class UserProfileAdmin(admin.ModelAdmin):
	list_display = ('user','bio','location', 'birth_date', 'view_newslist_block', 'sum_all', 'sum_positive', 'sum_today', 'sum_today_positive','sum_likes','sum_dislikes', 'sum_right', 'point', 'rank', 'sum_news', 'sum_news_rating')
	list_filter = ('user', 'location', 'view_newslist_block')

@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'text', 'link', 'count_view', 'count_click', 'status', 'image', 'place')
    list_filter = ('status', 'place')


@admin.register(Coin)
class CoinAdmin(admin.ModelAdmin):
    list_display = ('id', 'symbol', 'name', 'price', 'change', 'volume', 'mktcap', 'ath', 'athdate', 'athchange', 'volatility30day', 'volatility7day', 'supply','TotalCoinSupply','supply_share','Algorithm','ProofType','Id_cc','news_count','updatetime','image')
    search_fields = ['symbol','name']
    list_filter = ('Algorithm', 'ProofType')
    inlines = [NewsInline]

@admin.register(CoinCryptocompare)
class CoinCryptocompareAdmin(admin.ModelAdmin):
	list_display = ('Id_cc','symbol','name','short_description','WebsiteUrl','StartDate', 'twitter_link', 'twitter_followers', 'twitter_posts', 'reddit_link', 'reddit_subscribers', 'reddit_active_users','reddit_posts_per_day','reddit_comments_per_day')
	search_fields = ['symbol','name','WebsiteUrl','twitter_link','reddit_link','Id_cc']
	
@admin.register(Exchange)
class ExchangeAdmin(admin.ModelAdmin):
	list_display = ('exchange','count','coinlist','coinlist_update')
	search_fields = ['exchange','coinlist']

@admin.register(CoinGecko)
class CoinGeckoAdmin(admin.ModelAdmin):
	list_display = ('coinid','coinidname','symbol','name','geckoid','coingecko_score','p24h','p7d','p14d','p30d','current_price','market_cap','total_volume','circulating_supply')
	search_fields = ['coinidname','symbol','name','geckoid']
	list_max_show_all = 2000
	list_per_page = 200
	
@admin.register(YeenotSettings)
class YeenotSettingsAdmin(admin.ModelAdmin):
	list_display = ('id', 'name', 'num_value')

@admin.register(Promo_task)
class PromotaskAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'user_email', 'newsid', 'sourceid', 'bannerid', 'type', 'status', 'param', 'price', 'time')