from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns(
    '',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^login/user/(?P<user_id>.+)/$', 'loginas.views.user_login', name='loginas-user-login'),
)
