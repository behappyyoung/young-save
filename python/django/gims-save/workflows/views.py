from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.http import (HttpResponse, HttpResponseRedirect,
                         HttpResponseServerError)
from django.core import serializers
from tracker.models import Orders, Samples, SampleOrderRel, SampleContainer, SampleStatus, OrderType
from .models import Workflows, WorkflowType, LabWorkFlows, LabWorkFlowType, LabWorkFlowStatus, LabStatus, LabType
from .forms import WorkflowsForm
from mybackend.models import CustomSQL, GCloudFiles
from django.contrib import messages
from django.contrib.auth.decorators import login_required
import json, yaml
import socket, sys, re
from logger.models import accessLog, logging, OrderProcessingLog, samplelog, SampleProcessingLog, SampleHistory
from gims import settings
from httplib import BadStatusLine
from mybackend import functions, QubitResultsParser, FluidigmResultsParser
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


def sample_status_list(getid=False):
    sdict ={}
    ss = SampleStatus.objects.all()
    if getid:
        for s in ss:
            sdict[s.status] = s.id
    else:
        for s in ss:
            sdict[s.id] = s.status_name
    return sdict


def lab_status_list(getid=False):
    sdict ={}
    ss = LabStatus.objects.all()
    if getid:
        for s in ss:
            sdict[s.labstatus] = s.id
    else:
        for s in ss:
            sdict[s.id] = s.labstatus_name
    return sdict


def order_type_list():
    odict={}
    ot = OrderType.objects.all()
    for o in ot:
        odict[o.id] = o.type_name
    return odict


def getSampleList(so, forwhat=None):
    dash_lists = []
    for s in so:
        dlist = dict()
        dlist['sample_id'] = s.sample_id
        dlist['asn'] = str(s.sample.asn)
        dlist['pname'] = urllib2.quote(str(s.patient.name()))
        # dlist['pname'] = str(s.patient.name())
        dlist['container'] = str(s.container)
        dlist['order_type'] = urllib2.quote(str(s.order.type.type_name))
        dlist['order_id'] = str(s.order_id)
        dlist['sample_type'] = str(s.sample.type)
        status = s.sample.status
        dlist['status'] = str(status.status)
        dlist['volume'] = str(s.sample.volume)
        dlist['note'] = str(s.sample.note or '')
        dlist['status_name'] = str(status.status_name)

        if forwhat =='FP':
            ls = LabStatus.objects.filter(labstatus='QPASS')
            wfs = LabWorkFlowStatus.objects.filter(sample_id=s.sample_id, container=s.container, status=ls).last()
            dlist['username'] = str(wfs.workflow.username)
            dlist['project'] = wfs.workflow.name
            dlist['project_id'] = wfs.workflow.id
            dlist['start_date'] = wfs.workflow.created_date
            dlist['end_date'] = wfs.workflow.updated_date
            dlist['result'] = wfs.result
        elif 'DNA' in status.status:
            sh = SampleHistory.objects.filter(sample_id=s.sample_id).using('logs').last()
            dlist['username'] = str(sh.user_id)
            dlist['start_date'] = str(sh.update_time)
            dlist['end_date'] = 'N/A'
            dlist['project'] = 'N/A'
        elif 'Q' == status.status[0] or 'F' == status.status[0]:
            wfs = LabWorkFlowStatus.objects.filter(sample_id=s.sample_id, container=s.container).last()
            dlist['username'] = str(wfs.workflow.username)
            dlist['project'] = wfs.workflow.name
            dlist['project_id'] = wfs.workflow.id
            dlist['start_date'] = wfs.workflow.created_date
            dlist['end_date'] = wfs.workflow.updated_date
            dlist['result'] = wfs.result
        else:
            dlist['username'] = 'test'


        dash_lists.append(dlist)

    return dash_lists


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


