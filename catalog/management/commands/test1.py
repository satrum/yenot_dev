#update_news_rating_test1
import os,sys
# print(os.getcwd())
# print(sys.argv)
from django.core.management.base import BaseCommand, CommandError
from catalog.models import News

class Command(BaseCommand):
	
	# def add_arguments(self, parser):
	# 	parser.add_argument('poll_id', nargs='+', type=str)
	
	def handle(self, *args, **options):
		# try:
		# 	print('arguments exists:')
		# 	for poll_id in options['poll_id']:
		# 		print(poll_id)
		# except Exception:
		# 	print('no arguments')

		#system:
		print(os.getcwd()) #c:\WORK\Docs\python\web\locallibrary
		print(sys.argv)

		#get news ratings:
		news = News.objects.all()
		#print(type(news), news)
		for new in news:
	   		print(new.newsid, new.title, new.rating, new.like, new.dislike, new.time)





