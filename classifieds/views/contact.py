# vim: set fileencoding=utf-8 ft=python ff=unix nowrap tabstop=4 shiftwidth=4 softtabstop=4 smarttab shiftround expandtab :
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext

from classifieds.models import Ad


def contact_seller(request, pk):
    ad = get_object_or_404(Ad, pk=pk)
    # TODO contact form here
