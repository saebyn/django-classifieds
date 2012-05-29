"""
"""
from django.conf.urls.defaults import *

from classifieds.views import AdEditView, AdCreationEditView
from classifieds.views.manage import AdDeleteView


# nested urls
base_urlpatterns = patterns('classifieds.views',
    url(r'^$', 'browse.category_overview',
        name='classifieds_browse_categories'),

    url(r'^post/$', 'create.first_post', name='classifieds_create_ad'),
    url(r'^create/$', 'create.select_category',
        name='classifieds_create_ad_select_category'),
    url(r'^create/(?P<slug>[-\w]+)/$', 'create.create_in_category',
        name='classifieds_create_ad_in_category'),
    url(r'^create/edit/(?P<pk>[0-9]+)/$', AdCreationEditView.as_view(),
        name='classifieds_create_ad_edit'),
    url(r'^create/preview/(?P<pk>[0-9]+)/$', 'create.preview',
        name='classifieds_create_ad_preview'),

    url(r'^search/(?P<slug>[-\w]+)/$', 'browse.search_in_category',
        name='classifieds_browse_category_search'),
    url(r'^search/results/(?P<slug>[-\w]+)/$', 'browse.search_results',
        name='classifieds_browse_search_results'),
    url(r'^(?P<pk>[0-9]+)/$', 'browse.view',
        name='classifieds_browse_ad_view'),
)

# local-based urls coming soon
urlpatterns = base_urlpatterns

# top-level urls
urlpatterns += patterns('classifieds.views',
    url(r'^mine/$', 'manage.mine', name='classifieds_manage_view_all'),
    url(r'^edit/(?P<pk>[0-9]+)/$', AdEditView.as_view(),
        name='classifieds_manage_ad_edit'),
    url(r'^delete/(?P<pk>[0-9]+)/$', AdDeleteView.as_view(),
        name='classifieds_manage_ad_delete'),

    (r'^new/(?P<pk>[0-9]+)/$', 'payment.view_bought'),
    (r'^checkout/(?P<pk>[0-9]+)$', 'payment.checkout'),
    (r'^pricing$', 'payment.pricing'),

    (r'^contact/(?P<pk>[0-9]+)$', 'contact.contact_seller'),
)


from sitemaps import sitemaps


urlpatterns += patterns('',
    (r'^ipn/$', 'paypal.standard.ipn.views.ipn'),
    (r'^sitemap.xml$', 'django.contrib.sitemaps.views.sitemap',
     {'sitemaps': sitemaps}),
)
