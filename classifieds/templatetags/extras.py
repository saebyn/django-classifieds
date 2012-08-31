"""
"""

from django import template
from django.template.defaultfilters import stringfilter

import string


register = template.Library()


@stringfilter
def sortname(value):
    value = value.replace('type', '_type')
    value = value.replace('job', 'job_')
    value = value.replace('id', 'ad_id')
    words = value.split('_')
    return string.join(words).title()


register.filter('sortname', sortname)
