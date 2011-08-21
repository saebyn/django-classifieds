from django.shortcuts import render_to_response, get_object_or_404
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.forms.models import inlineformset_factory
from django.http import HttpResponseRedirect
from django.conf import settings as django_settings

from classifieds.models import Ad, AdImage
from classifieds.adform import AdForm
from classifieds.utils import clean_adimageformset, context_sortable, render_category_page

@login_required
def mine(request):
  ads = Ad.objects.filter(user=request.user, active=True)
  context = context_sortable(request, ads)
  context['sortfields'] = ['id', 'category', 'created_on']
  return render_to_response('classifieds/manage.html', context, context_instance=RequestContext(request))

@login_required
def delete(request, adId):
  # find the ad, if available
  ad = get_object_or_404(Ad, pk=adId, active=True)
  
  # make sure that only the owner of the ad can delete it
  if request.user != ad.user:
    return HttpResponseRedirect('%s?%s=%s' % (django_settings.LOGIN_URL, REDIRECT_FIELD_NAME, urlquote(request.get_full_path())))
  
  ad.delete()
  
  # create status message
  request.user.message_set.create(message='Ad deleted.')
  
  # send the user back to their ad list
  return HttpResponseRedirect(reverse('classifieds.views.mine'))

@login_required
def edit(request, adId):
  # find the ad, if available
  ad = get_object_or_404(Ad, pk=adId, active=True)
  
  # make sure that only the owner of the ad can edit it
  if request.user != ad.user:
    return HttpResponseRedirect('%s?%s=%s' % (django_settings.LOGIN_URL, REDIRECT_FIELD_NAME, urlquote(request.get_full_path())))

  image_count = ad.category.images_max_count
  ImageUploadFormSet = inlineformset_factory(Ad, AdImage, extra=image_count, max_num=image_count, fields=('full_photo',))
  # enforce max width & height on images
  ImageUploadFormSet.clean = clean_adimageformset
  
  if request.method == 'POST':
    imagesformset = ImageUploadFormSet(request.POST, request.FILES, instance=ad)
    form = AdForm(ad, request.POST)
    if form.is_valid() and imagesformset.is_valid():
      form.save()
      imagesformset.save()
      for image in ad.adimage_set.all():
        image.resize()
        image.generate_thumbnail()
      return HttpResponseRedirect(reverse('classifieds.views.mine'))
  else:
    imagesformset = ImageUploadFormSet(instance=ad)
    form = AdForm(ad)
  
  return render_category_page(request, ad.category, 'edit.html',
                              {'form': form, 
                               'imagesformset': imagesformset, 
                               'ad': ad})