def workflows(request):
    if 'username' in request.session:
        print request.session.get('username')
    else:
        return HttpResponseRedirect('/saml/?slo')
    try:
        if newversion:  # for python 2.7.9 above..
            loom_workflows_json = urllib2.urlopen(LOOMURLS['workflows'], context=ctx).read()
        else:
            loom_workflows_json = urllib2.urlopen(LOOMURLS['workflows']).read()
        loom_workflows = json.loads(loom_workflows_json)
    except:
        loom_workflows =[]
        message = "could not fetch %s" % LOOMURLS['workflows']
        messages.error(request, message)

    # save workflow in DB
    workflows =[]
    c_workflows = Workflows.objects.all()
    for lw in loom_workflows:
        w_exist = False
        uuid = lw.get('uuid')
        name = lw.get('name')
        type = lw.get('type')
        json_inputs = json.dumps(lw.get('inputs'))
        json_fixed_inputs = json.dumps(lw.get('fixed_inputs'))
        ordertype = None
        version = None
        desc = None
        for cw in c_workflows:
            if uuid == cw.workflow_id:
                w_exist = True
                cw.name = name
                cw.inputs = json_inputs
                cw.fixed_inputs = json_fixed_inputs
                type = type
                ordertype = cw.order_type.type_name if cw.order_type else ''
                version = cw.version
                cw.save()
                break

        if not w_exist and lw.get('type') == 'workflow':
            new_workflow = Workflows(workflow_id=uuid, name=name, inputs=json_inputs, fixed_inputs=json_fixed_inputs, type='workflow', status='A')
            new_workflow.save()
        workflows.append({'uuid': uuid, 'name': name, 'version': version, 'ordertype': ordertype, 'desc': desc,
                          'inputs': json_inputs, 'fixed_inputs': json_fixed_inputs, 'type': type})
    logging(request, 'access')
    return render(request, 'workflows/loom/workflows.html', {'workflows':json.dumps(workflows)}, context_instance=RequestContext(request, processors=[custom_proc]))


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
            wf = Workflows.objects.get(workflow_id=wid)
            wf.name = request.POST['name']
            wf.type = request.POST['type']
            wf.order_type_id = request.POST.get('order_type')
            wf.inputs = request.POST['inputs']
            wf.fixed_inputs = request.POST['fixed_inputs']
            wf.desc = request.POST.get('desc') or ''
            wf.status = request.POST['status']
            wf.version = request.POST['version']
            wf.save()
        else:
            message = form.errors
            messages.error(request, message)
        return HttpResponseRedirect('/editworkflow/'+wid+'/')
    else:
        wf = Workflows.objects.get(workflow_id=wid)
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
            running = urllib2.urlopen(LOOMURLS['runs'], context=ctx).read()
        else:
            running = urllib2.urlopen(LOOMURLS['runs']).read()
    except:
        message = "could not fetch %s" % LOOMURLS['runs']
        messages.error(request, message)
        return HttpResponseRedirect('/')
    json_running = yaml.safe_load(running)
    logging(request, 'access')
    return render(request, 'workflows/loom/runs.html', {'running': json.dumps(json_running) }, context_instance=RequestContext(request, processors=[custom_proc]))


@login_required(login_url='/saml/')
def run_analysis(request):
    if 'username' not in request.session:
        return HttpResponseRedirect('/saml/?slo')

    if 'Interpretation' not in request.session.get('role') and 'Manager' not in request.session.get('role'):
        message = " You do not have permission to load  %s" % request.path_info
        messages.error(request, message)
        logging(request, 'UnAuthorized')
        return HttpResponseRedirect('/')
    # try:
    #     if newversion:  # for python 2.7.9 above..
    #         workflows = urllib2.urlopen(LOOMURLS['workflows'], context=ctx).read()
    #     else:
    #         workflowa = urllib2.urlopen(LOOMURLS['workflows']).read()
    # except:
    #     message = "could not fetch %s" % LOOMURLS['workflows']
    #     messages.error(request, message)

    # so = SampleOrderRel.objects.all()
    # so_list = getSampleList(so)
    # myc = CustomSQL()
    # c_samples = myc.my_custom_sql(BASE_SAMPLE_SQL)
    # c_samplefiles = myc.my_custom_sql(BASE_SAMPLEFILES_SQL)
    # c_workflows = myc.my_custom_sql(BASE_WORKFLOW_SQL)
    w_list=[]
    workflows = Workflows.objects.filter(status='A')
    # workflows_json = serializers.serialize('json', workflows)
    for w in workflows:
        type_id = w.order_type.id if w.order_type else ''
        type_name = w.order_type.type_name if w.order_type else ''

        w_list.append({'name': str(w.name), 'wid': str(w.workflow_id), 'version': str(w.version),
                       'order_typeid': str(type_id),'type_name': str(type_name),
                       'inputs': str(w.inputs), 'fixed_inputs': str(w.fixed_inputs)})
    logging(request, 'access')
    return render(request, 'workflows/loom/analysis.html', {'workflows': json.dumps(w_list)}, context_instance=RequestContext(request, processors=[custom_proc]))


