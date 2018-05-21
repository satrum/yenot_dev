#update_news_rating_test1
#C:\WORK\Docs\python\web\locallibrary

#API
#https://min-api.cryptocompare.com/stats/rate/limit - my limits
#Hour limit - 150000, Minute limit - 1000, Second limit - 50


import os,sys
# print(os.getcwd())
# print(sys.argv)
from django.core.management.base import BaseCommand, CommandError
from catalog.models import News, Coin, Source, UserVotes, Profile, YeenotSettings
from django.contrib.auth.models import User

import requests
import json
import os
from statistics import median

FILE_COINLIST = 'coinlist.txt'
FILE_PRICE = 'coinpricefull.txt'
FILE_RESULT = 'result.txt'
FILE_RESULT_RATE_USERS = 'result_rate_users.txt'
TYPE_PRICE = 'full'
DATADIR = 'data'
COINIMAGESDIR = 'media/coin_images/'
RATING_MAX_DAYS = 7

EXCLUDE_LIST = ['ARENA','CNO', 'BTH', 'ADL']

#usage: 20.02.2018
#cd c:\WORK\Docs\python\web\locallibrary
#python manage.py test1 coinlist
		#coins: 2189 coins no image: 2
#python manage.py test1 coinprice
#python manage.py test1 coinlist_exclude
		# coins from full price file: 1878
		# coins from full price file with MKTCAP: 1100
		# coins from coinlist file: 2189
		# coins from coinlist file with price: 1100
#python manage.py test1 coinimage
#python manage.py test1 coinadd all
#
#scheduled: coinprice + coinlist_exclude + coinadd update
#python manage.py test1 update_cycle


from django.db import models
from django.utils import timezone
from django.core.mail import send_mail, get_connection
from datetime import datetime, timedelta
from django.db.models import Avg, Max, Min, Sum

#email:
SMTP_EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
CONSOLE_EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
EMAIL_PORT = 587
EMAIL_USE_TLS = True


