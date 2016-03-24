from django.contrib import admin
from django.conf.urls import include, url
from loginas import views as loginas_views

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^login/user/(?P<user_id>.+)/$', loginas_views.user_login, name='loginas-user-login'),
]
