"""
  $Id$
"""
from django.conf.urls.defaults import *

# nested urls
base_urlpatterns = patterns('classifieds.views',
  (r'^$', 'browse.category_overview'),


  url(r'^post/$', 'create.first_post', name='classifieds_create_ad'),
  url(r'^create/$', 'create.select_category', name='classifieds_create_ad_select_category'),
  url(r'^create/([-\w]+)/$', 'create.create_in_category', name='classifieds_create_ad_in_category'),
  url(r'^create/edit/([0-9]+)/$', 'create.edit', name='classifieds_create_ad_edit'),
  url(r'^create/preview/([0-9]+)/$', 'create.preview', name='classifieds_create_ad_preview'),


  (r'^search/$', 'browse.search'),
  (r'^search/([-\w]+)/$', 'browse.search_in_category'),
  (r'^search_results/([-\w]+)/$', 'browse.search_results'),
  url(r'^([0-9]+)/$', 'browse.view', name='classifieds_browse_ad_view'),
)

# local-based urls coming soon
urlpatterns = base_urlpatterns

# top-level urls
urlpatterns += patterns('classifieds.views',
  (r'^mine/$', 'manage.mine'),
  url(r'^edit/([0-9]+)/$', 'manage.edit', name='classifieds_manage_ad_edit'),
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

