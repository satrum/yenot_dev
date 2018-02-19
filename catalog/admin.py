from django.contrib import admin

# Register your models here.
from .models import Author, Genre, Book, BookInstance,Language

#admin.site.register(Book)
#admin.site.register(Author)
admin.site.register(Genre)
#admin.site.register(BookInstance)
admin.site.register(Language)

# Define the admin class
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name', 'date_of_birth', 'date_of_death')
    fields = ['first_name', 'last_name', ('date_of_birth', 'date_of_death')]

# Register the admin class with the associated model
admin.site.register(Author, AuthorAdmin)

class BooksInstanceInline(admin.TabularInline):
    model = BookInstance

# Register the Admin classes for Book using the decorator
@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'display_genre')
    inlines = [BooksInstanceInline]
	
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

#-------------------------
#ENOT
from .models import News, Source, UserVotes, Profile, Banner, Coin

#admin.site.register(News)
@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ('newsid', 'title', 'direction', 'coinid', 'text', 'time', 'link', 'rating', 'sourceid','like','dislike','user','moderation_status', 'promo_status', 'proof_image')
    list_filter = ('direction', 'moderation_status', 'promo_status', 'time', 'coinid')
    #fields = [('title', 'direction'), 'text', 'link'] надо сделать разное для add и change, и в зависимости от прав пользователя

class NewsInline(admin.TabularInline):
    model = News
	
@admin.register(Source)
class SourceAdmin(admin.ModelAdmin):
    list_display = ('sourceid', 'name', 'link', 'rating', 'text', 'telegram', 'moderation_status', 'promo_status')
    list_filter = ('moderation_status', 'promo_status')
    inlines = [NewsInline]

@admin.register(UserVotes)
class UserVotesAdmin(admin.ModelAdmin):
	list_display = ('user','news','vote_type', 'vote_time')
	list_filter = ('vote_type', 'user', 'news', 'vote_time')

@admin.register(Profile)
class UserProfileAdmin(admin.ModelAdmin):
	list_display = ('user','bio','location', 'birth_date', 'view_newslist_block')
	list_filter = ('user', 'location', 'view_newslist_block')

@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'text', 'link', 'count_view', 'count_click', 'status', 'image') #


@admin.register(Coin)
class CoinAdmin(admin.ModelAdmin):
    list_display = ('id', 'symbol', 'name', 'price', 'change', 'volume', 'mktcap', 'image') #
