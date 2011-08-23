"""
"""
from django.contrib.sitemaps import Sitemap
from django.core.urlresolvers import reverse

from classifieds.models import Ad

import datetime


class AdSitemap(Sitemap):
    changefreq = 'monthly'

    def items(self):
        return Ad.objects.filter(active=True,
                                 expires_on__gt=datetime.datetime.now())

    def location(self, item):
        return reverse('classifieds_browse_ad_view', args=[item.pk])

    def lastmod(self, item):
        return item.created_on


sitemaps = {'ads': AdSitemap}
