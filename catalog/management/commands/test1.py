#update_news_rating_test1
#C:\WORK\Docs\python\web\locallibrary

#API
#https://min-api.cryptocompare.com/stats/rate/limit - my limits
#Hour limit - 150000, Minute limit - 1000, Second limit - 50


import os,sys,glob
# print(os.getcwd())
# print(sys.argv)
from django.core.management.base import BaseCommand, CommandError
from catalog.models import News, Coin, Source, UserVotes, Profile, YeenotSettings, CoinCryptocompare
from catalog.models import Exchange, CoinGecko
from django.contrib.auth.models import User

import requests
import json
import os
from statistics import median
import collections #for coinsnapshot_print

FILE_COINLIST = 'coinlist.txt'
FILE_PRICE = 'coinpricefull.txt'
FILE_SNAPSHOT_CC = 'coinsnapshotcc.txt'
FILE_EXCHANGE_PAIRS = 'pairs.txt'
FILE_RESULT = 'result.txt'
FILE_RESULT_RATE_USERS = 'result_rate_users.txt'
TYPE_PRICE = 'full'
DATADIR = 'data'
COINIMAGESDIR = 'media/coin_images/'
RATING_MAX_DAYS = 7

EXCLUDE_LIST = ['ARENA','CNO', 'BTH', 'ADL','HOLD','MDX','ATOM*','DCS','LVL*','XUN','CWX', 'AMIS']

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
		print('coinadd [action - all, update, add]- read coinlist from file and update list on db model Coin - coin.id, coin.symbol, coin.name, etc...')
		print('.......also - calculate coin.news_count, coin_stats for volume, mktcap, change24h')#!!! another stats
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
		print('coinsnapshot - read json from file coinlist , get snapshot, write json to coinsnapshotcc file') #ok
		print('coinsnapshot_print - read json from file coinsnapshotcc, print data') #ok
		print('coinsnapshot_update - read json from file coinsnapshotcc, update data in Coin_Cryptocompare')#ok
		print('coinsocial - read json from file coinlist , get social, write json to social file with date')#!!!!
		print('coinsocial_update - read json from last time social file, update data in Coin_Cryptocompare')#!!!! twitter - ok, reddit - ok
		#need: facebook, cryptocompare, github
		#update_cycle_2 1/day: coinlist -> wait -> coinadd add -> coinimage -> coinsnapshot+coinsocial
		print('exchange_pairs - get exchange pairs, save to file, update model exchange_pairs')
		#!!! need create news and exclude exchanges, need compare current dblist with new list (возможны изменения в строну уменьшения)
		#!!! need clearing of coinlist_update
		print('coingecko_get - get coinlist API, save to file coingecko/list.txt , add to CoinGecko, save result.txt')
		#!!! need manual add (MIOTA and others) from list in function
		#!!! fastest method of update: https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd
		#[Alpha] List all supported coins price, market cap, volume, and market related data (no pagination required)
		'''
		"id": "bitcoin",
	    "symbol": "btc",
	    "name": "Bitcoin",
	    "current_price": 7534.35874634154,
	    "market_cap": 128718582106.5531,
	    "total_volume": 1123239107.9021242,
	    "high_24h": 7605.38589614029,
	    "low_24h": 7505.72763862948,
	    "price_change_24h": "7.14542922808",
	    "price_change_percentage_24h": "0.0949279491234099",
	    "market_cap_change_24h": "135623011.734",
	    "market_cap_change_percentage_24h": "0.10547510547956",
	    "circulating_supply": "17084212.0"
    	'''
		print('coingecko_export - get CoinGecko, save to file coingecko/export.txt')
		print('coingecko_import - get file coingecko/export.txt and add data to CoinGecko')
		print('coingecko_getall - get CoinGecko, request API for coins, save all data to file coingecko/all/id.txt')
		#need coingecko_getall coinmarketdata and stats по всем монетам
		print('coingecko_update - get files coingecko/all/id.txt and update data in CoinGecko')
		print('daily [get, update, [symbol] ] read coinlist from file, get daily OHLCV from cryptocompare, save to file, calculate ATH and Volatility and write to db')
		#need optimize 7day volatility with hours OHLCV
		#need [symbol]/BTC ATH
		#need plots
		#need days from ATH, trade days counts


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
					#name and others from filecoins
					dbcoin.name = filecoins[dbcoin.symbol]['CoinName']
					dbcoin.Algorithm = filecoins[dbcoin.symbol]['Algorithm']
					dbcoin.ProofType = filecoins[dbcoin.symbol]['ProofType']
					#dbcoin.SortOrder = int(filecoins[dbcoin.symbol]['SortOrder'])
					total = filecoins[dbcoin.symbol]['TotalCoinSupply']
					if total == 'N/A' or total == '0' or total == '':
						dbcoin.TotalCoinSupply = ''
					else:
						dbcoin.TotalCoinSupply = total.split('.')[0].replace(',','').replace(' ','')
					#dbcoin.TotalCoinSupply = filecoins[dbcoin.symbol]['TotalCoinSupply']
					dbcoin.Id_cc = int(filecoins[dbcoin.symbol]['Id'])
					#price
					pricedata = rawdata[dbcoin.symbol]['USD']
					dbcoin.price = pricedata['PRICE']
					dbcoin.change = pricedata['CHANGEPCT24HOUR']
					dbcoin.volume = pricedata['TOTALVOLUME24HTO']
					dbcoin.mktcap = pricedata['MKTCAP']
					dbcoin.supply = pricedata['SUPPLY']
					if total == 'N/A' or total == '0' or total == '':
						dbcoin.supply_share = 1
					else:
						dbcoin.supply_share = pricedata['SUPPLY']/int(dbcoin.TotalCoinSupply)
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
					#from filecoins
					newdbcoin.symbol = symbol
					#print(filecoins[symbol])
					newdbcoin.name = filecoins[symbol]['CoinName']
					newdbcoin.Algorithm = filecoins[symbol]['Algorithm']
					newdbcoin.ProofType = filecoins[symbol]['ProofType']
					#newdbcoin.SortOrder = int(filecoins[symbol]['SortOrder'])
					total = filecoins[symbol]['TotalCoinSupply']
					if total == 'N/A' or total == '0' or total == '':
						newdbcoin.TotalCoinSupply = ''
					else:
						newdbcoin.TotalCoinSupply = total.split('.')[0].replace(',','').replace(' ','')
					#newdbcoin.TotalCoinSupply = filecoins[symbol]['TotalCoinSupply']
					newdbcoin.Id_cc = int(filecoins[symbol]['Id'])
					#from pricedata
					pricedata = rawdata[symbol]['USD']
					newdbcoin.price = pricedata['PRICE']
					newdbcoin.change = pricedata['CHANGEPCT24HOUR']
					newdbcoin.volume = pricedata['TOTALVOLUME24HTO']
					newdbcoin.mktcap = pricedata['MKTCAP']
					newdbcoin.supply = pricedata['SUPPLY']
					if total == 'N/A' or total == '0' or total == '':
						newdbcoin.supply_share = 1
					else:
						newdbcoin.supply_share = pricedata['SUPPLY']/int(newdbcoin.TotalCoinSupply)
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
		#update news_count:
		yeenotnews = News.objects.values_list('coinid', flat=True)
		coin_id_set = set(yeenotnews)
		print('set of coins with yeenot news:',coin_id_set)
		for id in coin_id_set:
			coin = Coin.objects.get(id=id)
			coin.news_count = yeenotnews.filter(coinid=id).count()
			print(coin.id, coin.symbol, coin.news_count)
			coin.save()
		#update aggregation stats from dbcoins:
		'''
		example:
		{'change__min': Decimal('-80.00000000'), 'mktcap__max': Decimal('130742290177.00000000'),
		 'volume__max': Decimal('2786191258.85099983'), 'change__max': Decimal('800.00000000')}
		'''
		agg_value = dbcoins.aggregate(num_value = models.Max('volume'))
		obj, created = YeenotSettings.objects.update_or_create(name='coins_volume_max',defaults=agg_value)
		print(obj.id, obj.num_value, created)
		agg_value = dbcoins.aggregate(num_value = models.Max('mktcap'))
		obj, created = YeenotSettings.objects.update_or_create(name='coins_mktcap_max',defaults=agg_value)
		print(obj.id, obj.num_value, created)
		agg_value = dbcoins.aggregate(num_value = models.Min('change'))
		obj, created = YeenotSettings.objects.update_or_create(name='coins_change24h_min',defaults=agg_value)
		print(obj.id, obj.num_value, created)
		agg_value = dbcoins.aggregate(num_value = models.Max('change'))
		obj, created = YeenotSettings.objects.update_or_create(name='coins_change24h_max',defaults=agg_value)
		print(obj.id, obj.num_value, created)


	def cryptocompare_get_DOHLCV(self, action='get'): #get update or symbol
		# Load the required modules and packages
		import numpy as np
		import pandas as pd
		import time
		import datetime
		
		#read from coinlist file
		file = open(DATADIR+'/'+FILE_COINLIST, 'r')
		filecoins = json.load(file)
		file.close()

		#https://min-api.cryptocompare.com/data/histoday?fsym=BTC&tsym=USD&allData=1
		if action=='update':
			print('filecoins: {}'.format(len(filecoins)))
			for filecoin in filecoins:
				filename = filecoin.replace("*", "_")
				file = open(DATADIR+'/daily/'+filename+'.txt', 'r')
				dataraw = json.load(file) #get DOHLCV['Data'] from file
				days_before = len(dataraw)
				#remove HIGH > 100*CLOSE
				print('check data for:',filecoin)
				data=[]
				for daydata in dataraw:
					if daydata['high']>100*daydata['close'] or daydata['high']>100*daydata['open'] or daydata['high']>100*daydata['low']:
						pass
						#print(daydata)
					else:
						data.append(daydata)
				days = len(data)

				# Computing AHT
				ath = max(data, key=lambda x:x['high'])
				athdate =  datetime.datetime.fromtimestamp(ath['time'])#.strftime('%Y-%m-%d %H:%M:%S')
				#print('all time high: {} date: {}'.format(ath['high'],athdate))
				# Computing Volatility
				df = pd.DataFrame(data)
				df['Log_Ret'] = np.log(df['close'] / df['close'].shift(1))
				volatility30day =  df['Log_Ret'].tail(30).std(ddof=0)*np.sqrt(30)
				volatility7day =  df['Log_Ret'].tail(7).std(ddof=0)*np.sqrt(7)
				#print('volatility 30day: {} '.format(volatility30day))
				#if days<30:
				print('coin:{} days_b: {} days_a:{} ath:{} athdate: {} volatility 30day: {}'.format(filecoin, days_before, days, ath['high'], athdate, volatility30day))
				dbcoin = Coin.objects.get(symbol=filecoin)
				dbcoin.ath = ath['high']
				dbcoin.athdate = athdate
				dbcoin.athchange = float(dbcoin.price)/ath['high']
				if days>30:
					dbcoin.volatility30day = volatility30day
				else:
					dbcoin.volatility30day = 0
				if days>7:
					dbcoin.volatility7day = volatility7day
				else:
					dbcoin.volatility7day = 0
				dbcoin.save()

		elif action=='get': #get daily OHLCV for coins in filecoins if not downloaded today with pause control 
			count=0
			error_count=0
			error_list=[]
			downloaded_count=0
			#list_of_files = [item.split('\\')[1].split('.')[0].replace('_','*') for item in glob.glob(DATADIR+'/daily/*')]
			
			#times = [os.path.getctime(item) for item in glob.glob(DATADIR+'/daily/*')]
			#print('downloaded:',len(times))
			today = datetime.date.today() - datetime.timedelta(days=1)
			float_today=time.mktime(today.timetuple())
			print('today: {} unix: {}'.format(today,float_today))
			list_of_files = [item.split('\\')[1].split('.')[0].replace('_','*') for item in glob.glob(DATADIR+'/daily/*') if os.path.getctime(item)>float_today]
			print('downloaded last day:',len(list_of_files))

			for filecoin in filecoins:
				count+=1
				print('count:{} get daily OHLCV for {}/USD'.format(count,filecoin))
				if filecoin in list_of_files:
					print('already downloaded last day')
					continue
				#check file: filecoin.txt
				#change * to _
				filename = filecoin.replace("*", "_")
				#get info:
				url = 'https://min-api.cryptocompare.com/data/histoday?fsym='+filecoin+'&tsym=USD&allData=1'#limit=1'
				response = requests.get(url)
				DOHLCV = response.json()
				if DOHLCV['Response']=='Success':
					data = DOHLCV['Data']
					#save data:
					file = open(DATADIR+'/daily/'+filename+'.txt', 'w', encoding='utf8')
					json.dump(data, file)
					file.close()
					print('saved in file {}.txt days: {}'.format(filename, len(data)))
					downloaded_count+=1
				else:
					print(DOHLCV['Response'])
					error_count+=1
					error_list.append(filecoin)
				url = 'https://min-api.cryptocompare.com/stats/rate/limit'
				response = requests.get(url).json()
				hleft = response['Hour']['CallsLeft']['Histo']
				mleft = response['Minute']['CallsLeft']['Histo']
				sleft = response['Second']['CallsLeft']['Histo']
				print('HOUR made: {} left: {}'.format(response['Hour']['CallsMade']['Histo'],hleft))
				print('MIN  made: {} left: {}'.format(response['Minute']['CallsMade']['Histo'],mleft))
				print('SEC  made: {} left: {}'.format(response['Second']['CallsMade']['Histo'],sleft))
				if mleft<=6:
					print('MIN: sleep for 30 sec')
					time.sleep(30)
				'''
				if count>200:
					break
				'''	
			print('filecoins: {}'.format(len(filecoins)))
			print('already downloaded last day:',len(list_of_files))
			print('errors:',error_count)
			print('coins with error:',error_list)
			print('downloaded:',downloaded_count)
		
		else:
			print('get daily OHLCV for {}/USD'.format(action))
			url = 'https://min-api.cryptocompare.com/data/histoday?fsym='+action+'&tsym=USD&allData=1'#limit=1'
			response = requests.get(url)
			DOHLCV=response.json()
			url2 = 'https://min-api.cryptocompare.com/data/histohour?fsym='+action+'&tsym=USD&limit=348' # 7*24*2
			response2 = requests.get(url2)
			HOHLCV=response2.json()
			#print(DOHLCV) 
			#'TimeTo': 1528848000, 'TimeFrom': 1520208000, 'Response': 'Success'
			#'Data': [{'close': 11440.73, 'open': 11503.94, 'high': 11694.15, 'time': 1520208000, 'low': 11431.55, 'volumefrom': 68323.51, 'volumeto': 791471905.1}
			if DOHLCV['Response']=='Success':
				data = DOHLCV['Data']
				days = len(data)
				print('days: {}'.format(days))
				aht = max(data, key=lambda x:x['high'])
				ahtdate =  datetime.datetime.fromtimestamp(aht['time'])#.strftime('%Y-%m-%d %H:%M:%S')
				print('all time high: {} date: {}'.format(aht['high'],ahtdate))
				#save data:
				file = open(DATADIR+'/daily/'+action+'.txt', 'w', encoding='utf8')
				json.dump(data, file)
				file.close()
			if HOHLCV['Response']=='Success':
				data2 = HOHLCV['Data']
				hours = len(data2)
				print('hours: {}'.format(hours))
				print(data[-1])

			## Computing Volatility
			df = pd.DataFrame(data)
			df_hours = pd.DataFrame(data2)
			#vals = df.values
			#print(vals)

			# Compute the logarithmic returns using the Closing price 
			df['Log_Ret'] = np.log(df['close'] / df['close'].shift(1))
			df_hours['Log_Ret'] = np.log(df_hours['close'] / df_hours['close'].shift(1))
			#print(df.head())
			#print(df['Log_Ret'])

			# Compute Volatility using the pandas rolling standard deviation function
			df_hours['7dayVolatility'] = df_hours['Log_Ret'].rolling(174).std(ddof=0) * np.sqrt(174)
			df['7dayVolatility'] = df['Log_Ret'].rolling(7).std(ddof=0) * np.sqrt(7)
			df['30dayVolatility'] = df['Log_Ret'].rolling(30).std(ddof=0) * np.sqrt(30)
			df['60dayVolatility'] = df['Log_Ret'].rolling(60).std(ddof=0) * np.sqrt(60)
			print(df.tail(10))
			print(df_hours.tail(10))
			volatility_30day =  df['Log_Ret'].tail(30).std(ddof=0)*np.sqrt(30)
			print(volatility_30day)

			# Plot the NIFTY Price series and the Volatility
			plot = df[['close', '30dayVolatility']].tail(365).plot(subplots=True, color='blue',figsize=(8, 6))
			fig = plot[0].get_figure()
			fig.savefig(DATADIR+'/daily/volatility'+action+'.png')

			url = 'https://min-api.cryptocompare.com/stats/rate/limit'
			response = requests.get(url)
			rate = response.json()
			print(rate)


