from django.conf.urls import url
from workflows import views
urlpatterns = [
    url(r'^$', views.lab_main, name='lab_main'),
    url(r'^(?i)list/$', views.lab_workflows_list, name='lab_workflows_list'),
    url(r'^(?i)select_container/$', views.lab_select_container, name='lab_select_container'),
    url(r'^(?i)workflows/$', views.lab_workflows, name='lab_workflows'),
    url(r'^(?i)dash/$', views.lab_workflows_dash, name='lab_workflows_dash'),
    url(r'^(?i)quantification/$', views.quantification, name='quantification'),
    url(r'^(?i)quantification/redo/$', views.quantification_redo, name='quantification_redo'),
    url(r'^(?i)details/(?P<wid>\d+)/$', views.labwork_detail, name='labwork_detail'),
    url(r'^(?i)save/(?P<wtype>\w+)/$', views.save_labworkflow, name='save_labworkflow'),
    url(r'^(?i)create_fp/$', views.create_fp, name='create_fp'),
    url(r'^(?i)fluidigm/$', views.fluidigm, name='fluidigm'),
    url(r'^(?i)uploadfile/qt/$', views.uploadfile_qt, name='uploadfile_qt'),
    url(r'^(?i)uploadfile/fp/$', views.uploadfile_fp, name='uploadfile_fp')
]