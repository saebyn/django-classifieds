import datetime

from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.utils.translation import ugettext as _

from classifieds.models import Ad, Category, Pricing
from classifieds.utils import render_category_page


def first_post(request):
    if request.user.is_authenticated() and request.user.is_active:
        return redirect('classifieds_create_ad_select_category')
    else:
        return render_to_response('classifieds/index.html',
                                  {'prices': Pricing.objects.all()},
                                  context_instance=RequestContext(request))


@login_required
def select_category(request):
    """
    List the categories available and send the user to the create_in_category
    view.
    """
    return render_to_response('classifieds/category_choice.html',
                              {'categories': Category.objects.all(),
                               'type': 'create'},
                              context_instance=RequestContext(request))


@login_required
def create_in_category(request, slug):
    # validate category slug
    category = get_object_or_404(Category, slug=slug)

    ad = Ad.objects.create(category=category, user=request.user,
                           expires_on=datetime.datetime.now(), active=False)
    ad.save()
    return redirect('classifieds_create_ad_edit', pk=ad.pk)


@login_required
def preview(request, pk):
    ad = get_object_or_404(Ad, pk=pk, user=request.user)

    if ad.active:
        return redirect('classifieds_browse_ad_view', pk=pk)

    return render_category_page(request, ad.category, 'preview.html',
                                {'ad': ad, 'create': True})