################# Cryptocompare snapshot and social functions ######################
	def cryptocompare_get_snapshot(self, coinlist_file, coinsnapshot_file):
		#get coins from coinlist
		file = open(DATADIR+'/'+coinlist_file, 'r')
		filecoins = json.load(file)
		file.close()

		file = open(DATADIR+'/'+coinsnapshot_file, 'w')
		data={}
		counter=0
		for coin in filecoins:
			counter+=1
			id = filecoins[coin]['Id']
			print(id, coin, counter)
			url = 'https://www.cryptocompare.com/api/data/coinsnapshotfullbyid/?id='+id
			response = requests.get(url)
			temp = response.json()['Data']['General']
			data[id]=temp
		json.dump(data, file)
		file.close()

	def coin_cryptocompare_update(self, coinsnapshot_file):
		file = open(DATADIR+'/'+FILE_SNAPSHOT_CC, 'r')
		filecoins = json.load(file)
		file.close()
		#cc_coins = CoinCryptocompare.objects.get(Id_cc = 1)
		#print(cc_coins)
		count_update = 0
		count_add = 0
		for id in filecoins:
			try:
				cc_coin = CoinCryptocompare.objects.get(Id_cc = id) #!!!!need debug dublication
				print('coin found in db and updated. id: {} symbol: {}'.format(id, filecoins[id]['Symbol']))
				count_update +=1
			except:
				print('coin not found and created. id: {} symbol: {}'.format(id, filecoins[id]['Symbol']))
				cc_coin = CoinCryptocompare()
				count_add +=1
			cc_coin.Id_cc = id
			cc_coin.symbol = filecoins[id]['Symbol']
			cc_coin.name = filecoins[id]['Name']
			cc_coin.Description = filecoins[id]['Description']
			cc_coin.WebsiteUrl = filecoins[id]['WebsiteUrl'].split('?utm_source')[0]
			StartDate = filecoins[id]['StartDate'].split('/')
			cc_coin.StartDate = datetime(int(StartDate[2]), int(StartDate[1]), int(StartDate[0]))
			cc_coin.save()
		print('updated: {} added: {}'.format(count_update, count_add))

	def cryptocompare_get_social(self, coinlist_file):
		file = open(DATADIR+'/'+coinlist_file, 'r')
		filecoins = json.load(file)
		file.close()

		current_date = timezone.now().strftime("%Y-%m-%d-%H-%M") #strftime("%Y-%m-%d-%H-%M-%S")
		print(current_date)
		file = open(DATADIR+'/social/'+current_date+'.txt', 'w')
		data={}
		counter=0
		for coin in filecoins:
			counter+=1
			id = filecoins[coin]['Id']
			print(id, coin, counter)
			url = 'https://www.cryptocompare.com/api/data/socialstats/?id='+id
			response = requests.get(url)
			temp = response.json()['Data']
			data[id]=temp
		json.dump(data, file)
		file.close()

	def coin_cryptocompare_update_social(self):
		list_of_files = glob.glob(DATADIR+'/social/*') # * means all if need specific format then *.csv
		latest_file = max(list_of_files, key=os.path.getctime)
		print (latest_file)

		file = open(latest_file, 'r')
		filecoins = json.load(file)
		file.close()

		count_twitter = 0
		count_reddit = 0
		count_all = 0
		for id in filecoins:
			count_all+=1
			#print(id) #for debug doublication
			cc_coin = CoinCryptocompare.objects.get(Id_cc = id)
			#twitter:
			twitter = filecoins[id]['Twitter']
			try:
				twitter_link = twitter['link']
				twitter_followers = twitter['followers']
				twitter_posts = twitter['statuses']
				print(id, filecoins[id]['General']['Name'], twitter_link, twitter_posts, twitter_followers)
				count_twitter+=1
				cc_coin.twitter_link = twitter_link
				cc_coin.twitter_followers = twitter_followers
				cc_coin.twitter_posts = twitter_posts
				#cc_coin.save()
			except:
				print(id, filecoins[id]['General']['Name'],' no twitter link')
			#Reddit:
			reddit = filecoins[id]['Reddit']
			try:
				reddit_link = reddit['link']
				reddit_subscribers = reddit['subscribers']
				reddit_active_users = reddit['active_users']
				reddit_posts_per_day = float(reddit['posts_per_day'])
				reddit_comments_per_day = reddit['comments_per_day']
				print(id, filecoins[id]['General']['Name'], reddit_link, reddit_subscribers, reddit_active_users, reddit_posts_per_day, reddit_comments_per_day)
				#print(reddit_posts_per_day, type(reddit_posts_per_day))
				cc_coin.reddit_link = reddit_link
				cc_coin.reddit_subscribers = reddit_subscribers
				cc_coin.reddit_active_users = reddit_active_users
				cc_coin.reddit_posts_per_day = reddit_posts_per_day
				cc_coin.reddit_comments_per_day = reddit_comments_per_day
				count_reddit+=1
				#cc_coin.save()
			except:
				print(id, filecoins[id]['General']['Name'],' no reddit link')
			cc_coin.save()

		print('all:{} twitter:{} reddit:{}'.format(count_all, count_twitter, count_reddit))

