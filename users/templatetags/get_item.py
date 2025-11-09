from django import template
register = template.Library()

@register.filter
def get_item(dictionary, key):
    try:
        return dictionary.get(key, 0)
    except:
        return 0
