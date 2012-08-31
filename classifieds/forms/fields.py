# vim: set fileencoding=utf-8 ft=python ff=unix nowrap tabstop=4 shiftwidth=4 softtabstop=4 smarttab shiftround expandtab :
"""
Form field classes for django-classifieds.
"""

from django.forms import CharField, ValidationError
from django.forms.fields import EMPTY_VALUES

import re


class TinyMCEField(CharField):
    def clean(self, value):
        """Validates max_length and min_length. Returns a Unicode object."""
        if value in EMPTY_VALUES:
            return u''

        # This stripping was done to ensure that the character count reflected
        # what the user sees when they type.
        # I don't remember why 1 is subtracted from this XXX
        value_length = len(re.sub(r'<.*?>', '', value)\
            .replace('&nbsp;', ' ')\
            .replace('&lt;', '<')\
            .replace('&gt;', '>')\
            .replace('&amp;', '&')\
            .replace('\n', '')\
            .replace('\r', '')) - 1

        if self.max_length is not None and value_length > self.max_length:
            raise ValidationError(self.error_messages['max_length'] % {'max': self.max_length, 'length': value_length})
        if self.min_length is not None and value_length < self.min_length:
            raise ValidationError(self.error_messages['min_length'] % {'min': self.min_length, 'length': value_length})

        return value