################# end Cryptocompare snapshot and social functions ######################


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

	def exchange_pairs(self, action='update'):
		#get and save data to file
		url='https://min-api.cryptocompare.com/data/all/exchanges'
		response = requests.get(url)
		data = response.json()
		current_date = timezone.now().strftime("%Y-%m-%d-%H-%M") #strftime("%Y-%m-%d-%H-%M-%S")
		print(current_date)
		file = open(DATADIR+'/pairs/'+current_date+'.txt', 'w', encoding='utf8')
		json.dump(data, file)
		file.close()

		#open file to results
		file_result = open(DATADIR+'/pairs/'+FILE_EXCHANGE_PAIRS, 'a')

		#add exchange or update coinlist in exchange
		coins=0
		pairs=0
		max_len = 0

		dbcoins = set(Coin.objects.values_list('symbol', flat=True))
		#print('length:',len(dbcoins),dbcoins)

		for exchange in data:
			#print(exchange,len(data[exchange]))
			coins+=len(data[exchange])
			coinlist=[]
			for ex_pairs in data[exchange]:
				#print(data[exchange][ex_pairs])
				pairs+=len(data[exchange][ex_pairs])
				coinlist.append(ex_pairs)
			coinset = set(coinlist) #all coins need unique
			#check coins in db and remove
			count_before=len(coinlist)
			coinlist = [coin for coin in coinset if coin in dbcoins]

			#print(notfound,' not found in db for exchange ', exchange)
			json_coinlist = json.dumps(coinlist) #list to string
			length = len(json_coinlist) #string length
			count = len(coinlist) #coins count
			#if exchange=='Yobit' or exchange=='Poloniex' or exchange=='Etherdelta':
			print(exchange, 'before:', count_before, 'after:', count, length)
			if length>max_len:
				max_len=length
			try: #get exchange
				dbexchange = Exchange.objects.get(exchange=exchange)
			except: #new exchange
				dbexchange = Exchange()
				dbexchange.exchange = exchange
				dbexchange.coinlist = json_coinlist
				dbexchange.coinlist_update='[]'
				dbexchange.count = count
				dbexchange.save()
				text = 'new exchange found: {} new: {}\n'.format(exchange, dbexchange.coinlist)
				print(text)
				file_result.write(text)
				continue
			if count>dbexchange.count:
				#coinlist_update
				current_list = json.loads(dbexchange.coinlist)
				update_list = list(set(coinlist) - set(current_list))
				#print(exchange, current_list, coinlist, update_list)
				coinlist_update = json.loads(dbexchange.coinlist_update)
				update_list.extend(coinlist_update)
				#print(update_list, type(update_list))
				dbexchange.coinlist_update = json.dumps(update_list) #write update list to db
				#coinlist and count
				dbexchange.coinlist = json_coinlist
				dbexchange.count = count
				dbexchange.save()
				text = 'updates found in exchange: {} new: {}\n'.format(exchange, dbexchange.coinlist_update)
				print(text)
				file_result.write(text)
		
		text = 'exchanges: {} ex_coins: {} ex_pairs: {} max length: {}\n'.format(len(data), coins, pairs, max_len)
		print(text)
		file_result.write(text)
		file_result.close()

		#create news:

