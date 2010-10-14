"""
  $Id$
"""

from PIL import Image
import string

from django.shortcuts import render_to_response
from django.utils.datastructures import SortedDict
from django.utils.translation import ugettext as _

from django.core.paginator import Paginator, InvalidPage

from django.template.loader import get_template
from django.template import TemplateDoesNotExist, RequestContext

from django import forms

from classifieds.conf import settings

# classifieds internal modules
from models import Ad, Field, Category, Pricing, PricingOptions

def render_category_page(request, category, page, context):
    template_name = 'classifieds/category/' + category.template_prefix + '/' + page
    try:
        get_template(template_name)
    except TemplateDoesNotExist:
        template_name = 'classifieds/category/base/' + page

    return render_to_response(template_name, context, 
                              context_instance=RequestContext(request))

def clean_adimageformset(self):
    max_size = self.instance.category.images_max_size
    for form in self.forms:
      try:
        if not hasattr(form.cleaned_data['full_photo'], 'file'):
          continue
      except:
        continue

      if form.cleaned_data['full_photo'].size > max_size:
        raise forms.ValidationError(_('Maximum image size is ' + str(max_size/1024) + ' KB'))
      
      im = Image.open(form.cleaned_data['full_photo'].file)
      if self.instance.category.images_allowed_formats.filter(format=im.format).count() == 0:
        raise forms.ValidationError(_('Your image must be in one of the following formats: ') + string.join(self.instance.category.images_allowed_formats.values_list('format', flat=True), ','))
    

def context_sortable(request, ads, perpage=settings.ADS_PER_PAGE):
  order = '-'
  sort = 'expires_on'
  page = 1
  
  if request.GET.has_key('perpage') and request.GET['perpage'] != '':
    perpage = int(request.GET['perpage'])
  
  if request.GET.has_key('order') and request.GET['order'] != '':
    if request.GET['order'] == 'desc':
      order = '-'
    elif request.GET['order'] == 'asc':
      order = ''
      
  if request.GET.has_key('page'):
    page = int(request.GET['page'])
      
  if request.GET.has_key('sort') and request.GET['sort'] != '':
    sort = request.GET['sort']

  if sort in ['created_on', 'expires_on', 'category', 'title']:
    ads_sorted = ads.extra(select={'featured': """SELECT 1
FROM `classifieds_payment_options`
LEFT JOIN `classifieds_payment` ON `classifieds_payment_options`.`payment_id` = `classifieds_payment`.`id`
LEFT JOIN `classifieds_pricing` ON `classifieds_pricing`.`id` = `classifieds_payment`.`pricing_id`
LEFT JOIN `classifieds_pricingoptions` ON `classifieds_payment_options`.`pricingoptions_id` = `classifieds_pricingoptions`.`id`
WHERE `classifieds_pricingoptions`.`name` = %s
AND `classifieds_payment`.`ad_id` = `classifieds_ad`.`id`
AND `classifieds_payment`.`paid` =1
AND `classifieds_payment`.`paid_on` < NOW()
AND DATE_ADD( `classifieds_payment`.`paid_on` , INTERVAL `classifieds_pricing`.`length`
DAY ) > NOW()"""}, select_params=[PricingOptions.FEATURED_LISTING]).extra(order_by=['-featured', order + sort])
  else:
    # sometimes I surprise myself
    ads_sorted = ads.extra(select=SortedDict( [('fvorder', 'select value from classifieds_fieldvalue LEFT JOIN classifieds_field on classifieds_fieldvalue.field_id = classifieds_field.id where classifieds_field.name = %s and classifieds_fieldvalue.ad_id = classifieds_ad.id'), ('featured', """SELECT 1
FROM `classifieds_payment_options`
LEFT JOIN `classifieds_payment` ON `classifieds_payment_options`.`payment_id` = `classifieds_payment`.`id`
LEFT JOIN `classifieds_pricing` ON `classifieds_pricing`.`id` = `classifieds_payment`.`pricing_id`
LEFT JOIN `classifieds_pricingoptions` ON `classifieds_payment_options`.`pricingoptions_id` = `classifieds_pricingoptions`.`id`
WHERE `classifieds_pricingoptions`.`name` = %s
AND `classifieds_payment`.`ad_id` = `classifieds_ad`.`id`
AND `classifieds_payment`.`paid` =1
AND `classifieds_payment`.`paid_on` < NOW()
AND DATE_ADD( `classifieds_payment`.`paid_on` , INTERVAL `classifieds_pricing`.`length`
DAY ) > NOW()""")] ), select_params=[sort, PricingOptions.FEATURED_LISTING]).extra(order_by = ['-featured', order + 'fvorder'])
  
  pager = Paginator(ads_sorted, perpage)
  
  try:
    page = pager.page(page)
  except InvalidPage:
    page = {'object_list': False}

  can_sortby_list = []
  sortby_list = ['created_on']
  for category in Category.objects.filter(ad__in=ads.values('pk').query).distinct():
    can_sortby_list += category.sortby_fields.split(',')

  for category in Category.objects.filter(ad__in=ads.values('pk').query).distinct():
    for fieldname, in category.field_set.values_list('name'):
      if fieldname not in sortby_list and fieldname in can_sortby_list:
        sortby_list.append(fieldname)

  for fieldname, in Field.objects.filter(category=None).values_list('name'):
    if fieldname not in sortby_list and fieldname in can_sortby_list:
      sortby_list.append(fieldname)
  
  return {'page': page, 'sortfields': sortby_list, 'no_results': False, 'perpage': perpage}


