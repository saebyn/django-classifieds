from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.forms.models import inlineformset_factory
from django.contrib import messages
from django.utils.translation import ugettext as _


from classifieds.models import Ad, AdImage
from classifieds.adform import AdForm
from classifieds.utils import clean_adimageformset, context_sortable, \
                              render_category_page


@login_required
def mine(request):
    ads = Ad.objects.filter(user=request.user, active=True)
    context = context_sortable(request, ads)
    context['sortfields'] = ['id', 'category', 'created_on']
    return render_to_response('classifieds/manage.html', context,
                              context_instance=RequestContext(request))


# TODO class-based view with GET/POST confirmation thingy
@login_required
def delete(request, pk):
    # find the ad, if available
    ad = get_object_or_404(Ad, pk=pk, active=True, user=request.user)

    ad.delete()

    # create status message
    messages.success(request, _('Ad deleted.'))

    # send the user back to their ad list
    return redirect('classifieds_manage_view_all')


@login_required
def edit(request, pk):
    # find the ad, if available
    ad = get_object_or_404(Ad, pk=pk, active=True, user=request.user)

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
            form.save()
            if imagesformset.is_valid():
                imagesformset.save()
                for image in ad.adimage_set.all():
                    image.resize()
                    image.generate_thumbnail()

            return redirect('classifieds_manage_view_all')
    else:
        imagesformset = ImageUploadFormSet(instance=ad)
        form = AdForm(ad)

    return render_category_page(request, ad.category, 'edit.html',
                                {'form': form,
                                 'imagesformset': imagesformset,
                                 'ad': ad})
