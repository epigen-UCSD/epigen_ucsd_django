from django import template

register = template.Library()


@register.filter
def key(d, key_name):
	if key_name:
		return d[str(key_name)]
	else:
		return ''
