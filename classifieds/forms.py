"""
  $Id$
"""

from django import forms
from models import Pricing, PricingOptions

class CheckoutForm(forms.Form):
	# construct form from Pricing and PricingOptions models
	pricing = forms.ChoiceField(choices=map(lambda x: (x.pk, unicode(x.length) + u' Day Listing : $' + unicode(x.price)), Pricing.objects.all()), widget=forms.RadioSelect)
	pricing_options = forms.MultipleChoiceField(choices=map(lambda x: (x.pk, unicode(x) + u' : $' + unicode(x.price)), PricingOptions.objects.all()), widget=forms.CheckboxSelectMultiple, required=False)
	
	def clean_pricing(self):
		try:
			Pricing.objects.get(pk=int(self.data["pricing"]))
		except Pricing.DoesNotExist:
			raise forms.ValidationError(_("The selected price does not exist."))
		
		return int(self.data["pricing"])
	
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
			raise forms.ValidationError(_("The e-mail address you entered has already been registered."))
				
		return email