@login_required(login_url='/saml/')
def analysis_details(request, wid):
    if 'username' in request.session:
        print request.session.get('username')
    else:
        return HttpResponseRedirect('/saml/?slo')

    try:
        if newversion:  # for python 2.7.9 above..
            c_analysis = urllib2.urlopen(LOOMURLS['runs']+wid+'/', context=ctx).read()
        else:
            c_analysis = urllib2.urlopen(LOOMURLS['runs']+wid+'/').read()
    except BadStatusLine:
        message = "could not fetch %s" % LOOMURLS['runs']
        messages.error(request, message)
        return HttpResponseRedirect('/')
    json_analysis = yaml.safe_load(c_analysis)
    logging(request, 'access')
    # title = json_analysis.templates.name
    return render(request, 'workflows/analysis_details.html',
            {'analysis':json.dumps(json_analysis)}, context_instance=RequestContext(request, processors=[custom_proc]))


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


@login_required(login_url='/saml/')
def lab_workflows_list(request):
    if 'username' in request.session:
        print request.session.get('username')
    else:
        return HttpResponseRedirect('/saml/?slo')

    so = SampleOrderRel.objects.filter(sample__status__status='COLLECTED').order_by('sample__collection_date').select_related('patient', 'sample', 'order')
    so_list = []
    slist = []
    status_list = sample_status_list()
    type_list = order_type_list()
    for s in so:
        date_text = s.sample.collection_date.strftime('%A, %b %d, %Y, %I%p')
        so_list.append({'pname' : s.patient.name(), 'asn': s.sample.asn, 'cdate': s.sample.collection_date, 'date_text':date_text,  'sample_id': s.sample_id,
                        'type': type_list.get(s.order.type_id), 'status' : status_list.get(s.sample.status_id), 'notes':(s.sample.note or '')})
        slist.append(s.sample_id)
    container = SampleContainer.objects.filter(sample_id__in=slist)
    # json_container = serializers.serialize('json', container)
    logging(request, 'access')
    return render(request, 'workflows/lab_workflow_list.html', {'title': 'Lab Workflows - Outstading Lists',
                                                                'so_list':so_list, 'container': container})


@login_required()
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
                        name=sample.name, type=sample.type, prev_time=sample.collection_date).log()
        message = 'Updated'
        return HttpResponse(json.dumps({'status_code': 200, 'status_message': message}), content_type="application/json")


@login_required()
def lab_workflows_dash(request):
    if 'username' in request.session:
        print request.session.get('username')
    else:
        return HttpResponseRedirect('/saml/?slo')
    # if request.META['QUERY_STRING']:
    #     date_range = request.META['QUERY_STRING'].split('~')
    # else:
    #     now = datetime.now()
    #     today_in = now + timedelta(days=1)
    #     week_ago = now - timedelta(days=6)
    #     date_range = [week_ago.strftime('%Y-%m-%d'), today_in.strftime('%Y-%m-%d')]
    # myc = CustomSQL()
    # c_samples = myc.my_custom_sql(LAB_WORKFLOW_SAMPLES_SQL)
    ## create list of samples  for dash
    so = SampleOrderRel.objects.filter().exclude(sample__status__status='COLLECTED').order_by(
        'sample__collection_date').select_related('patient', 'sample', 'order')
    dash_lists = getSampleList(so, 'dash')

    logging(request, 'access')
    return render(request, 'workflows/lab_workflow_dash.html',
                  {'title': 'Lab Workflows - Dashboard','dash_lists': json.dumps(dash_lists)})


@login_required()
def lab_workflows(request):
    if 'username' in request.session:
        print request.session.get('username')
    else:
        return HttpResponseRedirect('/saml/?slo')
    # if request.META['QUERY_STRING']:
    #     date_range = request.META['QUERY_STRING'].split('~')
    # else:
    #     now = datetime.now()
    #     today_in = now + timedelta(days=1)
    #     week_ago = now - timedelta(days=6)
    #     date_range = [week_ago.strftime('%Y-%m-%d'), today_in.strftime('%Y-%m-%d')]
    # print date_range, [date_range[0], date_range[1]]
    # labworkflows = LabWorkFlows.objects.filter(created_date__range=[date_range[0], date_range[1]]).order_by('-created_date')
    labworkflows = LabWorkFlows.objects.all().order_by('-created_date').select_related('status', 'type')
    logging(request, 'access')
    return render(request, 'workflows/lab/workflows_tab.html', {'title': 'Lab Workflows - Workflows', 'labworkflows':labworkflows})


