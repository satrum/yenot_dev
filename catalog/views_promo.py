#need to do:
#1. add user to Banner
#2. add email to user and admin
#3. add external prices for promo
#4. modify structure of form
#5. modify css of form
#6. price in template from YeenotSettings (calculation or table)

#YeenotSettings promo price initialization:
from .models import YeenotSettings
def promo_price():
	obj, created = YeenotSettings.objects.get_or_create(name='price_promo_news')
	if created:
		obj.num_value = 10
		obj.save()
	obj, created = YeenotSettings.objects.get_or_create(name='price_promo_source_day')
	if created:
		obj.num_value = 4
		obj.save()
	obj, created = YeenotSettings.objects.get_or_create(name='price_promo_source_week')
	if created:
		obj.num_value = 20
		obj.save()
	obj, created = YeenotSettings.objects.get_or_create(name='price_promo_source_month')
	if created:
		obj.num_value = 80
		obj.save()
	obj, created = YeenotSettings.objects.get_or_create(name='price_promo_banner_day')
	if created:
		obj.num_value = 10
		obj.save()
	obj, created = YeenotSettings.objects.get_or_create(name='price_promo_banner_week')
	if created:
		obj.num_value = 50
		obj.save()
	obj, created = YeenotSettings.objects.get_or_create(name='price_promo_banner_month')
	if created:
		obj.num_value = 200
		obj.save()
	return YeenotSettings.objects.all()

#create promo task from base Modelform:
from django.forms import ModelForm
from .models import News, Source, Banner, Promo_task
from django.shortcuts import render, redirect

class AddPromoModelForm(ModelForm):
	class Meta:
		model = Promo_task
		fields = ['type','newsid','sourceid','bannerid','param']
	#sources only moderated:
	def __init__(self, user, *args, **kwargs):
		#print(kwargs)
		#user = kwargs.pop('user', None)
		super(AddPromoModelForm, self).__init__(*args, **kwargs)
		#print(user)
		self.fields['sourceid'].queryset = Source.objects.filter(user=user, promo_status='n') #and promo status no 'Promoted'
		self.fields['newsid'].queryset = News.objects.filter(user=user, promo_status='n') #and promo status no 'Promoted'
		self.fields['bannerid'].queryset = Banner.objects.filter(status=False) #and promo status no 'Promoted' and only user banner
		#print(self.fields['newsid'].queryset)

from django.contrib.auth.decorators import login_required
#from django.core import mail
#import requests
#import json

@login_required
def addpromo(request):
	if request.method == 'POST':
		form = AddPromoModelForm(request.user, request.POST)
		'''
		print(form.fields['newsid'].queryset)
		newsid = request.POST.get('newsid')
		form.fields['newsid'].queryset = [(newsid, newsid)]
		print(form.fields['newsid'].queryset)
		print(form.fields['newsid'])
		'''
		if form.is_valid():
			extend_form = form.save(commit=False)
			extend_form.user = request.user
			# !!!need get price from external settings
			if extend_form.type == 'n':
				price = YeenotSettings.objects.get(name='price_promo_news').num_value
			elif extend_form.type == 's':
				if extend_form.param == 'w':
					price = YeenotSettings.objects.get(name='price_promo_source_week').num_value
				elif extend_form.param == 'm':
					price = YeenotSettings.objects.get(name='price_promo_source_month').num_value
				elif extend_form.param == 'd':
					price = YeenotSettings.objects.get(name='price_promo_source_day').num_value
			elif extend_form.type == 'b':
				if extend_form.param == 'w':
					price = YeenotSettings.objects.get(name='price_promo_banner_week').num_value
				elif extend_form.param == 'm':
					price = YeenotSettings.objects.get(name='price_promo_banner_month').num_value
				elif extend_form.param == 'd':
					price = YeenotSettings.objects.get(name='price_promo_banner_day').num_value
			extend_form.price = price
			#save
			extend_form.save()
			return redirect('profile')
	else:
		form = AddPromoModelForm(request.user)
		'''
		yeenotsettings = promo_price() #get settings and create prices in model if not exist
		form.price_promo_news = yeenotsettings.get(name='price_promo_news').num_value
		form.price_promo_source_day = yeenotsettings.get(name='price_promo_source_day').num_value
		form.price_promo_source_week = yeenotsettings.get(name='price_promo_source_week').num_value
		form.price_promo_source_month = yeenotsettings.get(name='price_promo_source_month').num_value
		form.price_promo_banner_day = yeenotsettings.get(name='price_promo_banner_day').num_value
		form.price_promo_banner_week = yeenotsettings.get(name='price_promo_banner_week').num_value
		form.price_promo_banner_month = yeenotsettings.get(name='price_promo_banner_month').num_value
		'''
	return render(request, 'addpromo.html', {'form': form})	#need modify template structure and price calculation