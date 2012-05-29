"""
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

import re

from classifieds.conf import settings
from classifieds.models import Field, FieldValue
from classifieds.utils import fields_for_ad, field_list, strip

__all__ = ('AdForm',)


class AdForm(BaseForm):
    def __init__(self, data=None, files=None, instance=None, auto_id='id_%s',
                 prefix=None, initial=None, error_class=ErrorList,
                 label_suffix=':', empty_permitted=False):

        if not instance:
            raise NotImplementedError("Ad instance must be provided")

        self.instance = instance
        object_data = self.instance.fields_dict()
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
            raise ValueError(_(u"The ad could not be updated because the data didn't validate."))

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

            # The title is stored directly in the ad,
            # unlike all other editable fields.
            if field.name == 'title':
                self.instance.title = value
                self.instance.save()
            else:
                # Check to see if field.fieldvalue_set has a value with
                # ad=self.instance
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
