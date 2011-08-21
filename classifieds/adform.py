"""
  $Id$

Django ModelForms compatible class to provide database driven form structure.

Django's ModelForms provides a way to automatically generate forms from django
Models (which are representations of database tables and relationships).
We need the ability to describe the details (such as the widget type) for
multiple fields across several forms.

Our model for this consists of a 'category' with one or more fields. Each
field then has zero or more field values, where the value corresponds to a
value submitted via one of our forms.

The model for the 'ad', which is what the field values are for, has several
fields. None of those fields except for 'title' will be part of the generated
forms.

"""

from django.utils.datastructures import SortedDict
from django.forms.util import ErrorList
from django.utils.translation import ugettext as _
from django.forms import BaseForm
from django import forms

from classifieds.conf import settings
from classifieds.models import Field, FieldValue

__all__ = ('AdForm',)

import HTMLParser
import string


class StrippingParser(HTMLParser.HTMLParser):
    # These are the HTML tags that we will leave intact
    valid_tags = ('b', 'i', 'br', 'p', 'strong', 'h1', 'h2', 'h3', 'em',
                  'span', 'ul', 'ol', 'li')

    from htmlentitydefs import entitydefs  # replace entitydefs from sgmllib

    def __init__(self):
        HTMLParser.HTMLParser.__init__(self)
        self.result = ""
        self.endTagList = []

    def handle_data(self, data):
        if data:
            self.result = self.result + data

    def handle_charref(self, name):
        self.result = "%s&#%s;" % (self.result, name)

    def handle_entityref(self, name):
        if name in self.entitydefs:
            x = ';'
        else:
            # this breaks unstandard entities that end with ';'
            x = ''
            self.result = "%s&%s%s" % (self.result, name, x)

    def handle_starttag(self, tag, attrs):
        """ Delete all tags except for legal ones """
        if tag in self.valid_tags:
            self.result = self.result + '<' + tag
            for k, v in attrs:
                if string.lower(k[0:2]) != 'on' and \
                   string.lower(v[0:10]) != 'javascript':
                    self.result = '%s %s="%s"' % (self.result, k, v)

            endTag = '</%s>' % tag
            self.endTagList.insert(0, endTag)
            self.result = self.result + '>'

        def handle_endtag(self, tag):
            if tag in self.valid_tags:
                self.result = "%s</%s>" % (self.result, tag)
                remTag = '</%s>' % tag
                self.endTagList.remove(remTag)

        def cleanup(self):
            """ Append missing closing tags """
            for j in range(len(self.endTagList)):
                self.result = self.result + self.endTagList[j]


def strip(s):
    """ Strip illegal HTML tags from string s """
    parser = StrippingParser()
    parser.feed(s)
    parser.close()
    parser.cleanup()
    return parser.result


class TinyMCEWidget(forms.Textarea):
    def __init__(self, *args, **kwargs):
        attrs = kwargs.setdefault('attrs', {})
        if 'class' not in attrs:
            attrs['class'] = 'tinymce'
        else:
            attrs['class'] += ' tinymce'

        super(TinyMCEWidget, self).__init__(*args, **kwargs)

    class Media:
        js = ('js/tiny_mce/tiny_mce.js', 'js/tinymce_forms.js',)


from django.forms.fields import EMPTY_VALUES
import re


class TinyMCEField(forms.CharField):
    def clean(self, value):
        """Validates max_length and min_length. Returns a Unicode object."""
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
            raise forms.ValidationError(self.error_messages['max_length'] % {'max': self.max_length, 'length': value_length})
        if self.min_length is not None and value_length < self.min_length:
            raise forms.ValidationError(self.error_messages['min_length'] % {'min': self.min_length, 'length': value_length})

        return value


def field_list(instance):
    class MockField:
        def __init__(self, name, field_type, label, required, help_text, enable_wysiwyg, max_length):
            self.name = name
            self.field_type = field_type
            self.label = label
            self.required = required
            self.help_text = help_text
            self.enable_wysiwyg = enable_wysiwyg
            self.max_length = max_length

    title_field = MockField('title', Field.CHAR_FIELD, _('Title'), True, '', False, 100)

    fields = [title_field]  # all ads have titles
    fields += list(instance.category.field_set.all())
    fields += list(Field.objects.filter(category=None))
    return fields


