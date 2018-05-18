from django.contrib.auth.models import User

#reddit pipeline:
def update_user(backend, user, response, *args, **kwargs):
	#print('backend:')
	#print(backend, backend.name)
	#print('user:')
	#print(user)
	if backend.name == 'reddit':
		#print('need update first name for reddit')
		account = User.objects.get(username=user)
		#print('user:', account.username, 'name:',account.first_name, 'details:', kwargs['details']['username'])
		if account.first_name == '':
			print('empty first name, need update first name for reddit')
			account.first_name = kwargs['details']['username']
			account.save()
	#print('response:')
	#print(response)