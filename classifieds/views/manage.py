# vim: set fileencoding=utf-8 ft=python ff=unix nowrap tabstop=4 shiftwidth=4 softtabstop=4 smarttab shiftround expandtab :
from django.core.urlresolvers import reverse
from django.http import Http404
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.utils.translation import ugettext as _
from django.views.generic import DeleteView, TemplateView


from classifieds.models import Ad
from classifieds.utils import context_sortable
from classifieds.views.base import LoginRequiredMixin


class MyAdsView(LoginRequiredMixin, TemplateView):
    template_name = 'classifieds/manage.html'

    def get_context_data(self, **kwargs):
        context = super(MyAdsView, self).get_context_data(**kwargs)
        context['sortfields'] = ['id', 'category', 'created_on']
        context.update(context_sortable(self.request,
                                        Ad.objects.filter(user=self.request.user, active=True)))
        return context


class AdDeleteView(DeleteView):
    model = Ad

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(AdDeleteView, self).dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('classifieds_manage_view_all')

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
