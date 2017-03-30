from django.conf.urls import url
from tracker import views
urlpatterns = [
    url(r'^(?i)patients/$', views.patients, name='patients'),
    url(r'^(?i)patient/(?P<pid>[\-\w]+)/$', views.patient_details, name='patient_details'),
    url(r'^(?i)patient/(?P<pid>[\-\w]+)/Edit/$', views.patient_edit, name='patient_edit'),
    url(r'^(?i)patient/(?P<pid>[\-\w]+)/Notes/$', views.patient_notes, name='patient_notes'),
    url(r'^(?i)patient/(?P<pid>[\-\w]+)/Note/(?P<nid>\d+)/$', views.patient_note_action, name='patient_note_action'),
    url(r'^(?i)patient/(?P<pid>[\-\w]+)/pedigree/$', views.patient_pedigree, name='patient_pedigree'),
    url(r'^(?i)patient/(?P<pid>[\-\w]+)/relationship/$', views.patient_relationship, name='patient_relationship'),
    url(r'^(?i)patient/(?P<pid>[\-\w]+)/family/$', views.patient_family, name='patient_family'),
    url(r'^(?i)patient/(?P<pid>[\-\w]+)/Files/$', views.patient_files, name='patient_files'),
    url(r'^(?i)patient/(?P<pid>[\-\w]+)/Files/(?P<action>\w+)/$', views.patient_files_action, name='patient_files_action'),
    url(r'^(?i)families/(?P<action>\w+)/$', views.families_action, name='families_action'),
    url(r'^(?i)families/$', views.families, name='families'),

    url(r'^(?i)orders/$', views.orders_view, name='orders'),
    url(r'^(?i)order/(?P<oid>\d+)/$', views.order_details, name='order_details'),
    url(r'^(?i)order/(?P<oid>\d+)/Edit/$', views.order_edit, name='order_edit'),
    url(r'^(?i)order/(?P<oid>\d+)/Notes/$', views.order_notes, name='order_notes'),
    url(r'^(?i)order/(?P<oid>\d+)/Note/(?P<nid>\d+)/$', views.order_note_action, name='order_note_action'),
    url(r'^(?i)order/(?P<oid>\d+)/phenotypes/$', views.order_phenopypes, name='order_phenopypes'),
    url(r'^(?i)order/(?P<oid>\d+)/diseases/$', views.order_sortedDisease, name='order_sortedDisease'),
    url(r'^(?i)order/(?P<oid>\d+)/addphenotype/$', views.add_order_phenopype, name='add_order_phenopype'),
    url(r'^(?i)order/(?P<oid>\d+)/editphenotype/$', views.edit_order_phenopype, name='edit_order_phenopype'),
    url(r'^(?i)order/groups/$', views.order_groups, name='order_groups'),
    url(r'^(?i)order/groups/(?P<action>\w+)/$', views.ordergroup_action, name='ordergroup_action'),

    url(r'^(?i)samples/$', views.samples_view, name='samples'),
    url(r'^(?i)sample/(?P<sid>\d+)/$', views.sample_details, name='sample_details'),
    url(r'^(?i)sample/(?P<sid>\d+)/Edit/$', views.sample_edit, name='sample_edit'),

]