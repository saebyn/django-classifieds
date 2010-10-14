"""
  $Id$
"""
from django.conf.urls.defaults import *

# nested urls
base_urlpatterns = patterns('classifieds.views',
  (r'^$', 'browse.category_overview'),
  (r'^post/$', 'create.first_post'),
  (r'^create/$', 'create.select_category'),
  (r'^create/([-\w]+)/$', 'create.create_in_category'),
  (r'^create/edit/([-\w]+)/$', 'create.edit'),
  (r'^create/preview/([-\w]+)/$', 'create.preview'),

  (r'^search/$', 'browse.search'),
  (r'^search/([-\w]+)/$', 'browse.search_in_category'),
  (r'^search_results/([-\w]+)/$', 'browse.search_results'),
  (r'^([0-9]+)/$', 'browse.view'),
)

# local-based urls coming soon
urlpatterns = base_urlpatterns

# top-level urls
urlpatterns += patterns('classifieds.views',
  (r'^mine/$', 'manage.mine'),
  (r'^edit/([0-9]+)/$', 'manage.edit'),
  (r'^delete/([0-9]+)/$', 'manage.delete'),

  (r'^new/([0-9]+)/$', 'create.view_bought'),
  (r'^checkout/([0-9]+)$', 'create.checkout'),
  (r'^pricing$', 'create.pricing'),

  (r'^notify$', 'notify.notify'),
  (r'^notify_complete$', 'notify.notify_complete'),

  (r'^contact/([0-9]+)$', 'contact.contact_seller'),
)

from sitemaps import sitemaps

urlpatterns += patterns('',
  (r'^ipn/$', 'paypal.standard.ipn.views.ipn'),
  (r'^sitemap.xml$', 'django.contrib.sitemaps.views.sitemap', {'sitemaps': sitemaps}),
)

