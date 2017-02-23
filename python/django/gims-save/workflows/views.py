from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.http import (HttpResponse, HttpResponseRedirect,
                         HttpResponseServerError)
from django.core import serializers
from tracker.models import LabOrderStatus, Orders, Samples, SampleOrderRel, SampleContainer, SampleStatus
from .models import Workflows, WorkflowType, LabWorkFlows, LabWorkFlowType, LabWorkFlowStatus
from .forms import WorkflowsForm
from mybackend.models import CustomSQL, GCloudFiles
from django.contrib import messages
from django.contrib.auth.decorators import login_required
import json, yaml
import socket, sys, re
from logger.models import accessLog, logging, OrderProcessingLog, samplelog, SampleProcessingLog
from gims import settings
from httplib import BadStatusLine
from mybackend import functions
import urllib2
from gims.settings import LOOMURL, LOOMURLS
from datetime import datetime, timedelta
from bson import json_util

pattern = re.compile('^2\.7\.')                                  # for python 2.7.9 above..
if pattern.match(sys.version) and int(sys.version[4:6]) >= 9 :  # for python 2.7.9 above..
    newversion = True
    import ssl
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
else:
    newversion = False


def custom_proc(request):
    return {
        'LOOMURL': settings.LOOMURL,
    }


@login_required(login_url='/saml/')
def index(request):
    if 'username' in request.session:
        print request.session.get('username')
    else:
        return HttpResponseRedirect('/saml/?slo')
    response = urllib2.urlopen(LOOMURL+'data-objects/').read()
    workflows = urllib2.urlopen(LOOMURL+'abstract-workflows/').read()
    fileData = urllib2.urlopen(LOOMURL+'file-data-objects/').read()
    running = urllib2.urlopen(LOOMURL+'run-requests/').read()
    logging(request, 'access')
    return render(request, 'workflows/index.html', {'data':response, 'fileData': fileData, 'workflows':workflows, 'running':running}, context_instance=RequestContext(request, processors=[custom_proc]))

BASE_WORKFLOW_SQL='SELECT w.*, wt.type_name as tname from workflows_workflows w left join workflows_workflowtype wt on w.type_id = wt.id WHERE w.status="A" '


@login_required(login_url='/saml/')
def workflows(request):
    if 'username' in request.session:
        print request.session.get('username')
    else:
        return HttpResponseRedirect('/saml/?slo')

    myc = CustomSQL()
    c_workflows = myc.my_custom_sql(BASE_WORKFLOW_SQL)

    logging(request, 'access')
    return render(request, 'workflows/workflows.html', {'workflows':json.dumps(c_workflows)}, context_instance=RequestContext(request, processors=[custom_proc]))


@login_required(login_url='/saml/')
def workflow_details(request, wid):
    if 'username' in request.session:
        print request.session.get('username')
    else:
        return HttpResponseRedirect('/saml/?slo')

    try:
        if newversion:  # for python 2.7.9 above..
            c_workflow = urllib2.urlopen(LOOMURLS['workflows']+wid+'/', context=ctx).read()
        else:
            c_workflow = urllib2.urlopen(LOOMURLS['workflows']+wid+'/').read()
    except:
        message = "could not fetch %s" % LOOMURLS['workflows']
        messages.error(request, message)
        return HttpResponseRedirect('/')
    json_workflow = yaml.safe_load(c_workflow)
    logging(request, 'access')
    return render(request, 'workflows/workflow_details.html', {'workflow':json_workflow}, context_instance=RequestContext(request, processors=[custom_proc]))


@login_required(login_url='/saml/')
def define_workflows(request):
    if 'username' in request.session:
        print request.session.get('username')
    else:
        return HttpResponseRedirect('/saml/?slo')
    wf_types = WorkflowType.wf_objects.all()
    type_lists =[]
    for wftype in wf_types:
        type_lists.append({'id':wftype.id, 'type': wftype.type, 'typename': wftype.type_name, 'desc': wftype.desc})
    logging(request, 'access')
    return render(request, 'workflows/workflows_create.html', {'title': 'Create Workflows', 'wf_types': json.dumps(type_lists)},
                  context_instance=RequestContext(request, processors=[custom_proc]))


@login_required(login_url='/saml/')
def edit_workflow(request, wid):
    if request.method == 'POST':
        form = WorkflowsForm(request.POST)
        if form.is_valid():
            #form.save()
            wf = Workflows.objects.get(id=wid)
            wf.name = request.POST['name']
            wf.type_id = request.POST['type']
            wf.workflow_id = request.POST['workflow_id']
            wf.inputs = request.POST['inputs']
            wf.fixed_inputs = request.POST['fixed_inputs']
            wf.desc = request.POST['desc']
            wf.status = request.POST['status']
            wf.version = request.POST['version']
            wf.save()
            return HttpResponseRedirect('/editworkflow/'+wid+'/')
    else:
        wf = Workflows.objects.get(id=wid)
        form = WorkflowsForm(instance=wf)
    return render(request, 'workflows/workflow_edit.html', {'form': form, 'wid':wid })

