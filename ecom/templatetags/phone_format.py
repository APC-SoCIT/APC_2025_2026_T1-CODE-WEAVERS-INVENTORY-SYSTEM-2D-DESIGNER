from django import template
import re

register = template.Library()

def format_ph_mobile(value):
    """
    Formats a Philippine mobile number as '0956 837 0169'.
    Accepts numbers with or without spaces, dashes, or country code.
    """
    if not value:
        return ''
    # Convert value to string to avoid TypeError
    value_str = str(value)
    # Remove all non-digit characters
    digits = re.sub(r'\D', '', value_str)
    # Remove leading country code if present
    if digits.startswith('63'):
        digits = '0' + digits[2:]
    if len(digits) == 11:
        return f"{digits[:4]} {digits[4:7]} {digits[7:]}"
    return value

@register.filter(name='ph_mobile_format')
def ph_mobile_format(value):
    return format_ph_mobile(value)
