"""
  $Id$
"""
from django import template

register = template.Library()

from django.template.defaultfilters import stringfilter

import string

@stringfilter
def sortname(value):
	value = value.replace('type', '_type')
	value = value.replace('job', 'job_')
	value = value.replace('id', 'ad_ID')
	words = value.split('_')
	return string.join(words).title()

register.filter('sortname', sortname)

