"""
  $Id$
"""
from django.conf.urls.defaults import *

urlpatterns = patterns('classifieds.views',
  (r'^$', 'index'),
  (r'^create/$', 'create'),
  (r'^create/([0-9]+)/$', 'create_in_category'),
  (r'^create/edit/([0-9]+)/$', 'create_edit'),
  (r'^create/preview/([0-9]+)/$', 'create_preview'),
  (r'^search/$', 'search'),
  (r'^search/([0-9]+)/$', 'search_in_category'),
  (r'^search_results/([0-9]+)/$', 'search_results'),
  (r'^mine/$', 'mine'),
  (r'^edit/([0-9]+)/$', 'edit'),
  (r'^delete/([0-9]+)/$', 'delete'),
  (r'^([0-9]+)/$', 'view'),
  (r'^new/([0-9]+)/$', 'view_bought'),
  (r'^checkout/([0-9]+)$', 'checkout'),
  (r'^pricing$', 'pricing'),
  (r'^notify$', 'notify'),
  (r'^notify_complete$', 'notify_complete'),
)

from sitemaps import sitemaps

urlpatterns += patterns('',
  (r'^ipn/$', 'paypal.standard.ipn.views.ipn'),
  (r'^sitemap.xml$', 'django.contrib.sitemaps.views.sitemap', {'sitemaps': sitemaps}),
)

