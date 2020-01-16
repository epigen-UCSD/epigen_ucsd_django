from django import template
register = template.Library()

@register.filter
def tuple_do(List, tupl):
    return List[ tupl[1] ]