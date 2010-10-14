import datetime

from django.shortcuts import render_to_response, get_object_or_404
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django import forms
from django.http import HttpResponseRedirect, Http404

from classifieds.utils import context_sortable, render_category_page
from classifieds.search import *

def category_overview(request):
  context = {}
  categories = Category.objects.all().order_by('sort_order')
  return render_to_response('classifieds/category_overview.html', context, context_instance=RequestContext(request))


def view(request, adId):
  # find the ad, if available
  ad = get_object_or_404(Ad, pk=adId, active=True)
  
  if ad.expires_on < datetime.datetime.now() and ad.user != request.user:
    raise Http404
  
  return render_category_page(request, ad.category, 'view.html', {'ad': ad})

def search(request):
  # list categories available and send the user to the search_in_category view
  return render_to_response('classifieds/category_choice.html', {'categories': Category.objects.all(), 'type': 'search'}, context_instance=RequestContext(request))

def search_in_category(request, categoryId):
  try:
    del request.session['search']
  except KeyError:
    pass
  
  return search_results(request, categoryId)

def prepare_sforms(fields, fields_left, post=None):
  sforms = []
  select_fields = {}
  for field in fields:
    if field.field_type == Field.SELECT_FIELD:  # is select field
      # add select field
      options = field.options.split(',')
      choices = zip(options, options)
      choices.insert(0, ('', 'Any',))
      form_field = forms.ChoiceField(label=field.label, required=False, help_text=field.help_text + u'\nHold ctrl or command on Mac for multiple selections.', choices=choices, widget=forms.SelectMultiple)
      # remove this field from fields_list
      fields_left.remove( field.name )
      select_fields[field.name] = form_field
      
  sforms.append(SelectForm.create(select_fields, post))
  
  for sf in searchForms:
    f = sf.create(fields, fields_left, post)
    if f != None:
      sforms.append(f)
  
  return sforms

def search_results(request, categoryId):
  cat = get_object_or_404(Category, pk=categoryId)
  fields = list(cat.field_set.all())
  fields += list(Field.objects.filter(category=None))
  fieldsLeft = [field.name for field in fields]
  
  if request.method == "POST" or request.session.has_key('search'):
    ads = cat.ad_set.filter(active=True,expires_on__gt=datetime.datetime.now())
    # A request dictionary with keys defined for all
    # fields in the category.
    post = {}
    if request.session.has_key('search'):
      post.update(request.session['search'])
    else:
      post.update(request.POST)
    
    sforms = prepare_sforms(fields, fieldsLeft, post)

    isValid = True
    #validErrors = {}
    for f in sforms:
      #TODO: this assumes the form is not required (it's a search form after all)
      if not f.is_valid() and not f.is_empty():
        isValid = False
        #validErrors.update(f.errors)

    if isValid:
      if request.method == 'POST':
        request.session['search'] = {}
        request.session['search'].update(request.POST)
        return HttpResponseRedirect(reverse('classifieds.views.search_results', args=[categoryId]))
      
      for f in sforms:
        ads = f.filter(ads)
    
      if ads.count() == 0:
        return render_to_response('classifieds/list.html', {'no_results':True, 'category':cat}, context_instance=RequestContext(request))
      else:
        context = context_sortable(request, ads)
        context['category'] = cat
        return render_to_response('classifieds/list.html', context, context_instance=RequestContext(request))
  else:
    sforms = prepare_sforms(fields, fieldsLeft)
    
  return render_to_response('classifieds/search.html', {'forms':sforms, 'category':cat}, context_instance=RequestContext(request))