BASE_SAMPLE_SQL='Select * from tracker_samples s left join tracker_sampleorderrel rel on s.id = rel.sample_id ' \
                'join tracker_orders o on o.id = rel.order_id join tracker_sorelations rt on rel.relation_id = rt.id '

BASE_SAMPLEFILES_SQL='SELECT sf.*, s.asn as asn from tracker_samplefiles sf join tracker_samples s on sf.sample_id = s.id'


@login_required(login_url='/saml/')
def analyses(request):
    if 'username' not in request.session:
        return HttpResponseRedirect('/saml/?slo')

    try:
        if newversion:  # for python 2.7.9 above..
            running = urllib2.urlopen(LOOMURLS['runrequest'], context=ctx).read()
        else:
            running = urllib2.urlopen(LOOMURLS['runrequest']).read()
    except:
        message = "could not fetch %s" % LOOMURLS['runrequest']
        messages.error(request, message)
        return HttpResponseRedirect('/')
    json_running = yaml.safe_load(running)
    logging(request, 'access')
    return render(request, 'workflows/analyses.html', {'running': json_running}, context_instance=RequestContext(request, processors=[custom_proc]))


@login_required(login_url='/saml/')
def run_analysis(request):
    if 'username' not in request.session:
        return HttpResponseRedirect('/saml/?slo')

    if 'Interpretation' not in request.session.get('role') and 'Manager' not in request.session.get('role'):
        message = " You do not have permission to load  %s" % request.path_info
        messages.error(request, message)
        logging(request, 'UnAuthorized')
        return HttpResponseRedirect('/')

    myc = CustomSQL()
    c_samples = myc.my_custom_sql(BASE_SAMPLE_SQL)
    c_samplefiles = myc.my_custom_sql(BASE_SAMPLEFILES_SQL)
    c_workflows = myc.my_custom_sql(BASE_WORKFLOW_SQL)
    # workflows = Workflows.objects.filter(status='A')
    # workflows_json = serializers.serialize('json', workflows)
    logging(request, 'access')
    return render(request, 'workflows/analysis.html', {'workflows':json.dumps(c_workflows), 'samples':json.dumps(c_samples, default=json_util.default), 'samplefiles':json.dumps(c_samplefiles)}, context_instance=RequestContext(request, processors=[custom_proc]))


@login_required(login_url='/saml/')
def analysis_details(request, wid):
    if 'username' in request.session:
        print request.session.get('username')
    else:
        return HttpResponseRedirect('/saml/?slo')

    try:
        if newversion:  # for python 2.7.9 above..
            c_analysis = urllib2.urlopen(LOOMURLS['runrequest']+wid+'/', context=ctx).read()
        else:
            c_analysis = urllib2.urlopen(LOOMURLS['runrequest']+wid+'/').read()
    except BadStatusLine:
        message = "could not fetch %s" % LOOMURLS['runrequest']
        messages.error(request, message)
        return HttpResponseRedirect('/')
    json_analysis = yaml.safe_load(c_analysis)
    logging(request, 'access')
    return render(request, 'workflows/analysis_details.html',
            {'analysis':json_analysis}, context_instance=RequestContext(request, processors=[custom_proc]))


@login_required(login_url='/saml/')
def delete_workflow(request, wid):
    try:
        wf = Workflows.objects.get(id=wid)
        wf.status = '1'
        message = wf.save()
    except:
        message = 'error'

    return HttpResponse(message)

'''
    Lab Workflows
'''


@login_required(login_url='/saml/')
def lab_main(request):
    logging(request, 'access')
    return render(request, 'workflows/lab_main.html', {'title': 'Lab Workflows', })



LAB_SAMPLE_SQL = 'Select * from tracker_samples s left join tracker.sampleorderrel so on s.id =  so.sample_id' \
                 ' left join tracker_orders o on o.id = so.order_id ' \
                  'left join tracker_orderstatus os on o.status_id = os.id'


LAB_WORKFLOW_SAMPLES_SQL = 'Select * from tracker_samples s left join tracker_sampleorderrel rel on s.id = rel.sample_id'\
                         ' left join tracker_orders o on o.id = rel.order_id ' \
                        'left join tracker_samplestatus ss on s.status_id = ss.id left join workflows_labworkflowstatus wfs on wfs.sample_id = s.id ' \
                        ' WHERE ss.status != "COLLECTED" ORDER BY wfs.id,  s.collection_date '