########### coingecko ##############
#https://api.coingecko.com/api/v3/coins/list - List all supported coins id, name and symbol (no pagination required)
#https://api.coingecko.com/api/v3/coins/{id} - Get current data (name, price, market, … including exchange tickers) for a coin
	def coingecko_export(self):
		geckocoins = CoinGecko.objects.values()
		coinlist = []
		for geckocoin in geckocoins:
			coinsymbol = Coin.objects.get(id=geckocoin['coinid_id'])
			geckocoin['coinid_id']=coinsymbol.symbol
			coinlist.append(geckocoin)
			print(geckocoin)
		file = open(DATADIR+'/coingecko/export.txt', 'w', encoding='utf8')
		json.dump(coinlist, file)
		file.close()
		print('coins in list: ',len(coinlist))

	def coingecko_import(self):
		file = open(DATADIR+'/coingecko/export.txt', 'r')
		filecoins = json.load(file)
		file.close()
		count_saved=0
		for filecoin in filecoins:
			#print(filecoin)
			try: 
				dbcoin = Coin.objects.get(symbol=filecoin['coinid_id']) #get Coin by symbol from file
				geckocoin = CoinGecko(coinid=dbcoin)
				geckocoin.coinidname = dbcoin.name
				geckocoin.symbol = filecoin['symbol']
				geckocoin.name = filecoin['name']
				geckocoin.geckoid = filecoin['geckoid']
				geckocoin.save()
				count_saved+=1
			except Exception as error:
				print('not saved:', filecoin, 'error:', error)
		print('file coins:',len(filecoins),'saved:', count_saved)

	def coingecko_get(self):
		#this coins no add
		excepted = [
			'acchain',
			'ace',
			'bowhead-health',
			'applecoin',
			'arbitraging',
			'arcade-token',
			'aston',
			'b2bcoin',
			'blue',
			'capital',
			'cash-poker-pro',
			'cibus',
			'consensus',
			'corethum',
			'cybereits',
			'daostack',
			'first-bitcoin',
			'global-tour-coin',
			'harmonycoin',
			'hydro-protocol',
			'inchain',
			'invacio',
			'key-token',
			'link-platform',
			'marinecoin',
			'multiven',
			'natcoin',
			'neptunecoin',
			'pally',
			'piecoin',
			'pointium',
			'prcoin',
			'sakura-bloom',
			'sigame',
			'smarto',
			'sp8de',
			'sphere-social',
			'strikebitclub',
			'swishcoin',
			'tokenstars-team',

		]
		#K check

		url='https://api.coingecko.com/api/v3/coins/list'
		response = requests.get(url)
		data = response.json()
		file = open(DATADIR+'/coingecko/list.txt', 'w', encoding='utf8')
		json.dump(data, file)
		file.close()
		#get db Coin:
		dbcoins = list(Coin.objects.values_list('symbol','name'))
		#get db CoinGecko:
		#geckocoins = CoinGecko.objects.all()

		print('coins in db:',len(dbcoins))
		#stats:
		print('coins in coingecko:',len(data))#1909 at 02.06.2018
		data = sorted(data, key=lambda k: k['symbol'])
		count_found = 0 #in gecko
		count_notfound = 0 #in gecko
		saved = 0 #saved in gecko
		savedlist = []
		for item in data:
			if item['id'] in excepted:
				print(item,' excepted')
				try:
					geckocoin = CoinGecko.objects.get(geckoid=item['id'])
					geckocoin.delete()
				except Exception as error:
					pass
					#print(error, item)
				continue
			try:
				geckocoin = CoinGecko.objects.get(geckoid=item['id'])
				count_found+=1
			except:
				count_notfound+=1
				#print('item {} not found in gecko db'.format(item))
				symbol = item['symbol'].upper()
				#search item in dbcoins
				try:
					dbcoin = Coin.objects.get(symbol=symbol)
					print('found in coin db:',dbcoin,'item:',item)
					geckocoin = CoinGecko(coinid=dbcoin)
					#geckocoin.coinid = dbcoin.id
					geckocoin.coinidname = dbcoin.name
					geckocoin.symbol = item['symbol']
					geckocoin.name = item['name']
					geckocoin.geckoid = item['id']
					geckocoin.save()
					saved+=1
					print('saved:',item)
					savedlist.append(item)
				except Exception as error:
					pass
					#print(error, '--------',symbol)
					#print('symbol {} not found in coin db'.format(symbol))

			continue
			#https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd


			# symbol = item['symbol'].upper()
			# found=False
			# for dbcoin in dbcoins:
			# 	if symbol == dbcoin[0]:
			# 		dbsymbol = dbcoin[0]
			# 		dbname = dbcoin[1]
			# 		found = True
			# 		break
			# if found:
			# 	count_found+=1
			# 	print ('gecko:',item['symbol'],item['name'],'db:',item['id'], dbsymbol, dbname)
			# else:
			# 	count_notfound+=1
			# 	print ('------ not found in db -------- gecko:',item['symbol'],item['name'],item['id'])
		print('found: {} not found: {} saved: {}'.format(count_found, count_notfound, saved))
		print(savedlist)
		#open file to results
		file_result = open(DATADIR+'/coingecko/saveresult.txt', 'a')
		file_result.write('current time:{}\n'.format(timezone.now()))
		file_result.write('coins in db:{} coins in coingecko:{}\n'.format(len(dbcoins),len(data)))
		file_result.write('found: {} not found: {} saved: {}\n'.format(count_found, count_notfound, saved))
		json.dump(savedlist, file_result)
		file_result.close()

	def coingecko_getall(self):
		geckocoins = CoinGecko.objects.all()
		count=0
		for geckocoin in geckocoins:
			try:
				id = geckocoin.geckoid
				url='https://api.coingecko.com/api/v3/coins/'+id
				response = requests.get(url)
				data = response.json()
				file = open(DATADIR+'/coingecko/all/'+id+'.txt', 'w', encoding='utf8')
				json.dump(data, file)
				file.close()
				count+=1
				print(id, count)
			except Exception as error:
				print(id, error)

	def coingecko_update(self):
		geckocoins = CoinGecko.objects.all()
		for geckocoin in geckocoins:
			id = geckocoin.geckoid
			file = open(DATADIR+'/coingecko/all/'+id+'.txt', 'r')
			filecoin = json.load(file)
			file.close()
			#print(filecoin['categories'])
			#print(id)
			try:
				market=filecoin['market_data']
				geckocoin.p24h = float(market['price_change_percentage_24h'])
				geckocoin.p7d  = float(market['price_change_percentage_7d'])
				geckocoin.p14d = float(market['price_change_percentage_14d'])
				geckocoin.p30d = float(market['price_change_percentage_30d'])
				geckocoin.circulating_supply=float(market['circulating_supply'])
				geckocoin.coingecko_score = filecoin['coingecko_score']
				geckocoin.current_price = float(market['current_price']['usd'])
				geckocoin.market_cap = float(market['market_cap']['usd'])
				geckocoin.total_volume = float(market['total_volume']['usd'])
				#developer_score = filecoin['developer_score']
				#community_score = filecoin['community_score']
				#liquidity_score = filecoin['liquidity_score']
				#public_interest_score = filecoin['public_interest_score']
				#p60d = float(market['price_change_percentage_60d'])
				#---print('name:{} 1d:{} 7d:{} 14d:{} 30d:{} 60d:{}'.format(id, p24h, p7d, p14d, p30d, p60d))
				#print('name:{} 1d:{} 7d:{} 30d:{}'.format(id, p24h, p7d, p30d))
				#print(id, supply)
				'''
				  "market_cap_rank": 71,
				  "coingecko_rank": 60,
				  "coingecko_score": 53.099,
				  "developer_score": 70.438,
				  "community_score": 42.495,
				  "liquidity_score": 53.328,
				  "public_interest_score": 30.637,
				  "community_data": {
				    "facebook_likes": 59192,
				    "twitter_followers": 841,
				    "reddit_average_posts_48h": 0.111,
				    "reddit_average_comments_48h": 0.556,
				    "reddit_subscribers": 4672,
				    "reddit_accounts_active_48h": 987
				  },
				  "developer_data": {
				    "forks": 130,
				    "stars": 411,
				    "subscribers": 70,
				    "total_issues": 20,
				    "closed_issues": 12,
				    "pull_requests_merged": 170,
				    "pull_request_contributors": 5,
				    "commit_count_4_weeks": 30
				  },
				'''
				geckocoin.save()
			except Exception as error:
				print(id, error)
			'''
			tickers = filecoin['tickers']
			#print(id, len(tickers))
			for ticker in tickers:
				#print(ticker)
				base = ticker['base']
				target = ticker['target']
				market = ticker['market']['name']
				#print(market+': '+base+'/'+target)
			'''
			