@login_required()
def quantification(request):
    if 'username' in request.session:
        print request.session.get('username')
    else:
        return HttpResponseRedirect('/saml/?slo')
    so = SampleOrderRel.objects.filter(sample__status__status='DNA_RECEIVED').order_by('sample__collection_date').select_related('patient', 'sample', 'order')
    lists = getSampleList(so)
    logging(request, 'access')
    try:
        lastobj = LabWorkFlows.objects.latest('id')
        new_id = lastobj.id+1
    except LabWorkFlows.DoesNotExist:
        new_id = 1
    return render(request, 'workflows/lab/q_new.html',
                {'s_lists': json.dumps(lists), 'title': 'Quantification : [ New Project ]', 'new_id':new_id, 'type':'QT'})


@login_required()
def quantification_redo(request):
    if 'username' in request.session:
        print(request.session.get('username'))
    else:
        return HttpResponseRedirect('/saml/?slo')

    if request.method != 'POST':
        messages.error(request, 'Only POST requests are accepted')
        return HttpResponseRedirect('/lab/quantification/')
    else:
        if 'redo_list' in request.POST and 'new_id' in request.POST:
            redo_list = request.POST['redo_list']
            new_id = request.POST['new_id']
            so = SampleOrderRel.objects.filter(sample_id__in=[redo_list])
            lists = getSampleList(so)
            return render(request, 'workflows/lab/q_redo.html',
                          {'s_lists': json.dumps(lists), 'title': 'Quantification : [ Redo New Project ] ',
                           'new_id': new_id})
        else:
            messages.error(request, ' Data ( redo list and new id ) is missing ')
            return HttpResponseRedirect(request.META['HTTP_REFERER'])


@login_required()
def fluidigm(request):
    if 'username' in request.session:
        print(request.session.get('username'))
    else:
        return HttpResponseRedirect('/saml/?slo')
    so = SampleOrderRel.objects.filter(sample__status__status='QPASS').order_by(
        'sample__collection_date').select_related('patient', 'sample', 'order')
    lists = getSampleList(so, 'FP')
    logging(request, 'access')
    try:
        lastobj = LabWorkFlows.objects.latest('id')
        new_id = lastobj.id+1
    except LabWorkFlows.DoesNotExist:
        new_id = 1
    return render(request, 'workflows/lab/fp_new.html',
                {'s_lists': json.dumps(lists), 'title': 'Fluidigm : [ New Project ]', 'new_id':new_id, 'type':'FP'})


@login_required()
def save_labworkflow(request, wtype):
    if 'username' in request.session:
        print request.session.get('username')
    else:
        return HttpResponseRedirect('/saml/?slo')
    if request.method != 'POST':
        message = 'Only POST requests are accepted'
    else:
        if wtype == 'QT':
            newstatus = 'QSTART'
        elif wtype == 'FP':
            newstatus = 'FSTART'
        else:
            HttpResponse('Wrong Type Information Entered')
        d = json.loads(request.body)
        lab_type = LabType.objects.get(labtype=wtype)
        lab_status = LabStatus.objects.get(labstatus=newstatus)
        # orders = d.get('order_list').split(',')
        c_labworkflows = LabWorkFlows(name=d.get('name'), type_id=lab_type.id, status_id=lab_status.id, username=str(request.user.username))
        message = c_labworkflows.save()
        sample_list = d.get('sample_list')
        sample_status = SampleStatus.objects.get(status='QSTART')
        for s in sample_list:
            tube = s.get('tube')
            sample_id = s.get('sample_id')
            order_id = s.get('order_id')
            container = s.get('container')
            result = s.get('result')
            wfs = LabWorkFlowStatus(status_id=lab_status.id, workflow_id=c_labworkflows.id, tube_number=tube, order_id=order_id, sample_id=sample_id, container=container, result = result)
            wfs.save()
            c_sample = Samples.objects.get(id=sample_id)
            c_sample.status = sample_status
            c_sample.save()
            # last_update = SampleProcessingLog.objects.filter(sample_id=sample_id).using('logs').order_by('id')[0].update_time
            SampleProcessingLog(sample_id=sample_id, prev_status='DNA_RECEIVED', update_status='QSTART',
                                name=c_sample.name, type=c_sample.type).log()

    return HttpResponse(message)

'''
    save / create QT type - Quantification project
'''


