from django.shortcuts import render_to_response, redirect
from django.http import Http404
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.template import RequestContext
from django.contrib import messages
from django.utils.translation import ugettext as _
from django.views.generic import DeleteView


from classifieds.models import Ad
from classifieds.utils import context_sortable


@login_required
def mine(request):
    ads = Ad.objects.filter(user=request.user, active=True)
    context = context_sortable(request, ads)
    context['sortfields'] = ['id', 'category', 'created_on']
    return render_to_response('classifieds/manage.html', context,
                              context_instance=RequestContext(request))


class AdDeleteView(DeleteView):
    model = Ad

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(AdDeleteView, self).dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return redirect('classifieds_manage_view_all')

    def delete(self, request, *args, **kwargs):
        response = super(AdDeleteView, self).delete(request, *args, **kwargs)

        # create status message
        messages.success(request, _(u'Ad deleted.'))

        return response

    def get_object(self, queryset=None):
        obj = super(AdDeleteView, self).get_object(queryset)

        if not obj.user == self.request.user:
            raise Http404

        return obj