def fields_for_ad(instance):
    # generate a sorted dict of fields corresponding to the Field model
    # for the Ad instance
    fields_dict = SortedDict()
    fields = field_list(instance)
    # this really could be refactored
    for field in fields:
        if field.field_type == Field.BOOLEAN_FIELD:
            fields_dict[field.name] = forms.BooleanField(label=field.label, required=False, help_text=field.help_text)
        elif field.field_type == Field.CHAR_FIELD:
            widget = forms.TextInput
            fields_dict[field.name] = forms.CharField(label=field.label, required=field.required, max_length=field.max_length, help_text=field.help_text, widget=widget)
        elif field.field_type == Field.DATE_FIELD:
            fields_dict[field.name] = forms.DateField(label=field.label, required=field.required, help_text=field.help_text)
        elif field.field_type == Field.DATETIME_FIELD:
            fields_dict[field.name] = forms.DateTimeField(label=field.label, required=field.required, help_text=field.help_text)
        elif field.field_type == Field.EMAIL_FIELD:
            fields_dict[field.name] = forms.EmailField(label=field.label, required=field.required, help_text=field.help_text)
        elif field.field_type == Field.FLOAT_FIELD:
            fields_dict[field.name] = forms.FloatField(label=field.label, required=field.required, help_text=field.help_text)
        elif field.field_type == Field.INTEGER_FIELD:
            fields_dict[field.name] = forms.IntegerField(label=field.label, required=field.required, help_text=field.help_text)
        elif field.field_type == Field.TIME_FIELD:
            fields_dict[field.name] = forms.TimeField(label=field.label, required=field.required, help_text=field.help_text)
        elif field.field_type == Field.URL_FIELD:
            fields_dict[field.name] = forms.URLField(label=field.label, required=field.required, help_text=field.help_text)
        elif field.field_type == Field.SELECT_FIELD:
            options = field.options.split(',')
            fields_dict[field.name] = forms.ChoiceField(label=field.label, required=field.required, help_text=field.help_text, choices=zip(options, options))
        elif field.field_type == Field.TEXT_FIELD:
            if field.enable_wysiwyg:
                widget = TinyMCEWidget
                field_type = TinyMCEField
            else:
                widget = forms.Textarea
                field_type = forms.CharField

            fields_dict[field.name] = field_type(label=field.label, required=field.required, help_text=field.help_text, max_length=field.max_length, widget=widget)

    return fields_dict


def ad_to_dict(instance):
    # generate a dict of field => value pairs for the FieldValue model
    # for the Ad instance
    fields_dict = {}
    fields = field_list(instance)
    for field in fields:
        if field.name == 'title':
            fields_dict['title'] = instance.title
        else:
            try:
                fields_dict[field.name] = field.fieldvalue_set.get(ad=instance).value
            except FieldValue.DoesNotExist:
                pass

    return fields_dict


class AdForm(BaseForm):
    def __init__(self, instance, data=None, files=None, auto_id='id_%s', prefix=None,
                             initial=None, error_class=ErrorList, label_suffix=':',
                             empty_permitted=False):

        self.instance = instance
        object_data = ad_to_dict(self.instance)
        self.declared_fields = SortedDict()
        self.base_fields = fields_for_ad(self.instance)

        # if initial was provided, it should override the values from instance
        if initial is not None:
            object_data.update(initial)

        BaseForm.__init__(self, data, files, auto_id, prefix, object_data,
                          error_class, label_suffix, empty_permitted)

    def save(self, commit=True):
        if not commit:
            raise NotImplementedError("AdForm.save must commit it's changes.")

        if self.errors:
            raise ValueError("The ad could not be updated because the data didn't validate.")

        cleaned_data = self.cleaned_data

        # save fieldvalues for self.instance
        fields = field_list(self.instance)

        for field in fields:
            if field.enable_wysiwyg:
                value = unicode(strip(cleaned_data[field.name]))
            else:
                value = unicode(cleaned_data[field.name])

            # strip words in settings.FORBIDDEN_WORDS
            for word in settings.FORBIDDEN_WORDS:
                value = value.replace(word, '')

            # title is stored directly in the ad, unlike all other editable fields
            if field.name == 'title':
                self.instance.title = value
                self.instance.save()
            else:
                # check to see if field.fieldvalue_set has a value with ad=self.instance
                try:
                    # if it does, update
                    fv = field.fieldvalue_set.get(ad=self.instance)
                except FieldValue.DoesNotExist:
                    # otherwise, create a new one
                    fv = field.fieldvalue_set.create(ad=self.instance)

                # XXX some ugly price fixing
                if field.name.endswith('price'):
                    m = re.match('^\$?(\d{1,3},?(\d{3},?)*\d{3}(\.\d{0,2})?|\d{1,3}(\.\d{0,2})?|\.\d{1,2}?)$', value)
                    value = m.group(1)
                    value.replace(',', '')
                    value = '%.2f' % float(value)

                fv.value = value
                fv.save()

        return self.instance
