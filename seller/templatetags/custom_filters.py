from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Custom template filter to get dictionary item using a key"""
    return dictionary.get(key, "")
