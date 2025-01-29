from django import template

register = template.Library()

@register.filter
def has_decimal_less_than_half(value):
    return (value - int(value)) < 0.5