from django import template
from django.contrib.auth.models import Group

register = template.Library()


@register.filter
def key(d, key_name):
	if key_name:
		return d[str(key_name)]
	else:
		return ''

@register.filter(name='has_group')
def has_group(user, group_name):
	group = Group.objects.get(name=group_name)
	return True if group in user.groups.all() else False

@register.filter(name='has_groups')
def has_groups(user, group_name_list):
	grouplist = group_name_list.split(';')
	return user.groups.filter(name__in=grouplist).exists()

@register.filter
def humantitle(oldtitle):
	titlechange = {
		'jobstatus': 'Status',
		'set_id': 'Set ID',
		'set_name':'Title',
		'nextseqdir':'Location',

	}
	if oldtitle in titlechange.keys():
		return titlechange[oldtitle]
	else:
		return oldtitle.title().replace('_',' ')

@register.filter
def get_value(obj, field_name):
	return getattr(obj,field_name)

@register.filter
def get_type(value):
    return type(value)

@register.filter
def get_class(ob):
    return ob.__class__.__name__

@register.filter
def percentage(value):
    if value:
        return str(value)+"%"
    else:
    	return str(value)


@register.filter
def linktrackingsheet(stringtext):
	linktrans = {
		'TrackingSheet 1':'<a href="https://docs.google.com/spreadsheets/d/1gjPViUOd-2CQVAIwGUinmqeKQThjJp2cixWogV4qkok/edit" target=”_blank”>TrackingSheet 1</a>',
		'TrackingSheet 2':'<a href="https://docs.google.com/spreadsheets/d/19Qjv05LZo6pazNIvGrfj9GDzmK6riOwF3eriW7Ufj1o/edit" target=”_blank”>TrackingSheet 2</a>',
		'TrackingSheet 3':'<a href="https://docs.google.com/spreadsheets/d/1DqQQ0e5s2Ia6yAkwgRyhfokQzNPfDJ6S-efWkAk292Y/edit" target=”_blank”>TrackingSheet 3</a>',

	}
	for k,v in linktrans.items():
		stringtext = stringtext.replace(k,v)
	return stringtext


