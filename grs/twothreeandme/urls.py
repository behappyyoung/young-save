from django.conf.urls import include, url
from twothreeandme import views

urlpatterns = [
    url(r'get_grant/$', views.get_grant, name='twothreeandme_get_grant'),
    url(r'ttm_response/$', views.ttm_response, name='ttm_response'),
    url(r'get_account/(?P<token>[\-\w+]+)/$', views.get_account, name='twothreeandme_get_account'),
    url(r'get_genomes/(?P<profile_id>[\-\w+]+)/(?P<token>[\-\w+]+)/$', views.get_genomes, name='twothreeandme_get_genomes'),
    url(r'json_testing/$', views.json_testing, name='json_testing'),
    url(r'get_auth/$', views.get_auth, name='twothreeandme_get_auth'),
    url(r'consent/$', views.get_consent, name='twothreeandme_get_consent'),
    url(r'consent/form/$', views.consent_form, name='twothreeandme_consent_form'),
    url(r'backend/insert_map/$', views.insert_map, name='insert_map'),
    url(r'update_accessions/(?P<cid>\d+)/$', views.update_accessions, name='update_accessions'),
    url(r'update_chromosome/(?P<cid>\d+)/(?P<offset>\d+)/$', views.update_chromosome, name='update_chromosome'),
    url(r'$', views.index, name='twothreeandme_home')
]
