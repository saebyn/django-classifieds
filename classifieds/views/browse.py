# vim: set fileencoding=utf-8 ft=python ff=unix nowrap tabstop=4 shiftwidth=4 softtabstop=4 smarttab shiftround expandtab :
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext
from django.http import Http404
from django.utils import timezone

from classifieds.models import Category, Ad, Field
from classifieds.utils import context_sortable, render_category_page, \
                              prepare_search_forms


def category_overview(request):
    context = {}
    context['categories'] = Category.objects.order_by('sort_order')
    return render_to_response('classifieds/category_overview.html', context,
                              context_instance=RequestContext(request))


def view(request, pk):
    # find the ad, if available
    ad = get_object_or_404(Ad.objects.select_related('category', 'user'), pk=pk, active=True)

    # only show an expired ad if this user owns it
    if ad.expires_on < timezone.now() and ad.user != request.user:
        raise Http404

    return render_category_page(request, ad.category, 'view.html', {'ad': ad})


def search_in_category(request, slug):
    # reset the search params, if present
    try:
        del request.session['search']
    except KeyError:
        pass

    return search_results(request, slug)


# TODO consider switching this to get search parameters from GET instead of POST
# This POST -> save in session -> GET setup was used because it was desired to keep
# the URL of the search page clear of GET parameters.
def search_results(request, slug):
    if request.method == 'POST':
        request.session['search'] = {}
        request.session['search'].update(request.POST)
        return redirect('classifieds_browse_search_results', slug=slug)

    category = get_object_or_404(Category, slug=slug)
    fields = list(category.field_set.all())
    fields += list(Field.objects.filter(category=None))
    fieldsLeft = [field.name for field in fields]

    # A request dictionary with keys defined for all
    # fields in the category.
    post = request.session.get('search') or request.POST or None
    search_forms, is_valid = prepare_search_forms(fields, fieldsLeft, post)

    if post and is_valid:
        ads = category.ad_set.filter(active=True,
                                     expires_on__gt=timezone.now())

        for f in search_forms:
            ads = f.filter(ads)

        context = dict(category=category)
        if ads.count() > 0:
            context.update(context_sortable(request, ads))
        else:
            context['no_results'] = True

        return render_to_response('classifieds/list.html', context,
                                  context_instance=RequestContext(request))

    return render_to_response('classifieds/search.html',
                              {'forms': search_forms, 'category': category},
                              context_instance=RequestContext(request))
