from django.conf.urls import url
from mybackend import views

urlpatterns = [
    url(r'^$', views.testing_index, name='backend_index'),
    url(r'gettermlist/$', views.get_termlist, name='get_termlist'),
    url(r'getterm/byexid/(?P<exid>\d+)/$', views.get_hpo_by_exid, name='get_hpo_by_exid'),
    url(r'getterms_by_disease/(?P<did>\d+)/$', views.getterms_by_disease, name='getterms_by_disease'),
    url(r'getterm_details/(?P<tid>\d+)/$', views.get_term_details, name='get_term_details'),
    url(r'getterm_details/byacc/(?P<acc>\w+\:\w+)/$', views.get_term_details_byacc, name='get_term_details_byacc'),
    url(r'getdiseaselist/$', views.get_diseaselist, name='get_diseaselist'),
    url(r'getomimgenes/$', views.getOminGenes,name='get_omim_genes'),
    url(r'save_pedigree/$', views.save_pedigree, name='save_pedigree'),
    url(r'get_log/(?P<what>\w+)/$', views.get_log, name='get_log'),
    url(r'get_notes/$', views.get_notes, name='get_notes'),
    url(r'get_note/(?P<nid>\d+)/$', views.get_note, name='get_note'),
    url(r'save_file/$', views.save_file, name='save_file'),
    url(r'get_sampleorderlist/$', views.get_sampleorderlist, name='get_sampleorderlist'),
    url(r'get_samplefiles/$', views.getSampleFiles, name='get_samplefiles'),
    url(r'get_workflows/$', views.get_workflows, name='get_workflows'),
    url(r'run_cartagenia/(?P<group>\w+)/$', views.run_cartagenia, name='run_cartagenia'),
    url(r'sso_cartagenia/$', views.sso_cartagenia, name='sso_cartagenia'),
    url(r'getreport_cartagenia/$', views.getreport_cartagenia, name='getreport_cartagenia'),
    url(r'checkstatus_cartagenia/(?P<mrn>[\-\w]+)/$', views.checkstatus_cartagenia, name='checkstatus_cartagenia'),
    url(r'magic_function/(?P<func>\w+)/$', views.mybackend_magic, name='mybackend_magic')
]