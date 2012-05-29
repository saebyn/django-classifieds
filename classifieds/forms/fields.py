
from django.forms import CharField, ValidationError
from django.forms.fields import EMPTY_VALUES

import re, string

class TinyMCEField(CharField):
    def clean(self, value):
        "Validates max_length and min_length. Returns a Unicode object."
        if value in EMPTY_VALUES:
            return u''
        
        stripped_value = re.sub(r'<.*?>', '', value)
        stripped_value = string.replace(stripped_value, '&nbsp;', ' ')
        stripped_value = string.replace(stripped_value, '&lt;', '<')
        stripped_value = string.replace(stripped_value, '&gt;', '>')
        stripped_value = string.replace(stripped_value, '&amp;', '&')
        stripped_value = string.replace(stripped_value, '\n', '')
        stripped_value = string.replace(stripped_value, '\r', '')
        
        value_length = len(stripped_value)
        value_length -= 1
        if self.max_length is not None and value_length > self.max_length:
            raise ValidationError(self.error_messages['max_length'] % {'max': self.max_length, 'length': value_length})
        if self.min_length is not None and value_length < self.min_length:
            raise ValidationError(self.error_messages['min_length'] % {'min': self.min_length, 'length': value_length})
        
        return value
