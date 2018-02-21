#update_news_rating_test1
import os,sys
# print(os.getcwd())
# print(sys.argv)
from django.core.management.base import BaseCommand, CommandError
from catalog.models import News

import requests
import json
import os

FILE_COINLIST = 'coinlist.txt'
FILE_PRICE = 'coinpricefull.txt'
TYPE_PRICE = 'full'
DATADIR = 'data'
COINIMAGESDIR = 'media/coin_images/'

EXCLUDE_LIST = ['ARENA','CNO', 'BTH']

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

from django.db import models
from catalog.models import Coin

class Command(BaseCommand):

	def add_arguments(self, parser):
		parser.add_argument('poll_id', nargs='+', type=str)
	
	def help(self):
		print('parameters:')
		print('help - print this help')
		print('list_news - print list of all news')
		print('coinlist [filename=''coinlist.txt''] - get coin list from cryptocompare and write json to file')
		print('coinprint [filename=''coinlist.txt''] - read json from file and print ')
		print('coinprice [filename coinlist.txt] [filename coinpricefull.txt] [simple/full] - read json from file and get price and write json to file')
		print('coinlist_exclude - read full price, get coins with price, remove coins without from coinlist')
		print('coinimage - read from coinlist and update folder media/coin_images/ with images') #!!!!!!!
		print('coininfo [symbol] - read info about coin')
		print('coinadd [action - all, update, add]- read coinlist from file and update list on db model Coin - coin.id, coin.symbol, coin.name')
		print('update_cycle - coinprice + coinlist_exclude + coinadd update')
		print('--------need create or update:-----')
		print('coinprint_db - list info from Model Coin')
		print('coinpriceupdate - update fields in Model Coin - coin.price, coin.change, coin.volume, coin.mktcap')
		print('rate_news - calculate rating of news. Likes(Real)/Dislikes(Fake)/News_price/Current_price/Direction -> rating')
		print('full_cycle - coinlist + coinprice + coinlist_exclude + coinimage + coinadd full')


	def list_news(self):
		#get news ratings:
		news = News.objects.all()
		#print(type(news), news)
		for new in news:
			#print(new.newsid, new.title, new.rating, new.like, new.dislike, new.time)
			print(new.newsid, new.title, new.rating, new.like, new.dislike, new.sourceid, new.user)

	#'https://www.cryptocompare.com/api/data/coinlist/'
	#"DGB":{
	# "Id":"4430",
	# "Url":"/coins/dgb/overview",
	# "ImageUrl":"/media/12318264/7638-nty_400x400.jpg",
	# "Name":"DGB",
	# "Symbol":"DGB",
	# "CoinName":"DigiByte",
	# "FullName":"DigiByte (DGB)",
	# "Algorithm":"Multiple",
	# "ProofType":"PoW",
	# "FullyPremined":"0",
	# "TotalCoinSupply":"21000000000",
	# "PreMinedValue":"N/A",
	# "TotalCoinsFreeFloat":"N/A",
	# "SortOrder":"11",
	# "Sponsored":false}
	def cryptocompare_get_coinlist(self, filename):
		url1='https://www.cryptocompare.com/api/data/coinlist/'
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

		BATCHSIZE=50
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
		sets.append(names)

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
			print(temp)
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
		priced_coins = [ coin for coin in rawdata if 'MKTCAP' in rawdata[coin]['USD'] 
		and 'TOTALVOLUME24HTO' in rawdata[coin]['USD'] and rawdata[coin]['USD']['MKTCAP']!=0 and rawdata[coin]['USD']['TOTALVOLUME24HTO']!=0]
		#priced_coins = [ coin for coin in rawdata if 'MKTCAP' in rawdata[coin]['USD'] and rawdata[coin]['USD']['MKTCAP']!=0 ]
		print('coins from full price file with MKTCAP and TOTALVOLUME24HTO :',len(priced_coins))

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
					newdbcoin.save()
					count_add+=1
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
		
		if 'list_news' in poll_id:
			self.list_news()
		
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