####################################


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

		if 'daily' in poll_id:
			index = poll_id.index('daily')
			try:
				action = poll_id[index+1]
			except Exception:
				action = 'all'
			self.cryptocompare_get_DOHLCV(action)

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

		if 'coinsnapshot' in poll_id:
			self.cryptocompare_get_snapshot(FILE_COINLIST, FILE_SNAPSHOT_CC)
		
		if 'coinsnapshot_print' in poll_id:
			file = open(DATADIR+'/'+FILE_SNAPSHOT_CC, 'r')
			coins = json.load(file)
			file.close()
			for id in coins:
				coin = coins[id]
				print(id, coin['Symbol'], coin['Name'], coin['WebsiteUrl'], coin['StartDate'])
				#print(id,coin['WebsiteUrl'].split('?')[0])
				#if coin['WebsiteUrl'].split('?utm_source')[0]!=coin['WebsiteUrl']:
				#	print (coin['WebsiteUrl'])
				#cc_coin = CoinCryptocompare.objects.get(Id_cc = id)
				#print(cc_coin)
			a = [id for id in coins]
			#print(a)
			b =  [item for item, count in collections.Counter(a).items() if count > 1]
			print('dublication:', b)


		if 'coinsnapshot_update' in poll_id:
			self.coin_cryptocompare_update(FILE_SNAPSHOT_CC)

		if 'coinsocial' in poll_id:
			self.cryptocompare_get_social(FILE_COINLIST)

		if 'coinsocial_update' in poll_id:
			self.coin_cryptocompare_update_social()

		if 'exchange_pairs' in poll_id:
			self.exchange_pairs() #execute

		if 'coingecko_get' in poll_id:
			self.coingecko_get()

		if 'coingecko_export' in poll_id:
			self.coingecko_export()

		if 'coingecko_import' in poll_id:
			self.coingecko_import()

		if 'coingecko_getall' in poll_id:
			self.coingecko_getall()

		if 'coingecko_update' in poll_id:
			self.coingecko_update()
		










