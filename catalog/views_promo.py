#need to do:
#1. add user to Banner
#2. add email to user and admin
#3. add external prices for promo
#4. modify structure of form
#5. modify css of form
#6. price in template from YeenotSettings (calculation or table)

#create news from base Modelform:
from django.forms import ModelForm
from .models import News, Source, Banner, Promo_task
from django.shortcuts import render, redirect

class AddPromoModelForm(ModelForm):
	class Meta:
		model = Promo_task
		fields = ['type','newsid','sourceid','bannerid','param']
	#sources only moderated:
	def __init__(self, *args, **kwargs):
		#print(kwargs)
		user = kwargs.pop('user', None)
		super(AddPromoModelForm, self).__init__(*args, **kwargs)
		#print(user)
		self.fields['sourceid'].queryset = Source.objects.filter(user=user, promo_status='n') #and promo status no 'Promoted'
		self.fields['newsid'].queryset = News.objects.filter(user=user, promo_status='n') #and promo status no 'Promoted'
		self.fields['bannerid'].queryset = Banner.objects.filter(status=False) #and promo status no 'Promoted' and only user banner

from django.contrib.auth.decorators import login_required
#from django.core import mail
#import requests
#import json

@login_required
def addpromo(request):
	if request.method == 'POST':
		form = AddPromoModelForm(request.POST)
		if form.is_valid():
			extend_form = form.save(commit=False)
			extend_form.user = request.user
			# !!!need get price from external settings
			if extend_form.type == 'n':
				price = 10
			elif extend_form.type == 's':
				if extend_form.param == 'w':
					price = 20
				elif extend_form.param == 'm':
					price = 80
			elif extend_form.type == 'b':
				if extend_form.param == 'w':
					price = 50
				elif extend_form.param == 'm':
					price = 200
			extend_form.price = price
			#save
			extend_form.save()
			return redirect('profile')
	else:
		form = AddPromoModelForm(user=request.user)
	return render(request, 'addpromo.html', {'form': form})	#need modify template structure and price calculation