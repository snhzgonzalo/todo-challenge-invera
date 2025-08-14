from django import template
from django.utils.dateparse import parse_datetime
from django.utils.timezone import localtime

register = template.Library()

@register.filter
def local_dt(value):
    dt = parse_datetime(value) if isinstance(value, str) else value
    return localtime(dt).strftime("%d-%m-%Y %H:%M") if dt else ""