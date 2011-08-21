"""
  $Id$
"""
from django.conf.urls.defaults import *

# nested urls
base_urlpatterns = patterns('classifieds.views',
  (r'^$', 'browse.category_overview'),


  url(r'^post/$', 'create.first_post', name='classifieds_create_ad'),
  url(r'^create/$', 'create.select_category', name='classifieds_create_ad_select_category'),
  url(r'^create/(?P<slug>[-\w]+)/$', 'create.create_in_category', name='classifieds_create_ad_in_category'),
  url(r'^create/edit/(?P<pk>[0-9]+)/$', 'create.edit', name='classifieds_create_ad_edit'),
  url(r'^create/preview/(?P<pk>[0-9]+)/$', 'create.preview', name='classifieds_create_ad_preview'),


  (r'^search/$', 'browse.search'),
  (r'^search/([-\w]+)/$', 'browse.search_in_category'),
  (r'^search_results/([-\w]+)/$', 'browse.search_results'),
  url(r'^(?P<pk>[0-9]+)/$', 'browse.view', name='classifieds_browse_ad_view'),
)

# local-based urls coming soon
urlpatterns = base_urlpatterns

# top-level urls
urlpatterns += patterns('classifieds.views',
  url(r'^mine/$', 'manage.mine', name='classifieds_manage_view_all'),
  url(r'^edit/(?P<pk>[0-9]+)/$', 'manage.edit', name='classifieds_manage_ad_edit'),
  (r'^delete/(?P<pk>[0-9]+)/$', 'manage.delete'),

  (r'^new/(?P<pk>[0-9]+)/$', 'create.view_bought'),
  (r'^checkout/(?P<pk>[0-9]+)$', 'create.checkout'),
  (r'^pricing$', 'create.pricing'),

  (r'^notify$', 'notify.notify'),
  (r'^notify_complete$', 'notify.notify_complete'),

  (r'^contact/(?P<pk>[0-9]+)$', 'contact.contact_seller'),
)

from sitemaps import sitemaps

urlpatterns += patterns('',
  (r'^ipn/$', 'paypal.standard.ipn.views.ipn'),
  (r'^sitemap.xml$', 'django.contrib.sitemaps.views.sitemap', {'sitemaps': sitemaps}),
)