LAB_WORKFLOW_BASE_SQL = 'Select * from tracker_samples s left join tracker_sampleorderrel rel on s.id = rel.sample_id'\
                         ' left join tracker_orders o on o.id = rel.order_id ' \
                        'left join tracker_orderstatus os on o.status_id = os.id ' \
                        ' WHERE o.lab_status="%s" '

LAB_QUANTIFICATION_SQL = 'Select * from tracker_samples s left join tracker_sampleorderrel rel on s.id = rel.sample_id'\
                         ' left join tracker_orders o on o.id = rel.order_id ' \
                        'left join tracker_orderstatus os on o.status_id = os.id ' \
                        ' left join tracker_laborderstatus ls on o.lab_status_id = ls.id ' \
                        ' WHERE ls.labstatus="DNA_RECEIVED" '


@login_required(login_url='/saml/')
def lab_workflows_list(request):
    if 'username' in request.session:
        print request.session.get('username')
    else:
        return HttpResponseRedirect('/saml/?slo')

    so = SampleOrderRel.objects.filter(sample__status__status='COLLECTED').order_by('sample__collection_date').select_related('patient', 'sample', 'order')
    container = SampleContainer.objects.all()
    logging(request, 'access')
    return render(request, 'workflows/lab_workflow_list.html', {'title': 'Lab Workflows - Outstading Lists',
                                                                'sample_order':so, 'container': container})


@login_required(login_url='/saml/')
def lab_select_container(request):
    if 'username' in request.session:
        print request.session.get('username')
    else:
        return HttpResponseRedirect('/saml/?slo')

    if request.method != 'POST':
        message = ' Request Error : Only POST requests are accepted'
        return HttpResponse(json.dumps({'status_code': 406, 'status_message': message}), content_type="application/json")
    else:
        # body = request.body
        sid = request.POST['sid']
        cid = request.POST['cid']
        SampleOrderRel.objects.filter(sample_id=sid).update(container=cid)
        new_status = SampleStatus.objects.get(status='DNA_RECEIVED')
        sample = Samples.objects.get(id=sid)
        sample.status_id = new_status.id
        sample.save()
        samplelog(request, sid, 'Status Change from %s to %s'%('COLLECTED', 'DNA_RECEIVED'))
        SampleProcessingLog(sample_id=sid, prev_status='CELLECTED', update_status='DNA_RECEIVED',
                        name=sample.name, type=sample.type, prev_time=sample.collection_date )
        message = 'Updated'
        return HttpResponse(json.dumps({'status_code': 200, 'status_message': message}), content_type="application/json")


@login_required(login_url='/saml/')
def lab_workflows_dash(request):
    if 'username' in request.session:
        print request.session.get('username')
    else:
        return HttpResponseRedirect('/saml/?slo')
    if request.META['QUERY_STRING']:
        date_range = request.META['QUERY_STRING'].split('~')
    else:
        now = datetime.now()
        today_in = now + timedelta(days=1)
        week_ago = now - timedelta(days=6)
        date_range = [week_ago.strftime('%Y-%m-%d'), today_in.strftime('%Y-%m-%d')]
    myc = CustomSQL()
    c_samples = myc.my_custom_sql(LAB_WORKFLOW_SAMPLES_SQL)
    ## create list of samples  for dash
    so = SampleOrderRel.objects.filter().exclude(sample__status__status='COLLECTED').order_by(
        'sample__collection_date').select_related('patient', 'sample', 'order')
    dash_list = {}
    for s in so:
        dash_list['sid'] = s.sample_id
        dash_list['pname'] = s.patient.first_name + ' ' + s.patient.last_name
        dash_list['container'] = s.container


    logging(request, 'access')
    return render(request, 'workflows/lab_workflow_dash.html',
                  {'title': 'Lab Workflows - Dashboard','dash_list':dash_list, 'samples':c_samples})


@login_required(login_url='/saml/')
def lab_workflows(request):
    if 'username' in request.session:
        print request.session.get('username')
    else:
        return HttpResponseRedirect('/saml/?slo')
    if request.META['QUERY_STRING']:
        date_range = request.META['QUERY_STRING'].split('~')
    else:
        now = datetime.now()
        today_in = now + timedelta(days=1)
        week_ago = now - timedelta(days=6)
        date_range = [week_ago.strftime('%Y-%m-%d'), today_in.strftime('%Y-%m-%d')]
    # print date_range, [date_range[0], date_range[1]]
    labworkflows = LabWorkFlows.objects.filter(created_date__range=[date_range[0], date_range[1]]).order_by('-created_date')
    logging(request, 'access')
    return render(request, 'workflows/lab_workflow_tab.html', {'title': 'Lab Workflows - Workflows', 'labworkflows':labworkflows})


