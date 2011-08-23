import datetime

from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext
from django import forms
from django.http import Http404

from classifieds.models import Category, Ad, Field
from classifieds.utils import context_sortable, render_category_page, \
                              prepare_sforms


def category_overview(request):
    context = {}
    context['categories'] = Category.objects.order_by('sort_order')
    return render_to_response('classifieds/category_overview.html', context,
                              context_instance=RequestContext(request))


def view(request, pk):
    # find the ad, if available
    ad = get_object_or_404(Ad, pk=pk, active=True)

    # only show an expired ad if this user owns it
    if ad.expires_on < datetime.datetime.now() and ad.user != request.user:
        raise Http404

    return render_category_page(request, ad.category, 'view.html', {'ad': ad})


def search_in_category(request, slug):
    # reset the search params, if present
    try:
        del request.session['search']
    except KeyError:
        pass

    return search_results(request, slug)


def search_results(request, slug):
    category = get_object_or_404(Category, slug=slug)
    fields = list(category.field_set.all())
    fields += list(Field.objects.filter(category=None))
    fieldsLeft = [field.name for field in fields]

    if request.method == "POST" or 'search' in request.session:
        ads = category.ad_set.filter(active=True,
                                     expires_on__gt=datetime.datetime.now())
        # A request dictionary with keys defined for all
        # fields in the category.
        post = {}
        if 'search' in request.session:
            post.update(request.session['search'])
        else:
            post.update(request.POST)

        sforms = prepare_sforms(fields, fieldsLeft, post)

        isValid = True

        for f in sforms:
            # TODO: this assumes the form is not required
            # (it's a search form after all)
            if not f.is_valid() and not f.is_empty():
                isValid = False

        if isValid:
            if request.method == 'POST':
                request.session['search'] = {}
                request.session['search'].update(request.POST)
                return redirect('classifieds_browse_search_results', slug=slug)

            for f in sforms:
                ads = f.filter(ads)

            if ads.count() == 0:
                return render_to_response('classifieds/list.html',
                                          {'no_results': True,
                                           'category': category},
                                          context_instance=RequestContext(request))
            else:
                context = context_sortable(request, ads)
                context['category'] = category
                return render_to_response('classifieds/list.html', context,
                                          context_instance=RequestContext(request))
    else:
        sforms = prepare_sforms(fields, fieldsLeft)

    return render_to_response('classifieds/search.html',
                              {'forms': sforms, 'category': category},
                              context_instance=RequestContext(request))
