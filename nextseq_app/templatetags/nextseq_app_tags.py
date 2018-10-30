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


@register.filter
def humantitle(oldtitle):
	titlechange = {
		'jobstatus': 'Demultiplexing Status',
		'set_id': 'Set ID',
		'set_name':'Title',

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
        return str(value)+"%"
