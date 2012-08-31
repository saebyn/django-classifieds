"""
"""

from django import forms
from django.contrib.localflavor.us import forms as us_forms
from django.utils.translation import ugettext as _

from classifieds.models import *


class PriceRangeForm(forms.Form):
    """
    A price range form.  It operates on
    forms that have the fields bottom_price
    and top_price
    """
    lowest = forms.DecimalField(label="Minimum Price", decimal_places=2)
    highest = forms.DecimalField(label="Maximum Price", decimal_places=2)

    def filter(self, qs):
        """
        Returns a new QuerySet with items in the given price range.
        Remember to validate this form (call is_valid()) before calling this
        function.
        """
        if not self.is_empty():
            range = (float(self.data["lowest"]), float(self.data["highest"]))
            fvs = FieldValue.objects.filter(field__name="price",
                                            value__range=range)
            validAds = [fv.ad.pk for fv in fvs]
            return qs.filter(pk__in=validAds)
        else:
            return qs

    @staticmethod
    def create(fieldList, fieldsLeft, response=None):
        if "price" in fieldsLeft:
            fieldsLeft.remove("price")
            if response != None:
                return PriceRangeForm({'lowest': response['lowest'][0],
                                       'highest': response['highest'][0]})
            else:
                return PriceRangeForm()
        else:
            return None

    def is_empty(self):
        return not ('lowest' in self.data and \
                    self.data["lowest"] != "" and \
                    'highest' in self.data and \
                    self.data["highest"] != "")


class ZipCodeForm(forms.Form):
    """
    A zip code form.  This operates on forms that have a zip_code field.
    """
    zip_code = us_forms.USZipCodeField(required=False, label=_("Zip Code"))
    zip_range = forms.DecimalField(required=False, label=_("Range (miles)"),
                                   initial="1")

    def filter(self, qs):
        """
        Returns a new QuerySet with only items in the given zip code.
        Remember to validate this form before calling this function.
        """
        if not self.is_empty():
            zip_code = self.cleaned_data['zip_code']
            radius = self.cleaned_data['zip_range']
            zipcodeObj = ZipCode.objects.get(zipcode=zip_code)
            zipcodes = [zipcode.zipcode for zipcode in zipcodeOb.nearby(radius)]

            fvs = FieldValue.objects.filter(field__name="zip_code")
            fvs = fvs.filter(value__in=list(zipcodes))

            validAds = [fv.ad.pk for fv in fvs]

            return qs.filter(pk__in=validAds)
        else:
            return qs

    @staticmethod
    def create(fields, fieldsLeft, response=None):
        """
        Creates a new ZipCodeForm if the given fieldsLeft list contains
        'zip_code'.  Pass a dictionary (i.e. from response.GET
        or response.POST) that contains a 'zip_code' key if you want
        to initialize this form.
        """
        if 'zip_code' in fieldsLeft:
            fieldsLeft.remove('zip_code')
            if response != None:
                return ZipCodeForm({'zip_code': response['zip_code'][0],
                                    'zip_range': response['zip_range'][0]})
            else:
                return ZipCodeForm()
        else:
            return None

    def is_empty(self):
        return not ('zip_code' in self.data and \
                    self.data["zip_code"] != "" and \
                    'zip_range' in self.data and \
                    self.data["zip_range"] != "")


class MultiForm(forms.Form):
    """
    A multiselect keyword search form.  This allows users
    to pick multiple fields to search in, and enter keywords
    to find in those fields.
    """
    keywords = forms.CharField(label='Keywords:', required=False)
    #criteria = forms.MultipleChoiceField(required=False,label='Other Criteria',choices=(("Fake Choice","1")))

    def is_empty(self):
        return not ('keywords' in self.data and self.data["keywords"] != "")
        # and self.data.has_key("criteria") and self.data["criteria"] != "")

    def filter(self, qs):
        """
        Returns a new QuerySet containing only items with at least
        one attribute that matches the user's keywords.
        """
        if not self.is_empty():
            # Create a set of all field value IDs
            allAdIDs = set()

            if 'title' in self.fieldNames:
                ad_title_qs = Ad.objects.filter(title__search=self.cleaned_data["keywords"])
                allAdIDs |= set([val.pk for val in ad_title_qs])

            fvs = set(FieldValue.objects.filter(value__search=self.cleaned_data["keywords"]))

            # Join the current set with this set
            allAdIDs |= set([val.ad.pk for val in fvs])

            return qs.filter(pk__in=list(allAdIDs))
        else:
            return qs

    @staticmethod
    def create(fields, fieldsLeft, response=None):
        """
        This creates a MultiForm from the given field list and,
        optionally, a response.  NOTE: It DOES NOT remove
        the fields it uses from fieldsLeft.
        """
        inits = {"keywords": [""]}  # ,"criteria":[]}
        if response != None:
            inits.update(response)

        inits["keywords"] = inits["keywords"][0]

        x = MultiForm(inits)
        x.fieldNames = fieldsLeft
        #x.fields["criteria"].choices=[(field.name,field.label)
        #  for field in fields if field.name in fieldsLeft]
        return x


class SelectForm(forms.Form):
    def is_empty(self):
        empty = True
        for field in self.fields.keys():
            if field in self.data and \
               self.data[field] != "" and \
               self.data[field] != [] and \
               self.data[field] != ['']:
                empty = False

        return empty

    def is_valid(self):
        # XXX ?
        return True

    def filter(self, qs):
        # filter search results
        if not self.is_empty():
            allAdIDs = set()

            for field in self.fields.keys():
                if field in self.data and \
                   self.data[field] != "" and \
                   self.data[field] != [] and \
                   self.data[field] != ['']:
                    if type(self.data[field]) == type([]):
                        fvs = set(FieldValue.objects.filter(field__name=field,
                                                            value__in=self.data[field]))
                    else:
                        fvs = set(FieldValue.objects.filter(field__name=field,
                                                            value=self.data[field]))

                    # Join the current set with this set
                    allAdIDs |= set([val.ad.pk for val in fvs])

            return qs.filter(pk__in=list(allAdIDs))

        return qs

    @staticmethod
    def create(fields, response=None):
        inits = {}
        if response:
            inits.update(response)

        x = SelectForm(inits)
        x.fields.update(fields)

        return x

searchForms = (PriceRangeForm, ZipCodeForm, MultiForm)
