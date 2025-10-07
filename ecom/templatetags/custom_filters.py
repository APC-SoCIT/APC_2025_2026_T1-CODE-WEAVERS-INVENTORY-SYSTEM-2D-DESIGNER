from django import template
from ecom.utils import get_region_name, get_province_name, get_citymun_name, get_barangay_name

register = template.Library()

@register.filter
def multiply(value, arg):
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return ''

@register.filter
def region_name(value):
    """Convert region code to readable name"""
    try:
        return get_region_name(value) if value else value
    except:
        return value

@register.filter
def province_name(value):
    """Convert province code to readable name"""
    try:
        return get_province_name(value) if value else value
    except:
        return value

@register.filter
def citymun_name(value):
    """Convert city/municipality code to readable name"""
    try:
        return get_citymun_name(value) if value else value
    except:
        return value

@register.filter
def barangay_name(value):
    """Convert barangay code to readable name"""
    try:
        return get_barangay_name(value) if value else value
    except:
        return value