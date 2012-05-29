"""
"""

from django import forms
from django.utils.translation import ugettext as _
from classifieds.models import Pricing, PricingOptions


# TODO make inlineformset class for ad images


class CheckoutForm(forms.Form):
    # construct form from Pricing and PricingOptions models
    pricing = forms.ModelChoiceField(queryset=Pricing.objects.all(),
                                     widget=forms.RadioSelect,
                                     empty_label=None)
    pricing_options = forms.ModelMultipleChoiceField(queryset=PricingOptions.objects.all(),
                                                     widget=forms.CheckboxSelectMultiple,
                                                     required=False)


class SubscribeForm(forms.Form):
    first_name = forms.CharField(max_length=100)
    last_name = forms.CharField(max_length=100)
    email_address = forms.EmailField()
    #interested_in = forms.MultipleChoiceField(choices=[(category.name, category.name) for category in Category.objects.all()], widget=forms.CheckboxSelectMultiple)
    #comments = forms.CharField(widget=forms.Textarea)

    def clean_captcha(self):
        # TODO check captcha
        return ''

    def clean_email_address(self):
        email = self.cleaned_data["email_address"]

        if User.objects.filter(email=email).count() > 0:
            raise forms.ValidationError(_(u"The e-mail address you entered has already been registered."))

        return email
