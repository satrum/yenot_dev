from django.conf import settings # import the settings file

def context_yeenot(request):
    # return the value you want as a dictionnary. you may add multiple values in there.
    return {'GOOGLE_ANALYTICS_KEY': settings.GOOGLE_ANALYTICS_KEY}