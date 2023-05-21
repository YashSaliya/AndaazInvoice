from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()

@register.filter
def get_item(dictionary, key):
    return str(dictionary.get(key))

@register.filter
@stringfilter
def replace(value):
    if value == '1':
        return "Breakfast"
    elif value == '2':
        return 'Lunch'
    else:
        return 'Dinner'


@register.filter
def getStringValue(value):
    if value:
        return "Paid"
    return "Due"