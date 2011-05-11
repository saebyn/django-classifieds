from django.conf.urls.defaults import *

from django.conf import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),

    # Uncomment the admin/doc line below to enable admin documentation:
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),

    # generic and contrib views
    (r'^accounts/login/$', 'django.contrib.auth.views.login'),
    (r'^accounts/logout/$', 'django.contrib.auth.views.logout', {'next_page': '/'}),
    (r'^accounts/password_reset/$', 'django.contrib.auth.views.password_reset'),
	
    
    # add-on apps.
    (r'^registration/', include('registration.urls')),
    (r'^profiles/', include('profiles.urls'), {'success_url': '/profiles/edit/'}),

    # our views (included from the app)
    (r'', include('classifieds.urls')),
)
