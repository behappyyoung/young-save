from django.conf.urls import include, url
from django.contrib import admin
from django.views.static import serve
from crsapi import settings
from twothreeandme import views as ttm_views
from crsapi import views
from users import views as users_views


urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^(?i)system/$', views.crsapi_system, name='system_check'),
    url(r'^(?i)login/(?P<uid>\w+)/$', users_views.user_login, name='test_login'),
    url(r'^(?i)user/profile/$', users_views.profile, name='profile'),
    url(r'^(?i)privacy/$', views.privacy, name='privacy'),
    url(r'^(?i)static/(.*)$', serve, {'document_root': settings.STATIC_ROOT}),
    url(r'^(?i)twothreeandme/', include('twothreeandme.urls')),
    url(r'^$',  ttm_views.index, name='index')
]
