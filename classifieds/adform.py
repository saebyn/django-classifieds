"""
  $Id$

Django ModelForms compatible class to provide database driven form structure.

Django's ModelForms provides a way to automatically generate forms from django Models
(which are representations of database tables and relationships). We need the 
ability to describe the details (such as the widget type) for multiple fields
across several forms.

Our model for this consists of a 'category' with one or more fields. Each field
then has zero or more field values, where the value corresponds to a value 
submitted via one of our forms.

"""

from django.utils.datastructures import SortedDict
from django.forms.util import ErrorList
from django.utils.translation import ugettext as _
from django.forms import BaseForm
from django import forms

from classifieds.conf import settings
from classifieds.models import Field, FieldValue
from classifieds.forms.widgets import TinyMCEWidget
from classifieds.forms.fields import TinyMCEField
from classifieds.utils import stripHTML

__all__ = ('AdForm',)

def field_list(instance):
    # TODO we need a "base" form that has "normal" fields in it
    # that applies to all ads (regardless of category) that we can
    # then add additional fields to.
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

    fields = [title_field] # all ads have titles
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
                value = unicode(stripHTML(cleaned_data[field.name]))
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

