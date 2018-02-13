import os,sys
print(os.getcwd())
print(sys.argv)

#get news ratings:

from catalog.models import News
news = News.objects.all()
print(type(news), news)
for new in news:
    print(new.newsid, new.title, new.rating, new.like, new.dislike)

