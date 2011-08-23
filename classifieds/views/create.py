import datetime

from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.forms.models import inlineformset_factory
from django.utils.translation import ugettext as _


from classifieds.models import Ad, Category, Pricing, AdImage
from classifieds.adform import AdForm
from classifieds.utils import clean_adimageformset, render_category_page


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
def edit(request, pk):
    # get the specified ad, only if it's not active and this user owns it.
    ad = get_object_or_404(Ad, pk=pk, user=request.user)

    if ad.active:
        return redirect('classifieds_manage_ad_edit', pk=pk)

    image_count = ad.category.images_max_count
    ImageUploadFormSet = inlineformset_factory(Ad, AdImage, extra=image_count,
                                               max_num=image_count,
                                               fields=('full_photo',))
    # enforce max width & height on images
    ImageUploadFormSet.clean = clean_adimageformset

    if request.method == 'POST':
        imagesformset = ImageUploadFormSet(request.POST, request.FILES,
                                           instance=ad)
        form = AdForm(ad, request.POST)
        if form.is_valid():
            ad = form.save()
            if imagesformset.is_valid():
                imagesformset.save()
                # XXX image processing
                for image in ad.adimage_set.all():
                    image.resize()
                    image.generate_thumbnail()

            return redirect('classifieds_create_ad_preview', pk=ad.pk)
    else:
        imagesformset = ImageUploadFormSet(instance=ad)
        form = AdForm(ad)

    return render_category_page(request, ad.category, 'edit.html',
                                {'form': form,
                                 'imagesformset': imagesformset,
                                 'ad': ad,
                                 'create': True})


@login_required
def preview(request, pk):
    ad = get_object_or_404(Ad, pk=pk, user=request.user)

    if ad.active:
        return redirect('classifieds_browse_ad_view', pk=pk)

    return render_category_page(request, ad.category, 'preview.html',
                                {'ad': ad, 'create': True})
