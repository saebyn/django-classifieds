from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.contrib import messages
from django.utils.translation import ugettext as _


from classifieds.models import Ad
from classifieds.utils import context_sortable


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
