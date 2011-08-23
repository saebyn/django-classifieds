from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext

from classifieds.models import Ad


def contact_seller(request, pk):
    ad = get_object_or_404(Ad, pk=pk)
    # TODO contact form here