@login_required(login_url='/saml/')
def quantification(request):
    if 'username' in request.session:
        print request.session.get('username')
    else:
        return HttpResponseRedirect('/saml/?slo')
    myc = CustomSQL()
    c_samples = myc.my_custom_sql(LAB_QUANTIFICATION_SQL)
    logging(request, 'access')
    lastobj = LabWorkFlows.objects.latest('id')
    return render(request, 'workflows/labwork_new.html',
                {'samples':json.dumps(c_samples, default=functions.date_handler), 'title': 'Quantification', 'new_id':lastobj.id+1})


@login_required(login_url='/saml/')
def fluidigm(request):
    if 'username' in request.session:
        print request.session.get('username')
    else:
        return HttpResponseRedirect('/saml/?slo')
    myc = CustomSQL()
    c_samples = myc.my_custom_sql(LAB_WORKFLOW_BASE_SQL%('QPASS'))

    logging(request, 'access')
    lastobj = LabWorkFlows.objects.latest('id')
    return render(request, 'workflows/labwork_new.html',
                {'samples':json.dumps(c_samples, default=functions.date_handler), 'title': 'Fluidigm', 'new_id':lastobj.id+1})


# @login_required(login_url='/saml/')
# def quantification_detail(request, wid):
# 	if 'username' in request.session:
# 		print request.session.get('username')
# 	else:
# 		return HttpResponseRedirect('/saml/?slo')
# 	logging(request, 'access')
# 	detail_list = []
# 	workflow = LabWorkFlows.objects.get(id=wid)
# 	sample_list = workflow.samples_list.split(',')
#
# 	for s in sample_list:
# 		temp = {}
# 		s_list = s.split('-')
# 		c_order = Orders.objects.get(id=s_list[1])
# 		c_sample = Samples.objects.get(id=s_list[2])
# 		temp['tube'] = s_list[0]
# 		temp['order'] = c_order
# 		temp['sample'] = c_sample
# 		temp['container'] = s_list[3]
# 		detail_list.append(temp)
#
# 	return render(request, 'workflows/quantification_details.html',
# 				{'workflow':workflow, 'title': 'Quantification Details','detail_list': detail_list})


@login_required(login_url='/saml/')
def save_labworkflow(request, type):
    if 'username' in request.session:
        print request.session.get('username')
    else:
        return HttpResponseRedirect('/saml/?slo')
    if request.method != 'POST':
        message = 'Only POST requests are accepted'
    else:
        if type == 'Q':
            new_status = 'QSTART'
        elif type == 'F':
            new_status = 'FSTART'

        d = json.loads(request.body)
        # orders = d.get('order_list').split(',')
        c_labworkflows = LabWorkFlows(name=d.get('name'), samples_list=d.get('sample_list'), type=type, status=new_status)
        message = c_labworkflows.save()
        sample_list = d.get('sample_list').split(',')
        for s in xrange(len(sample_list)):
            s_list = sample_list[s].split('-')
            wfs = LabWorkFlowStatus(workflow_id=c_labworkflows.id, tube_number=s_list[0], order_id=s_list[1], sample_id=s_list[2], container=s_list[3])
            wfs.save()
            c_order = Orders.objects.get(id=s_list[2])
            c_order.lab_status = new_status
            c_order.save()
            OrderProcessingLog(order_id=c_order.id, order_name=c_order.order_name, prev_time=c_order.updated,
                        order_type=c_order.type, prev_status=str(c_order.status), update_status=new_status).log()

        #
        # for i in xrange(len(orders)):
        # 	wfs = LabWorkFlowStatus(workflow_id=c_labworkflows, order_id=orders[i], sample_id=orders[i])
        # 	c_order = Orders.objects.get(id=orders[i])
        # 	c_order.lab_status = new_status
            # c_order.save()
            # OrderProcessingLog(order_id=c_order.id, order_name=c_order.order_name, prev_time=c_order.updated,
            # 				order_type=c_order.type, prev_status=str(c_order.status), update_status=new_status).log()

    return HttpResponse(message)


@login_required(login_url='/saml/')
def labwork_detail(request, wid):
    if 'username' in request.session:
        print request.session.get('username')
    else:
        return HttpResponseRedirect('/saml/?slo')
    logging(request, 'access')
    workflow = LabWorkFlows.objects.get(id=wid)
    wfs = LabWorkFlowStatus.objects.filter(workflow_id=wid).order_by('tube_number')
    redo_list=[]
    for s in wfs:
        if s.status =='QREDO':
            redo_list.append(s)
    files = GCloudFiles.objects.filter(obj_id=workflow.id, obj_type='Quantification').order_by('-upload_date')
    if workflow.type == 'Q':
        title = 'Quantification'
    elif workflow.type =='F':
        title = 'Fluidigm'

    return render(request, 'workflows/labwork_details.html',
                {'workflow':workflow, 'title': title , 'wf_status': wfs, 'files':files,'redo_list':redo_list})