@login_required()
def save_qt(request):
    if 'username' in request.session:
        print(request.session.get('username'))
    else:
        return HttpResponseRedirect('/saml/?slo')
    if request.method != 'POST':
        message = 'Only POST requests are accepted'
    else:
        newstatus = 'QSTART'

        d = json.loads(request.body)
        lab_type = LabType.objects.get(labtype='QT')
        lab_status = LabStatus.objects.get(labstatus=newstatus)
        # orders = d.get('order_list').split(',')
        c_labworkflows = LabWorkFlows(name=d.get('name'), samples_list=d.get('sample_list'), type_id=lab_type.id, status_id=lab_status.id, username=str(request.user.username))
        message = c_labworkflows.save()
        sample_list = d.get('sample_list')
        sample_status = SampleStatus.objects.get(status=newstatus)
        for s in sample_list:
            tube = s.get('tube')
            sample_id = s.get('sample_id')
            order_id = s.get('order_id')
            container = s.get('container')
            wfs = LabWorkFlowStatus(status_id=lab_status.id, workflow_id=c_labworkflows.id, tube_number=tube, order_id=order_id, sample_id=sample_id, container=container)
            wfs.save()
            c_sample = Samples.objects.get(id=sample_id)
            c_sample.status = sample_status
            c_sample.save()
            SampleProcessingLog(sample_id=sample_id, prev_status='DNA_RECEIVED', update_status=newstatus,
                                name=c_sample.name, type=c_sample.type).log()

    return HttpResponse(message)


@login_required()
def uploadfile_qt(request):
    message = 'Done'
    if request.method != 'POST':
        message = 'Only POST requests are accepted'
    else:
        myFile = request.FILES['files']
        id = request.POST.get('id')
        id_type = request.POST.get('type')
        file_type = request.POST.get('file_type')
        try:
            path = functions.handle_uploaded_file(myFile, id_type, id, myFile.name, settings.BUCKET_ROOT)
            url = settings.GCLOUD_URL_ROOT + path
            try:
                file_db = GCloudFiles.objects.get(name=myFile.name, obj_type=id_type, obj_id=id, file_type=file_type, file_path=path)
                file_db.url = url
                file_db.upload_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                file_db.save()
            except GCloudFiles.DoesNotExist:
                file_db = GCloudFiles(name=myFile.name, obj_type=id_type, obj_id=id, file_type=file_type, url=url, file_path=path)
                file_db.save()

            qubit = QubitResultsParser.QubitResultsParser()
            result = qubit.parseResults(settings.GCLOUD_ROOT+path)
            wfs = LabWorkFlowStatus.objects.filter(workflow_id=id).order_by('tube_number')
            ls = lab_status_list(True)
            ss = sample_status_list(True)
            for i in range(len(wfs)):
                c_sample = Samples.objects.get(id=wfs[i].sample_id)
                if 'F' == c_sample.status.status[0]:       # skip if already did Finger Printing
                    pass
                else:
                    wfs[i].result = result[i+1][2]
                    if result[i+1][4] == 'PASS':
                        status_name = 'QPASS'
                    elif 'FAIL' in result[i+1][4]:
                        status_name = 'QFAIL'
                    elif 'HIGH' in result[i+1][4]:
                        status_name = 'QREDO'
                    wfs[i].status_id = ls.get(status_name)
                    wfs[i].save()

                    c_sample.status_id = ss.get(status_name)
                    c_sample.save()
            wf = LabWorkFlows.objects.get(id=id)
            wf.status_id = ls.get('QPASS')
            wf.save()

        except Exception as e:
            message = 'Error : %s'%e.message
    return HttpResponse(json.dumps(message))


'''
    save / create FP type - FingerPrinting project
'''


