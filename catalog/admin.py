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
from .models import News, Source, UserVotes, Profile, Banner, Coin, YeenotSettings, Promo_task

#admin.site.register(News)
@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ('newsid', 'title', 'direction', 'duration', 'coinid', 'coinprice', 'short_text', 'time', 'link', 'rating', 'sourceid','like','dislike','user','moderation_status', 'promo_status', 'proof_image','count_link_click')
    list_filter = ('direction', 'duration', 'moderation_status', 'promo_status', 'time', 'sourceid')
    #fields = [('title', 'direction'), 'text', 'link'] надо сделать разное для add и change, и в зависимости от прав пользователя
    search_fields = ['newsid','title','text','coinid__symbol','sourceid__name']
	
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
	list_display = ('user','bio','location', 'birth_date', 'view_newslist_block', 'sum_all', 'sum_positive', 'sum_today', 'sum_today_positive','sum_likes','sum_dislikes', 'sum_right', 'point', 'rank')
	list_filter = ('user', 'location', 'view_newslist_block')

@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'text', 'link', 'count_view', 'count_click', 'status', 'image', 'place')


@admin.register(Coin)
class CoinAdmin(admin.ModelAdmin):
    list_display = ('id', 'symbol', 'name', 'price', 'change', 'volume', 'mktcap', 'image') #
    search_fields = ['symbol','name']
    inlines = [NewsInline]

@admin.register(YeenotSettings)
class YeenotSettingsAdmin(admin.ModelAdmin):
	list_display = ('id', 'name', 'num_value')

@admin.register(Promo_task)
class PromotaskAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'user_email', 'newsid', 'sourceid', 'bannerid', 'type', 'status', 'param', 'price', 'time')