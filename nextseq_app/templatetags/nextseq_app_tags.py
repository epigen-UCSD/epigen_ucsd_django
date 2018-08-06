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
	