@login_required()
def uploadfile_fp(request):
    message = 'Done'
    if request.method != 'POST':
        message = 'Only POST requests are accepted'
    else:
        myFile = request.FILES['files']
        id = request.POST.get('id')
        id_type = request.POST.get('type')
        file_type = request.POST.get('file_type')
        try:
            path = functions.handle_uploaded_file(myFile, id_type, id, myFile.name, settings.BUCKET_ROOT)
            url = settings.GCLOUD_URL_ROOT + path
            try:
                file_db = GCloudFiles.objects.get(name=myFile.name, obj_type=id_type, obj_id=id, file_type=file_type, file_path=path)
                file_db.url = url
                file_db.upload_by = request.user
                file_db.upload_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                file_db.save()
            except GCloudFiles.DoesNotExist:
                file_db = GCloudFiles(name=myFile.name, obj_type=id_type, obj_id=id, file_type=file_type, url=url, file_path=path, upload_by=request.user)
                file_db.save()

            fparser = FluidigmResultsParser.FluidigmResultsParser()
            result = fparser.parseResults(settings.GCLOUD_ROOT+path)
            wfs = LabWorkFlowStatus.objects.filter(workflow_id=id).order_by('tube_number')
            ls = lab_status_list(True)
            ss = sample_status_list(True)
            for i in range(len(wfs)):
                # wfs[i].result = result[i]
                if 'PASS' in result[i+1]:
                    status_name = 'FPASS'
                elif 'FAIL' in result[i+1]:
                    status_name = 'FFAIL'

                wfs[i].status_id = ls.get(status_name)
                wfs[i].save()
                c_sample = Samples.objects.get(id=wfs[i].sample_id)
                c_sample.status_id = ss.get(status_name)
                c_sample.save()
            wf = LabWorkFlows.objects.get(id=id)
            wf.status_id = ls.get('FPASS')
            wf.save()

        except Exception as e:
            message = 'Error : %s'%e.message
    return HttpResponse(json.dumps(message))


@login_required()
def create_fp(request):
    if 'username' in request.session:
        print(request.session.get('username'))
    else:
        return HttpResponseRedirect('/saml/?slo')
    if request.method != 'POST':
        message = 'Only POST requests are accepted'
    else:
        newstatus = 'FSTART'

        d = json.loads(request.body)
        lab_type = LabType.objects.get(labtype='FP')
        lab_status = LabStatus.objects.get(labstatus=newstatus)
        samples = []
        sample_list = d.get('sample_list')
        sample_status = SampleStatus.objects.get(status=newstatus)
        c_labworkflows = LabWorkFlows(name=d.get('name'), result_data=d.get('result_data'), type_id=lab_type.id,
                                      status_id=lab_status.id, username=str(request.user.username))
        message = c_labworkflows.save()
        for s in sample_list:
            sample_id = s.get('sample_id')
            container = s.get('container')
            tube_number = s.get('tube')
            order_id = s.get('order_id')
            result = s.get('result')
            wfs = LabWorkFlowStatus(status_id=lab_status.id, workflow_id=c_labworkflows.id, sample_id=sample_id,
                                    container=container, tube_number=tube_number, result=result, order_id=order_id)
            wfs.save()
            c_sample = Samples.objects.get(id=sample_id)
            c_sample.status = sample_status
            c_sample.save()
            SampleProcessingLog(sample_id=sample_id, prev_status='QPASS', update_status=newstatus,
                                name=c_sample.name, type=c_sample.type).log()
            samples.append(sample_id)

    return HttpResponse(message)


@login_required()
def labwork_detail(request, wid):
    if 'username' in request.session:
        print request.session.get('username')
    else:
        return HttpResponseRedirect('/saml/?slo')
    logging(request, 'access')
    workflow = LabWorkFlows.objects.get(id=wid)
    wfs = LabWorkFlowStatus.objects.filter(workflow_id=wid).order_by('tube_number')
    if workflow.type.labtype == 'QT':
        redo_list = []
        for s in wfs:
            if s.status.labstatus == 'QREDO' and s.sample.status.status == 'QREDO':
                redo_list.append(s.sample_id)

    elif workflow.type.labtype == 'FP':
        worksheet = []
        for s in wfs:
            so = SampleOrderRel.objects.get(sample_id=s.sample_id, relation_id=1)
            worksheet.append({'asn': s.sample.asn, 'container': s.container, 'result': s.result,
                              'status': s.status.labstatus, 'status_name': s.status.labstatus_name, 'pname': so.patient.name()})

    else:
        redo_list = []

    title = workflow.type.labtype_name
    files = GCloudFiles.objects.filter(obj_id=wid, obj_type=title).order_by('-upload_date')

    if workflow.type.labtype == 'QT':                       # quantification
        template = 'workflows/lab/q_details.html'
    elif workflow.type.labtype == 'FP':                     # Fluidigm
        template = 'workflows/lab/FP_Worksheet.html'
        platemap = str(json.loads(str(workflow.result_data).replace("'", '"').replace('u', '')).get('platemap')).split(',')

        return render(request, template,
                      {'workflow': workflow, 'title': title, 'files': files, 'worksheet': json.dumps(worksheet), 'platemap': json.dumps(platemap)})
    else:                                                    # Sanger
        template = 'workflows/lab/q_details.html'
    return render(request, template,
                {'workflow':workflow, 'title': title , 'wf_status': wfs, 'files':files,'redo_list':','.join(map(str, redo_list))})
