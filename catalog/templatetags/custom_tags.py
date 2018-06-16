from django import template

register = template.Library()

@register.filter
def sizeoffmt(num):
    print(num, type(num))
    num = float(num)
    for unit in ['','K','M','B']:
        if abs(num) < 1000.0:
            return "{0:3.2f} {1:}".format(num, unit)
        num = num / 1000.0
    return "{0:3.2f} {1:}".format(num, 'T')
	
''' for Bytes
def sizeoffmt(num, suffix='B'):
    for unit in ['','Ki','Mi','Gi','Ti','Pi','Ei','Zi']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num = num / 1024.0
    return "%.1f%s%s" % (num, 'Y', suffix)

{% load custom_tags %}
{{coin.mktcap|sizeoffmt}}
	'''