class Command(BaseCommand):

	def add_arguments(self, parser):
		parser.add_argument('poll_id', nargs='+', type=str)
	
	def help(self):
		print('parameters:')
		print('help - print this help')
		#print('list_news - print list of all news')
		print('rate_news - calculate rating of news. Likes(Real)/Dislikes(Fake)/News_price/Current_price/Direction/1DAY -> rating')
		print('rate_sources - calculate stats for sources from news rating. News Rating -> Source.stats')
		print('coinlist [filename=''coinlist.txt''] - get coin list from cryptocompare and write json to file')
		print('coinprint [filename=''coinlist.txt''] - read json from file and print ')
		print('coinprice [filename coinlist.txt] [filename coinpricefull.txt] [simple/full] - read json from file and get price and write json to file')
		print('coinlist_exclude - read full price, get coins with price, remove coins without from coinlist')
		print('coinimage - read from coinlist and update folder media/coin_images/ with images') #!!!!!!!
		print('coininfo [symbol] - read info about coin')
		print('coinadd [action - all, update, add]- read coinlist from file and update list on db model Coin - coin.id, coin.symbol, coin.name')
		print('update_cycle - coinprice + coinlist_exclude + coinadd update + rate_news + rate_sources')
		print('coinprint_db - list info from Model Coin')
		print('get_price [symbol default=BTC]')
		print('--------need create or update:-----')
		print('coinpriceupdate - update fields in Model Coin - coin.price, coin.change, coin.volume, coin.mktcap')
		print('full_cycle - coinlist + coinprice + coinlist_exclude + coinimage + coinadd full')
		print('coinhistory - get price history for coins in news and save in files by (day, month, coin)')
		print('random_news [create, delete] random news with title random_news')
		print('sendmail [news] [id] - send all or one news to admin with MODERATE_STATUS = `a` status')
		print('promo - change promo status, see views, clicks, time period, views.py')
		print('rate_users - rate votes and calculate stats about users(profiles)') #!!!!!
		print('update_first_name - read reddit accounts and add first_name to users') #!!!!!


	def rate_news(self):
		#get news ratings:
		news = News.objects.order_by('time')
		#print(type(news), news)
		for new in news:
			#print(new.newsid, new.title, new.rating, new.like, new.dislike, new.time)
			#print(new.newsid, new.title, new.rating, new.like, new.dislike, new.sourceid, new.user, new.coinprice, new.time)
			time = new.time
			curtime = timezone.now()
			delta = curtime-time
			currating = new.rating
			duration = new.duration
			print('id: {} duration: {} delta: {} time: {}'.format(new.newsid, duration, delta, time))
			if duration == '4h':
				time_delta = timedelta(days=0, hours=4, seconds=0)
			elif duration == '1d':
				time_delta = timedelta(days=1, hours=0, seconds=0)
			elif duration == '1w':
				time_delta = timedelta(days=7, hours=0, seconds=0)
			elif duration == '2w':
				time_delta = timedelta(days=14, hours=0, seconds=0)
			elif duration == '3w':
				time_delta = timedelta(days=21, hours=0, seconds=0)
			elif duration == '1m':
				time_delta = timedelta(days=30, hours=0, seconds=0)
			else:
				continue
			#oneday = timedelta(days=RATING_MAX_DAYS, hours=0, seconds=0)
			if time+time_delta<curtime:
				print('more then {}'.format(duration))
				#print(new.newsid, new.title, new.rating, new.like, new.dislike, new.sourceid, new.user, new.coinprice, new.time)
				continue
			else:
			 	curprice = Coin.objects.get(symbol=new.coinid).price
			 	newsprice = new.coinprice
			 	if newsprice == 0:
			 		print('news price is zero, no rate')
			 		#print(new.newsid, new.title, new.rating, new.like, new.dislike, new.sourceid, new.user, new.coinprice, new.time)
			 		continue
			 	p2p1 = curprice/newsprice
			 	decimalp2p1 = int(p2p1*10000)/10000
			 	if new.direction =='b' or new.direction =='h':
			 		rating = new.like*p2p1 - new.dislike/p2p1
			 	else:
			 		rating = new.like/p2p1 - new.dislike*p2p1
			 	rating = int(rating*10000)/10000
			 	likedelta = new.like-new.dislike
			 	new.rating=rating
			 	new.save()
			print(new.newsid, new.coinid, 'time delta:', delta, 'price changed: ',decimalp2p1, new.direction, 'likes:{:<3} dislike:{:<3} delta:{:<3}'.format(new.like,new.dislike,likedelta), 'rating: ',rating)#curprice, newsprice, likedelta
		# setup YeenotSettings with aggregation and update_or_create:
		# https://docs.djangoproject.com/en/2.0/topics/db/aggregation/
		# https://docs.djangoproject.com/en/2.0/ref/models/querysets/#update-or-create
		agg_value = news.aggregate(num_value = models.Max('rating')) #{'num_value': Decimal('41.74')}
		obj, created = YeenotSettings.objects.update_or_create(name='news_rate_max',defaults=agg_value)
		print(obj.id, obj.num_value, created)
		agg_value_2 = news.aggregate(num_value = models.Min('rating')) #{'num_value': Decimal('41.74')}
		obj, created = YeenotSettings.objects.update_or_create(name='news_rate_min',defaults=agg_value_2)
		print(obj.id, obj.num_value, created)
			


	# if news.rating == 0 - exclude
	def rate_sources(self):
		sources = Source.objects.all()
		for source in sources:
			news = News.objects.filter(sourceid=source.sourceid)
			#print(source, source.sourceid, news.count())
			likes = 0
			dislikes = 0
			minimum = 0
			maximum = 0
			count = 0
			summa = 0 
			#array = []
			for new in news:
				likes+=new.like
				dislikes+=new.dislike
				rate = new.rating
				if rate != 0:
					count+=1
					if rate>maximum: maximum=rate
					if rate<minimum: minimum=rate
					summa+=rate
					#array.append(rate)

			source.stats_likes = likes
			source.stats_dislikes = dislikes
			source.stats_max = maximum
			source.stats_min = minimum
			source.stats_sum = summa
			if count>0:
				source.stats_avg = avg = summa/count
				#source.stats_median = med = median(array)
			else:
				source.stats_avg = avg = 0
				#source.stats_median = med = 0
			# rating of source = average rating on source's news with rate<>0
			source.rating = avg 
			source.save()
			#print('id:{} news:{:<3} likes:{:<3} dislikes:{:<3} max:{:<5} min:{:<5} sum:{:<5} avg:{:<5} name: {}'.format(source.sourceid, news.count(), likes, dislikes, maximum, minimum, summa, avg, source))
			print('id:{} news:{:<3} likes:{:<3} dislikes:{:<3} max:{:<5} min:{:<5} sum:{:<5} avg:{:<5}'.format(source.sourceid, news.count(), likes, dislikes, maximum, minimum, summa, avg))

	def rate_users(self):
		#users = User.objects.all()
		profiles = Profile.objects.all()
		#votes = UserVotes.objects.all()
		votes = UserVotes.objects.filter(vote_rate_status=False)
		#print(users)
		#print(profiles)
		# for user in users:
		# 	profile = Profile.objects.get(user=user)
		# 	print('{} {}'.format(profile.user,profile.view_newslist_block))
		stats_votes_false=votes.count()
		stats_profiles=profiles.count()
		stats_votes_chenged = 0 # count of calculated votes
		for vote in votes:
			if vote.vote_rate_status == True: # news duration ended or vote after news ended
				print('vote {} - news duration ended or vote after news ended, rate: {}'.format(vote.id, vote.vote_rate))
				continue
			#print(vote.news)
			new_rate = vote.news.rating
			direction = vote.news.direction #not used
			duration = vote.news.duration
			if duration == '4h':
				dur_time = timedelta(hours=4)
			elif duration == '1d':
				dur_time = timedelta(days=1)
			elif duration == '1w':
				dur_time = timedelta(days=7)
			elif duration == '2w':
				dur_time = timedelta(days=14)
			elif duration == '3w':
				dur_time = timedelta(days=21)
			elif duration == '1m':
				dur_time = timedelta(days=30)
			else:
				dur_time = timedelta(days=7) #default 1 week
			vote_time = vote.vote_time
			news_time = vote.news.time
			# formula:
			if (news_time+dur_time-vote_time).total_seconds() < 0: #vote after news ended
				vote.vote_rate = 0
				vote.vote_rate_status = True # optimize with not recalculation
				print('vote {} after news ended'.format(vote))
				vote.save()
				#coef = 0
			else:
				print((news_time+dur_time-vote_time).total_seconds(), dur_time.total_seconds())
				#1 - if vote_time==news_time to 0 if vote_time==news_time+duration
				vote_rate = (news_time+dur_time-vote_time).total_seconds()/dur_time.total_seconds()
				coef = 1
				if new_rate > 0 and vote.vote_type =='dislike':
					coef = -1
				if new_rate < 0 and vote.vote_type =='like':
					coef = -1
				vote_rate = vote_rate * coef * abs(float(new_rate))
				print('{} {} {}'.format(vote.user, vote.news.newsid, vote.vote_type))
				print('nr:{} dir:{} d:{} n:{} v:{} vr:{} c:{}'.format(new_rate, direction ,dur_time, news_time, vote_time, vote_rate, coef))
				#save:
				vote.vote_rate = vote_rate
				if news_time+dur_time<timezone.now(): # news duration ended
					print('news duration ended')
					vote.vote_rate_status=True # optimize with not recalculation
				vote.save()
				stats_votes_chenged += 1
		#rate profiles:
		all_users_today_positive = 0
		all_users_today_active = 0 #sum_today <> 0
		dayago = timezone.now()-timedelta(days=1)
		for profile in profiles:
			print(profile.user)
			votes = UserVotes.objects.filter(user=profile.user)
			sum_all = 0
			sum_positive = 0
			sum_today = 0
			sum_today_positive = 0
			for vote in votes:
				print('{} {}'.format(vote.vote_rate, vote.vote_time))
				sum_all +=vote.vote_rate
				if vote.vote_rate>0:
					sum_positive += vote.vote_rate
				if vote.vote_time > dayago:
					sum_today += vote.vote_rate
					if vote.vote_rate>0:
						sum_today_positive += vote.vote_rate
			profile.sum_all = sum_all
			profile.sum_positive = sum_positive
			profile.sum_today = sum_today
			profile.sum_today_positive = sum_today_positive
			profile.sum_likes = votes.filter(vote_type='like').count()
			profile.sum_dislikes = votes.filter(vote_type='dislike').count()
			profile.sum_right = votes.filter(vote_rate__gt=0).count()
			#second stage (calculate news stats):
			news = News.objects.filter(user=profile.user)
			profile.sum_news = news.count()
			if profile.sum_news>0:
				profile.sum_news_rating = news.aggregate(Sum('rating'))['rating__sum']
				print(news.count(),' news, ', profile.sum_news_rating,' sum news rating')
			#need news aggs stats -> news_points
			#profile.point = sum_positive # first stage
			profile.point = sum_all + profile.sum_news_rating #second stage
			profile.save()
			if sum_today != 0:
				all_users_today_active += 1
			all_users_today_positive += sum_today_positive
			print('a:{} p:{} ta:{} tp:{} counts l:{} d:{} r:{}'.format(sum_all, sum_positive, sum_today, sum_today_positive, profile.sum_likes, profile.sum_dislikes, profile.sum_right))
		print('sum positive:{} all active:{}'.format(all_users_today_positive,all_users_today_active))
		#sort by profile.point and save order place in rank:
		profiles=Profile.objects.order_by('-point')
		i=0
		for profile in profiles:
			if profile.point>0:
				i+=1
				profile.rank=i
			else:
				profile.rank=0
			profile.save()
			#print(i, profile, profile.point, profile.rank, profile.user)
		#return:
		return_text = 'profiles:{} sum positive:{} all active:{} votes(false): {} votes(calc):{}'.format(stats_profiles,all_users_today_positive,all_users_today_active,stats_votes_false,stats_votes_chenged)
		return return_text


	#'https://www.cryptocompare.com/api/data/coinlist/'
	#"DGB":{
	# "Id":"4430",
	# "Url":"/coins/dgb/overview",
	#ok "ImageUrl":"/media/12318264/7638-nty_400x400.jpg",
	# "Name":"DGB",
	#ok "Symbol":"DGB",
	#ok "CoinName":"DigiByte",
	# "FullName":"DigiByte (DGB)",
	#! "Algorithm":"Multiple",
	#! "ProofType":"PoW",
	#! "FullyPremined":"0",
	# "TotalCoinSupply":"21000000000",
	# "PreMinedValue":"N/A",
	# "TotalCoinsFreeFloat":"N/A",
	#! "SortOrder":"11",
	# "Sponsored":false}
	def cryptocompare_get_coinlist(self, filename):
		url1='https://min-api.cryptocompare.com/data/all/coinlist'
		#old url: https://www.cryptocompare.com/api/data/coinlist/
		#new url: https://min-api.cryptocompare.com/data/all/coinlist
		response1 = requests.get(url1)
		data = response1.json()['Data']
		file = open(DATADIR+'/'+filename, 'w', encoding='utf8')
		json.dump(data, file)
		file.close()
		print('coins:',len(data))
	
	def print_coinlist(self, filename):
		file = open(DATADIR+'/'+filename, 'r')
		data = json.load(file)
		file.close()
		coin_count=0
		coin_noimage_count=0
		for coin in data:
			coin_count+=1
			try:
				if 'ImageUrl' in data[coin].keys():
					print(data[coin]['Symbol'], data[coin]['CoinName'], data[coin]['SortOrder'], data[coin]['TotalCoinSupply'], data[coin]['ImageUrl'])
				else:
					coin_noimage_count+=1
					print(data[coin]['Symbol'], data[coin]['CoinName'], data[coin]['SortOrder'],data[coin]['TotalCoinSupply'])
			except UnicodeEncodeError as error:
				print(error)
		print('coins: {} coins no image: {}'.format(coin_count, coin_noimage_count))

	#https://min-api.cryptocompare.com/data/price?fsym=ETH&tsyms=BTC,USD,EUR
	#https://min-api.cryptocompare.com/data/pricemulti?fsyms=ETH,DASH&tsyms=BTC,USD,EUR
	#https://min-api.cryptocompare.com/data/pricemultifull?fsyms=ETH,DASH&tsyms=BTC,USD,EUR
	def cryptocompare_get_price(self, coinlist_file, pricelist_file, type):
		if type!='simple' and type!='full':
			return False

		BATCHSIZE=20
		file = open(DATADIR+'/'+coinlist_file, 'r')
		data = json.load(file)
		file.close()

		size = len(data)
		names = ''
		sets=[]
		count=0
		for coin in data:
			names=names+coin+','
			count+=1
			if count>BATCHSIZE:
				names=names[:-1]
				sets.append(names)
				names=''
				count=0
				continue
		names=names[:-1]
		if names != '':
			sets.append(names)
		#print(sets)

		file = open(DATADIR+'/'+pricelist_file, 'w')
		data={}
		for string in sets:
			print(string)
			if type=='simple':
				url2 = 'https://min-api.cryptocompare.com/data/pricemulti?fsyms='+string+'&tsyms=USD'
				response2 = requests.get(url2)
				temp=response2.json()
			elif type=='full':
				url2 = 'https://min-api.cryptocompare.com/data/pricemultifull?fsyms='+string+'&tsyms=USD'
				response2 = requests.get(url2)
				temp=response2.json()['RAW']
			#print(temp)
			for coin in temp:
				data[coin]=temp[coin]
		json.dump(data, file)
		file.close()

	def coinlist_exclude(self):
		#read from price file
		file = open(DATADIR+'/'+FILE_PRICE, 'r')
		rawdata = json.load(file)
		file.close()
		print('coins from full price file:',len(rawdata))
		
		#create list of priced coins with marketcap > 0 
		#may be: TOTALVOLUME24HTO > 0 test
		priced_coins = [ coin for coin in rawdata if 'TOTALVOLUME24HTO' in rawdata[coin]['USD'] and rawdata[coin]['USD']['TOTALVOLUME24HTO']!=0]
		#priced_coins = [ coin for coin in rawdata if 'MKTCAP' in rawdata[coin]['USD'] 
		#and 'TOTALVOLUME24HTO' in rawdata[coin]['USD'] and rawdata[coin]['USD']['MKTCAP']!=0 and rawdata[coin]['USD']['TOTALVOLUME24HTO']!=0]
		#priced_coins = [ coin for coin in rawdata if 'MKTCAP' in rawdata[coin]['USD'] and rawdata[coin]['USD']['MKTCAP']!=0 ]
		print('coins from full price file with TOTALVOLUME24HTO :',len(priced_coins))
		#print('coins from full price file with MKTCAP and TOTALVOLUME24HTO :',len(priced_coins))

		#read from coinlist file
		file = open(DATADIR+'/'+FILE_COINLIST, 'r')
		coins = json.load(file)
		file.close()
		
		#remove coins without price from coinlist
		print('coins from coinlist file:', len(coins))
		new_coins = {k:v for k,v in coins.items() if k in priced_coins}
		print('coins from coinlist file with price:', len(new_coins))
		#exclude custom list:
		for symbol in EXCLUDE_LIST:
			if symbol in new_coins:
				new_coins.pop(symbol)
				print('removed coin:'+symbol)
		file = open(DATADIR+'/'+FILE_COINLIST, 'w')
		json.dump(new_coins, file)
		file.close()

	def cryptocompare_get_images(self):
		
		print(os.getcwd()) #coin_images
		filelist = os.listdir(COINIMAGESDIR)
		#print(filelist)
		file = open(DATADIR+'/'+FILE_COINLIST, 'r')
		coins = json.load(file)
		file.close()

		for coin in coins:
			if 'ImageUrl' not in coins[coin].keys():
				print('not find ImageUrl for coin:'+coin)
				continue
			filename = coins[coin]['CoinName']+'.'+coins[coin]["ImageUrl"].split('.')[-1]
			if filename in filelist:
				pass
				#print('already downloaded')
			else:
				url = 'https://www.cryptocompare.com'+coins[coin]["ImageUrl"]# "https://www.cryptocompare.com /media/1382433/btz.png"
				response = requests.get(url)
				if response.status_code == 200:
					filename = COINIMAGESDIR+filename
					try:
						with open(filename, 'wb') as f:
							f.write(response.content)
						print('saved file:'+filename+' coinname:'+coins[coin]["CoinName"])
					except Exception as error:
						print('error:', error)

	#'coinadd - read coinlist from file and update list on db model Coin - coin.id, coin.symbol, coin.name'
	def coinadd(self, action='all'):
		#read from coinlist file
		file = open(DATADIR+'/'+FILE_COINLIST, 'r')
		filecoins = json.load(file)
		file.close()
		
		#read from db and creade dict of coins symbol
		dbcoins = Coin.objects.all()
		coins_symbol = [coin.symbol for coin in dbcoins]
		coins_symbol.sort()
		print(coins_symbol)

		#read from coinprice file
		#read from price file
		file = open(DATADIR+'/'+FILE_PRICE, 'r')
		rawdata = json.load(file)
		file.close()
		
		count_update=0
		if action in ['all', 'update']:
			#update coins in db
			print('update coins in db:')
			for dbcoin in dbcoins:
				if dbcoin.symbol in EXCLUDE_LIST:
					print('coin excluded: '+dbcoin.symbol)
				elif dbcoin.symbol not in filecoins:
					print('coin {} not found in coinlist'.format(dbcoin.symbol))
				else:
					#name
					dbcoin.name = filecoins[dbcoin.symbol]['CoinName']
					#price
					pricedata = rawdata[dbcoin.symbol]['USD']
					dbcoin.price = pricedata['PRICE']
					dbcoin.change = pricedata['CHANGEPCT24HOUR']
					dbcoin.volume = pricedata['TOTALVOLUME24HTO']
					dbcoin.mktcap = pricedata['MKTCAP']
					#image
					if 'ImageUrl' not in filecoins[dbcoin.symbol].keys():
						print('not find ImageUrl for coin:'+ dbcoin.symbol)
					else:
						filepath = 'coin_images/'+filecoins[dbcoin.symbol]['CoinName']+'.'+filecoins[dbcoin.symbol]["ImageUrl"].split('.')[-1]
						#print('image path:', filepath)
						dbcoin.image = filepath
					try:
						dbcoin.save()
						count_update+=1
					except Exception as error:
						print('not saved coin {} with error {}'.format(dbcoin.symbol, error))
					# print('newdbcoin: {}'.format(dbcoin.symbol)), 
					# print('name: {}'.format(dbcoin.name)),
					# print('image: {}'.format(dbcoin.image))

		count_add=0
		if action in ['all', 'add']:
			#add coins in db
			print('add coins in db:')
			#for filecoin in filecoins:
			for symbol in filecoins:
				if symbol in coins_symbol:
					print('coin: {} already in db'.format(symbol))
				else:
					#newdbcoin = Coin.objects.create()
					newdbcoin = Coin()
					newdbcoin.symbol = symbol
					newdbcoin.name = filecoins[symbol]['CoinName']
					pricedata = rawdata[symbol]['USD']
					newdbcoin.price = pricedata['PRICE']
					newdbcoin.change = pricedata['CHANGEPCT24HOUR']
					newdbcoin.volume = pricedata['TOTALVOLUME24HTO']
					newdbcoin.mktcap = pricedata['MKTCAP']
					if 'ImageUrl' not in filecoins[symbol].keys():
						print('not find ImageUrl for coin:'+ dbcoin.symbol)
					else:
						filepath = 'coin_images/'+filecoins[symbol]['CoinName']+'.'+filecoins[symbol]["ImageUrl"].split('.')[-1]
						try:
							print('image path:', filepath)
						except Exception:
							print('error filepath in coin:',symbol)
						newdbcoin.image = filepath
					try:
						newdbcoin.save()
						count_add+=1
					except Exception as error:
						print(error)
						print(newdbcoin.price)
						print(newdbcoin.change)
						print(newdbcoin.volume)
						print(newdbcoin.mktcap)
					# print('newdbcoin: {}'.format(newdbcoin.symbol)), 
					# print('name: {}'.format(newdbcoin.name)),
					# print('image: {}'.format(newdbcoin.image))
		print('coins updated:', count_update)
		print('coins added  :', count_add)



	def coinlist_from_db(self):
		coins = Coin.objects.all()
		for coin in coins:
			print(coin.id, coin.symbol, coin.name, coin.image, coin.price, coin.change, coin.volume, coin.mktcap)
		print('coins in db:', len(coins))

		#coin.image = 'coin_images/CoinName.xxx'
		#coin.save()

	def coininfo(self, symbol):
		#read from price file
		file = open(DATADIR+'/'+FILE_PRICE, 'r')
		rawdata = json.load(file)
		file.close()
		print('coins from full price file:',len(rawdata))

		pricedata = rawdata[symbol]['USD']
		for key, value in pricedata.items():
			print(key, value)
		#read from coinlist file
		file = open(DATADIR+'/'+FILE_COINLIST, 'r')
		coins = json.load(file)
		file.close()
		print('\ncoins from coinlist file:', len(coins))

		coin = coins[symbol]
		for key, value in coin.items():
			print(key, value)

	def get_price(self, coin):
		url = 'https://min-api.cryptocompare.com/data/pricemulti?fsyms='+coin+'&tsyms=USD,BTC'
		try:
			response = requests.get(url)
			price=response.json()[coin]['USD']
			print('from internet')
		except Exception as error:
			dbcoin=Coin.objects.get(symbol=coin)
			price=dbcoin.price
			print('error:',error)
			print('from db')
		return price

	def sendmail(self):
		try: #get production settings
			connection = get_connection(backend=SMTP_EMAIL_BACKEND)
			with open('email.txt') as f:
				email_setting = [line.strip() for line in f]
			connection.host = email_setting[1]
			connection.username = email_setting[2]
			connection.password = email_setting[3]
			connection.port = EMAIL_PORT
			connection.use_tls = EMAIL_USE_TLS
			test_to = email_setting[4]
			print(email_setting[0])
			print(connection)
			print(connection.host, connection.username, connection.password)
			send_mail('from test1', 'test1 sendmail function', connection.username, [test_to], connection = connection)
		except Exception: #get console settings for dev
			connection = get_connection(backend=CONSOLE_EMAIL_BACKEND)
			print(connection)
			send_mail('from test1', 'test1 sendmail function', 'admin@localhost', ['user@localhost'], connection = connection)

	def get_apistats(self):
		#{"Message":"Total rate limit stats",
		# "Hour":{"CallsMade":{"Histo":0,"Price":54,"News":0,"Strict":0},
		#         "CallsLeft":{"Histo":8000,"Price":149946,"News":3000,"Strict":500}},
		# "Minute":{"CallsMade":{"Histo":0,"Price":0,"News":0,"Strict":0},
		#         "CallsLeft":{"Histo":300,"Price":1000,"News":100,"Strict":20}},
		# "Second":{"CallsMade":{"Histo":0,"Price":0,"News":0,"Strict":0},
		#         "CallsLeft":{"Histo":15,"Price":50,"News":5,"Strict":1}}}
		url = 'https://min-api.cryptocompare.com/stats/rate/limit'
		response = requests.get(url)
		hour_price_made = str(response.json()['Hour']['CallsMade']['Price'])
		hour_price_left = str(response.json()['Hour']['CallsLeft']['Price'])
		min_price_made = str(response.json()['Minute']['CallsMade']['Price'])
		min_price_left = str(response.json()['Minute']['CallsLeft']['Price'])
		return 'hm:'+hour_price_made+' hl:'+hour_price_left+' mm:'+min_price_made+' ml:'+min_price_left

	def handle(self, *args, **options):
		try:
			print('arguments exists:')
			for poll_id in options['poll_id']:
				print(poll_id)
		except Exception:
			print('no arguments')

		#system:
		print(os.getcwd()) #c:\WORK\Docs\python\web\locallibrary
		print(sys.argv)
		print(options)

		#selector:
		poll_id = options['poll_id']
		if 'help' in poll_id:
			self.help()
		
		if 'rate_news' in poll_id:
			self.rate_news()

		if 'rate_sources' in poll_id:
			self.rate_sources()

		if 'rate_users' in poll_id:
			text = self.rate_users()
			file = open(DATADIR+'/'+FILE_RESULT_RATE_USERS, 'a')
			file.write(text)
			file.write(' rate_users finished at time {}\n'.format(timezone.now()))
			file.close()
		
		if 'coinlist' in poll_id:
			index = poll_id.index('coinlist')
			try:
				filename = poll_id[index+1]
			except Exception:
				filename = FILE_COINLIST
			print(filename)
			self.cryptocompare_get_coinlist(filename)
		
		if 'coinprint' in poll_id:
			index = poll_id.index('coinprint')
			try:
				filename = poll_id[index+1]
			except Exception:
				filename = FILE_COINLIST
			print(filename)
			self.print_coinlist(filename)
		
		#cryptocompare_get_price('coinlist.txt', 'coinpricesimple.txt', 'simple')
		#cryptocompare_get_price('coinlist.txt', 'coinpricefull.txt', 'full' )
		if 'coinprice' in poll_id:
			index = poll_id.index('coinprice')
			try:
				coinlist_file = poll_id[index+1]
			except Exception:
				coinlist_file = FILE_COINLIST
			try:
				pricelist_file = poll_id[index+2]
			except Exception:
				pricelist_file = FILE_PRICE
			try:	
				type_file = poll_id[index+3]
			except Exception:
				type_file = TYPE_PRICE
			self.cryptocompare_get_price(coinlist_file, pricelist_file, type_file)

		if 'coinimage' in poll_id:
			self.cryptocompare_get_images()

		if 'coinprint_db' in poll_id:
			self.coinlist_from_db()

		if 'coininfo' in poll_id:
			index = poll_id.index('coininfo')
			try:
				symbol = poll_id[index+1]
			except Exception:
				symbol = 'BTC'
			print(symbol)
			self.coininfo(symbol)

		if 'coinlist_exclude' in poll_id:
			self.coinlist_exclude()

		if 'coinadd' in poll_id:
			index = poll_id.index('coinadd')
			try:
				action = poll_id[index+1]
			except Exception:
				action = 'all'
			self.coinadd(action)

		if 'update_cycle' in poll_id:
			self.cryptocompare_get_price(FILE_COINLIST, FILE_PRICE, TYPE_PRICE)
			self.coinlist_exclude()
			self.coinadd('update')
			self.rate_news()
			self.rate_sources()
			stats = self.get_apistats() #https://min-api.cryptocompare.com/stats/rate/limit
			print(stats)
			file = open(DATADIR+'/'+FILE_RESULT, 'a')
			file.write(stats)
			file.write(' update_cycle finished at time {}\n'.format(timezone.now()))
			file.close()

		if 'get_price' in poll_id:
			index = poll_id.index('get_price')
			try:
				coin = poll_id[index+1]
			except Exception:
				coin = 'BTC'
			print(self.get_price(coin))

		if 'sendmail' in poll_id:
			self.sendmail()









