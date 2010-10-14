import datetime

from django.shortcuts import render_to_response, get_object_or_404
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.template import Context, loader, RequestContext
from django.forms.models import inlineformset_factory
from django.utils.translation import ugettext as _
from django.http import HttpResponseRedirect
from django.conf import settings as django_settings

from paypal.standard.forms import PayPalPaymentsForm

from classifieds.models import Ad, Category, Pricing, PricingOptions, AdImage
from classifieds.forms import CheckoutForm
from classifieds.adform import AdForm
from classifieds.utils import clean_adimageformset, render_category_page
from classifieds import views
from classifieds.conf import settings

def first_post(request):
  if request.user.is_authenticated() and request.user.is_active:
    return HttpResponseRedirect(reverse('classifieds.views.create.select_category'))
  else:
    return render_to_response('classifieds/index.html', {'prices': Pricing.objects.all()}, context_instance=RequestContext(request))    

@login_required
def view_bought(request, adId):
  request.user.message_set.create(message=_('Your ad has been successfully posted. Thank You for Your Order!'))
  return views.browse.view(request, adId)

  
@login_required
def select_category(request):
  # list categories available and send the user to the create_in_category view
  return render_to_response('classifieds/category_choice.html', {'categories': Category.objects.all(), 'type': 'create'}, context_instance=RequestContext(request))

@login_required
def create_in_category(request, slug):
  # validate categoryId
  category = get_object_or_404(Category, slug=slug)

  ad = Ad.objects.create(category=category, user=request.user, expires_on=datetime.datetime.now(), active=False)
  ad.save()
  return HttpResponseRedirect(reverse('classifieds.views.create.edit', args=[ad.pk]))

@login_required
def edit(request, adId):
  # get the specified ad, only if it's not active and this user owns it.
  ad = get_object_or_404(Ad, pk=adId, active=False, user=request.user)
  
  image_count = ad.category.images_max_count
  ImageUploadFormSet = inlineformset_factory(Ad, AdImage, extra=image_count, max_num=image_count, fields=('full_photo',))
  # enforce max width & height on images
  ImageUploadFormSet.clean = clean_adimageformset
  
  if request.method == 'POST':
    imagesformset = ImageUploadFormSet(request.POST, request.FILES, instance=ad)
    form = AdForm(ad, request.POST)
    if form.is_valid():# and imagesformset.is_valid():
      ad = form.save()
      if imagesformset.is_valid():
        imagesformset.save()
        for image in ad.adimage_set.all():
          image.resize()
          image.generate_thumbnail()
        
        return HttpResponseRedirect(reverse('classifieds.views.create.preview', args=[ad.pk]))
  else:
    imagesformset = ImageUploadFormSet(instance=ad)
    form = AdForm(ad)
  
  return render_category_page(request, ad.category, 'edit.html',
                              {'form': form, 
                               'imagesformset': imagesformset, 
                               'ad': ad, 
                               'create': True})
  

@login_required
def preview(request, adId):
  ad = get_object_or_404(Ad, pk=adId, active=False, user=request.user)
  
  return render_category_page(request, ad.category, 'preview.html',
                              {'ad': ad, 'create': True})


def checkout(request, adId):
  ad = get_object_or_404(Ad, pk=adId)
  if request.method == 'POST':
    form = CheckoutForm(request.POST)
    if form.is_valid():
      total = 0
      pricing = Pricing.objects.get(pk=form.cleaned_data["pricing"])
      total += pricing.price
      pricing_options = []
      for pk in form.cleaned_data["pricing_options"]:
        option = PricingOptions.objects.get(pk=pk)
        pricing_options.append(option)
        total += option.price
      
      # create Payment object
      payment = Payment.objects.create(ad=ad, pricing=pricing)
      for option in pricing_options:
        payment.options.add(option)
      
      payment.save()
      
      # send email when done
      # 1. render context to email template
      email_template = loader.get_template('classifieds/email/posting.txt')
      context = Context({'ad': ad})
      email_contents = email_template.render(context)

      # 2. send email
      send_mail(_('Your ad will be posted shortly.'),
                email_contents, 
                settings.FROM_EMAIL, 
                [ad.user.email], 
                fail_silently=False)
      
      item_name = _('Your ad on ') + Site.objects.get_current().name 
      paypal_values = {'amount': total,
                       'item_name': item_name, 
                       'item_number': payment.pk, 
                       'quantity': 1}
      if django_settings.DEBUG:
        paypal_form = PayPalPaymentsForm(initial=paypal_values).sandbox()
      else:
        paypal_form = PayPalPaymentsForm(initial=paypal_values).render()

      return render_to_response('classifieds/paypal.html', {'form': paypal_form}, context_instance=RequestContext(request))
  else:
    form = CheckoutForm()
  
  return render_to_response('classifieds/checkout.html', {'ad': ad, 'form': form}, context_instance=RequestContext(request))
  
def pricing(request):
  return render_to_response('classifieds/pricing.js', {'prices': Pricing.objects.all(), 'options': PricingOptions.objects.all()}, context_instance=RequestContext(request))
