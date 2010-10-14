"""
  $Id$
"""
from django.conf.urls.defaults import *

# nested urls
base_urlpatterns = patterns('classifieds.views',
  (r'^$', 'front_page'),
  (r'^post/$', 'index'),
  (r'^create/$', 'create'),
  (r'^create/([-\w]+)/$', 'create_in_category'),
  (r'^create/edit/([-\w]+)/$', 'create_edit'),
  (r'^create/preview/([-\w]+)/$', 'create_preview'),
  (r'^search/$', 'search'),
  (r'^search/([-\w]+)/$', 'search_in_category'),
  (r'^search_results/([-\w]+)/$', 'search_results'),
  (r'^([0-9]+)/$', 'view'),
)

# local-based urls coming soon
urlpatterns = base_urlpatterns

# top-level urls
urlpatterns += patterns('classifieds.views',
  (r'^mine/$', 'mine'),
  (r'^edit/([0-9]+)/$', 'edit'),
  (r'^delete/([0-9]+)/$', 'delete'),
  (r'^new/([0-9]+)/$', 'view_bought'),
  (r'^checkout/([0-9]+)$', 'checkout'),
  (r'^pricing$', 'pricing'),
  (r'^notify$', 'notify'),
  (r'^notify_complete$', 'notify_complete'),
  (r'^contact/([0-9]+)$', 'contact_seller'),
)

from sitemaps import sitemaps

urlpatterns += patterns('',
  (r'^ipn/$', 'paypal.standard.ipn.views.ipn'),
  (r'^sitemap.xml$', 'django.contrib.sitemaps.views.sitemap', {'sitemaps': sitemaps}),
)

