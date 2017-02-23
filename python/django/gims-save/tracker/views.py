from django.shortcuts import render
from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.core import serializers
from users.models import UserMessage, UserProfile
from .models import Samples, Orders, OrderStatus, SampleOrderRel, Patients, SampleContainer, OrderPhenoTypes, \
    PatientOrderPhenoType, PatientOrderPhenoList, OrderGeneList, Notes, PeopleRelations, PatientRelations, \
    Family, OrderGroups, PatientFiles, SampleFiles
from .forms import OrderForm, OrderGeneListForm, NotesPatientForm, NotesOrderForm, PatientRelationsForm, \
    PatientRelationsEditForm, FamilyForm, OrderGroupForm, PatientForm, PatientFilesForm
from mybackend.models import CustomSQL, PhenoTypeLists, GeneLists

from mybackend import functions, LoadOntology
from logger.models import accessLog, loomLog, logging, orderlog, samplelog, log_history, OrderProcessingLog
import json, requests, os
from gims import settings
from django.contrib import messages
from .forms import SampleOrderRelForm, PatientOrderPhenoTypeForm, PhenoTypesForm, GeneListsForm
from datetime import datetime
from django.core.cache import cache
from bson import json_util


def custom_proc(request):
    return {
        'LOOMURL': settings.LOOMURL,
    }


def date_handler(obj):
    if hasattr(obj, 'isoformat'):
        return obj.isoformat()
    else:
        raise TypeError


def getPatientInfo(pid, what):
    patient = Patients.objects.get(pid=pid)
    if isinstance(what, list):
        result = []
        for i in what:
            result.append(getattr(patient, i))
    else:
        result = getattr(patient, what)
    return result


def getOrderInfo(oid, what):
    order = Orders.objects.get(id=oid)
    if isinstance(what, list):
        result = []
        for i in what:
            result.append(getattr(order, i))
    else:
        result = getattr(order, what)
    return result


def getOrderStatus(sid):
    orderstatus = OrderStatus.objects.get(id=sid)
    return getattr(orderstatus, 'status_name')


def getPatientRelations(rid, what):
    rel = PeopleRelations.objects.get(id=rid)
    return getattr(rel, what)


# BASE_SAMPLE_SQL = 'SELECT s.*,  o.id as order_id, o.order_name, rt.rel_name as relation, ot.type_name as order_type FROM tracker_samples s ' \
#                   ' left join tracker_sampleorderrel r on s.id = r.sample_id left join tracker_orders o on r.order_id = o.id ' \
#                   ' left join tracker_relations rt on r.relation_id = rt.id left join tracker_ordertype ot on o.type_id = ot.id'


SAMPLE_PATIENT_ORDER_SQL = 'SELECT s.*,  o.id as order_id, o.order_name, rt.rel_name as relation, ot.type_name as order_type ' \
                           'FROM tracker_samples s ' \
                 'left join tracker_sampleorderrel rel on s.id = rel.sample_id  ' \
                 'left join tracker_orders o on rel.order_id = o.id ' \
                   'left join tracker_sampleorderrel r on s.id = r.sample_id ' \
                  ' left join tracker_sorelations rt on r.relation_id = rt.id left join tracker_ordertype ot on o.type_id = ot.id '


# SAMPLE_PATIENT_ORDER_SQL = 'SELECT s.*,  o.id as order_id, o.order_name, os.status_name as order_status, ot.type_name as order_type ' \
#                            'FROM tracker_samples s ' \
# 				  ' left join tracker_patients p on p.pid = s.patient_id left join tracker_orders o on s.patient_id = o.patient_id ' \
# 				   'left join tracker_orderstatus os on os.id = o.status_id ' \
# 					'left join tracker_ordertype ot on o.type_id = ot.id'

BASE_SAMPLEFILES_SQL='SELECT sf.*, s.asn as asn, o.order_name as ordername from tracker_samplefiles sf ' \
                     'join tracker_samples s on sf.sample_id = s.id join tracker_orders o on sf.order_id = o.id'

'''
    Sample Related Views
'''


@login_required(login_url='/login/')
def samples_view(request):
    if 'username' in request.session:
        print(request.session.get('username'), request.session['username'])
    else:
        return HttpResponseRedirect('/saml/?slo')
    myc = CustomSQL()
    c_samples = myc.my_custom_sql(SAMPLE_PATIENT_ORDER_SQL +' order by s.collection_date, s.asn; ')
    so = SampleOrderRel.objects.all()
    container = functions.getSampleContainer_list()
    # container = SampleContainer.objects.all()
    # container_json = serializers.serialize('json', container)
    title = 'Samples'
    logging(request, 'access')
    return render(request, 'tracker/samples.html',
                  {'samples':json.dumps(c_samples, default=date_handler),'containers':json.dumps(container),
                   'sample_order': so, 'title': title})


SAMPLE_WORKFLOWS_SQL = 'SELECT * from tracker_samples s join logger_loomlog l on s.asn = l.relSample '


@login_required(login_url='/login/')
def sample_details(request, sid):
    if 'username' in request.session:
        print(request.session.get('username'), request.session['username'])
    else:
        return HttpResponseRedirect('/saml/?slo')
    myc = CustomSQL()
    c_samples = myc.my_custom_sql(SAMPLE_PATIENT_ORDER_SQL + ' WHERE s.id = "' + sid + '" order by s.asn; ')
    so = SampleOrderRel.objects.filter(sample_id=sid)
    if len(so) <= 0:
        message = "No Sample Matching ID : %s " % sid
        messages.error(request, message)
        logging(request, '400')
        return HttpResponseRedirect('/samples/')
    asn = so[0].sample.asn
    jsonstring_samples = json.dumps(c_samples, default=json_util.default)
    # c_samplefiles = myc.my_custom_sql(BASE_SAMPLEFILES_SQL  + ' WHERE s.id = "' + sid + '" ')
    files = SampleFiles.objects.filter(sample_id=sid)
    c_loomlog = loomLog.objects.using('logs').filter(relSample = asn)
    jsonstring_loomlog = serializers.serialize('json', c_loomlog, fields=('analysisID', 'workflowID', 'relOrder', 'acc_time', 'loomResponse'))
    title = 'Sample : ' + asn
    logging(request, 'access')
    return render(request, 'tracker/sample_details.html',
                  {'samples':jsonstring_samples,'so':so,  'files': files, 'workflows': jsonstring_loomlog, 'title': title},
                  context_instance=RequestContext(request, processors=[custom_proc]))


BASE_ORDER_SQL = 'SELECT *, o.id as orderid, up.title as ownername FROM tracker_orders o  ' \
                 'left join tracker_sampleorderrel rel on o.id = rel.order_id  ' \
                 'left join tracker_samples s on rel.sample_id = s.id ' \
                 'left join tracker_relations rt on rel.relation_id = rt.id' \
                ' left join tracker_ordertype ot on o.type_id = ot.id ' \
                'left join tracker_orderstatus os on o.status_id = os.id  ' \
                 'left join users_userprofile up on o.owner = up.user_id'

# ORDER_PATIENT_SAMPLE_SQL = 'SELECT o.*, ot.*, os.*, up.*, s.asn as asn,  s.source as source, s.container as container, ' \
#                            's.id as sampleid,  o.id as orderid, up.title as ownername FROM tracker_orders o  ' \
#                  'left join tracker_patients p on o.patient_id = p.pid  ' \
#                  'left join tracker_samples s on s.patient_id = p.pid ' \
#                 ' left join tracker_ordertype ot on o.type_id = ot.id ' \
#                 'left join tracker_orderstatus os on o.status_id = os.id  ' \
#                  'left join users_userprofile up on o.owner_id = up.user_id'


SIMPLE_ORDER_SQL = 'SELECT *, o.id as order_id FROM tracker_orders o ' \
                ' left join tracker_ordertype ot on o.type_id = ot.id ' \
                'left join tracker_orderstatus os on o.status_id = os.id ' \
                'LEFT JOIN users_userprofile u on u.id = o.owner_id'

'''
    Order Related Views
'''


@login_required(login_url='/saml/')
def orders_view(request):
    if 'username' in request.session:
        print(request.session.get('username'), request.session['username'])
    else:
        return HttpResponseRedirect('/saml/?slo')
    myc = CustomSQL()
    mysql = SIMPLE_ORDER_SQL+'  order by o.flag desc, o.due_date; '
    c_orders = myc.my_custom_sql(mysql)            # raw dict
    logging(request, 'access')
    return render(request, 'tracker/orders.html', {'orders':json.dumps(c_orders)})


ORDER_GROUPS_SQL = 'SELECT * FROM tracker_ordergroups g ' \
             'LEFT JOIN tracker_orders o on g.order_id = o.id ' \
             'LEFT JOIN tracker_orderrelations r on g.relation_id = r.id ' \
             ' LEFT JOIN  tracker_affectedstatus s on g.affectedstatus_id = s.id ' \
             'WHERE group_id in (SELECT group_id FROM tracker_ordergroups WHERE order_id = %s) ORDER BY group_id, order_id'


@login_required(login_url='/saml/')
def order_details(request, oid):
    if 'username' in request.session:
        print(request.session.get('username'), request.session['username'])
    else:
        return HttpResponseRedirect('/saml/?slo')
    myc = CustomSQL()
    # c_orders = myc.my_custom_sql(ORDER_PATIENT_SAMPLE_SQL+' WHERE o.id = "' + oid + '" order by o.due_date; ')            # raw dict
    # oname = c_orders[0]['order_name']
    # phenolists = PhenoTypeLists.objects.select_related('category').all().order_by('mybackend_phenotypecategory.priority', 'priority', 'name')
    so = SampleOrderRel.objects.filter(order_id=oid).select_related('order', 'sample')
    if len(so) <= 0:
        message = "No Order Matching ID : %s " % oid
        messages.error(request, message)
        logging(request, '400')
        return HttpResponseRedirect('/orders/')
    oname = so[0].order.order_name
    try:
        c_phenolist = OrderPhenoTypes.objects.filter(order_id=oid)
        jsonstring_phenolist = serializers.serialize('json', c_phenolist)
    except OrderPhenoTypes.DoesNotExist:
        jsonstring_phenolist = []
    try:
        genelist = OrderGeneList.objects.select_related('genelist').filter(order_id=oid)
    except OrderGeneList.DoesNotExist:
        print ('no genelist')
    c_loomlog = loomLog.objects.using('logs').filter(relOrder=oname)
    jsonstring_loomlog = serializers.serialize('json', c_loomlog,
                                               fields=('analysisID', 'workflowID', 'relSample', 'acc_time', 'loomResponse'))
    # order_group_ids = OrderGroups.objects.filter(order_id=oid)
    order_groups = functions.doSQL(ORDER_GROUPS_SQL%oid)
    title = 'Order : ' + oname
    logging(request, 'access', title)
    return render(request, 'tracker/orders/Details.html',
                  {'so': so, 'groups': order_groups,  'phenolists' : c_phenolist, 'workflows': jsonstring_loomlog, 'genelists':genelist, 'title': title},
                  context_instance=RequestContext(request, processors=[custom_proc]))


@login_required(login_url='/saml/')
def order_edit(request, oid):
    if request.method == 'POST':
        change = 'updated'
        c_order = Orders.objects.get(id=oid)
        if c_order.phenotype != request.POST['phenotype']:
            c_order.phenotype = request.POST['phenotype']
            change += ' phenotype / '
        if c_order.physician_phone != request.POST['physician_phone']:
                c_order.physician_phone = request.POST['physician_phone']
                change += ' physician contact info / '
        if c_order.owner_id != request.POST['owner']:
            prev = c_order.owner or '  '
            userprofile = UserProfile.objects.get(id=request.POST['owner'])
            change += ' ownership / From ' + str(prev) + ' To ' + userprofile.username
            c_order.owner_id = request.POST['owner']
        if str(c_order.status_id) != str(request.POST['status']):
            new_status = getOrderStatus(request.POST['status'])
            change += ' Status / From ' + str(c_order.status) + ' To ' + new_status
            OrderProcessingLog(order_id=oid, order_name=c_order.order_name, prev_time=c_order.updated,
                    order_type=c_order.type, prev_status=str(c_order.status), update_status=new_status).log()
            c_order.status_id = request.POST['status']
        if c_order.desc != request.POST['desc']:
            c_order.desc = request.POST['desc']
            change += ' description / '
        if c_order.flag != request.POST['flag']:
            c_order.flag = request.POST['flag']
            if c_order.flag =='':
                change += ' Removed Flag '
            else:
                change += ' Added Flag - ' + c_order.flag
        if change != 'updated':
            c_order.save()
            orderlog(request, oid, c_order.order_name, change)
        return HttpResponseRedirect('/order/'+oid+'/')
    else:
        order = Orders.objects.get(id = oid)
        # order.lab_status = order.get_lab_status_display()
        form = OrderForm(instance=order)
    logging(request, 'access')
    return render(request, 'tracker/EditOrder.html', {'form' : form, 'oid': oid})


@login_required(login_url='/saml/')
def order_notes(request, oid):
    if request.method == 'POST':
        form = NotesOrderForm(request.POST)
        if form.is_valid():
            recipients = request.POST.getlist('recipients')
            obj = form.save(commit=False)
            obj.order_id = oid
            obj.writer=request.user
            obj.recipients = ','.join(recipients)
            obj.save()
            order_name = getOrderInfo(oid, 'order_name')
            orderlog(request, oid, order_name, 'new note added ')
            for recipient in recipients:
                message = UserMessage( user_id=recipient, related_order_id = oid,
                                       related_note_id = obj.id, message = 'new note on ' + order_name , sender = request.user)
                message.save()
        notes = Notes.objects.filter(order_id=oid).order_by('-update_time')
    else:
        try:
            notes = Notes.objects.filter(order_id = oid).order_by('-update_time')
        except :
            notes=[]
    if len(notes) == 0:
        notes = [{'id': ' --', 'update_time': ' -- ', 'category': ' -- ', 'note': 'no note'}]
    pid = getOrderInfo(oid, 'patient_id')
    form = NotesOrderForm(initial={'order': oid, 'patient_id':pid})
    logging(request, 'access')
    return render(request, 'tracker/orders/Order_Notes.html', {'form' : form, 'oid': oid, 'notes':notes})


@login_required(login_url='/saml/')
def order_groups(request):
    gid = None
    oid = None
    if 'gid' in request.META['QUERY_STRING']:
        gid = request.GET.get('gid')
        groups = OrderGroups.objects.filter(group_id=gid).order_by('group_id', 'order')
    elif 'oid' in request.META['QUERY_STRING']:
        oid = request.GET.get('oid')
        groups = OrderGroups.objects.filter(order_id=oid).order_by('group_id', 'order')
    else:
        groups = OrderGroups.objects.filter().order_by('group_id')

    return render(request, 'tracker/orders/Order_Groups.html', {'groups': groups, 'gid' : gid, 'oid' : oid})


@login_required(login_url='/saml/')
def ordergroup_action(request, action):
    if request.method == 'POST':
        form = OrderGroupForm(request.POST)
        action = request.POST['action']
        gid = request.POST['group_id']
        oid = request.POST['order']
        if form.is_valid():

            if action == 'New':
                form.save()
            elif action == 'Add':
                if OrderGroups.objects.filter(group_id=gid, order_id=oid).count() > 0:
                    messages.error(request, ' Patient already exists in Family Group ')
                else:
                    form.save()
        else:
            action = request.POST['action']
            messages.error(request, form.errors)
        return HttpResponseRedirect('/order/groups/%s/?gid=%s' % (action, gid) )
    else:
        if action == 'New':      # create new family group
            try:
                groups = OrderGroups.objects.filter().latest('id')
                gid = 'OG_' + str(groups.id + 1)
            except OrderGroups.DoesNotExist:
                gid = 'OG_1'
            oid = request.GET.get('oid')
            groups=[]
        else:
            gid = request.GET.get('gid')
            oid = request.GET.get('oid')

            groups = OrderGroups.objects.filter(group_id=gid)
        form = OrderGroupForm(initial={'group_id': gid, 'order_id': oid})
    return render(request, 'tracker/orders/Order_Groups_Edit.html',
                  {'form': form, 'action': action, 'groups': groups})


'''
    patient related def
'''


@login_required(login_url='/saml/')
def patients(request):
    if 'username' in request.session:
        print(request.session.get('username'), request.session['username'])
        if 'Interpretation' not in request.session.get('role') and 'Manager' not in request.session.get('role'):
            message = " You do not have permission to load  %s" % request.path_info
            messages.error(request, message)
            logging(request, 'UnAuthorized')
            return HttpResponseRedirect('/')
    else:
        return HttpResponseRedirect('/saml/?slo')
    c_patients = Patients.objects.all()
    family = Family.objects.filter(patient_id__in=c_patients)
    jsonstring_patients = serializers.serialize('json', c_patients)
    logging(request, 'access')
    return render(request, 'tracker/patients.html', {'patients':jsonstring_patients.replace("'","\\'"), 'family':family})


@login_required(login_url='/saml/')
def patient_edit(request, pid):
    if 'username' in request.session:
        print(request.session.get('username'), request.session['username'])
        if 'Interpretation' not in request.session.get('role') and 'Manager' not in request.session.get('role'):
            message = " You do not have permission to load  %s" % request.path_info
            messages.error(request, message)
            logging(request, 'UnAuthorized')
            return HttpResponseRedirect('/')
    else:
        return HttpResponseRedirect('/saml/?slo')
    if request.method == 'POST':
        change = 'updated'
        patient = Patients.objects.get(pid=pid)
        if patient.phone != request.POST['phone']:
            patient.phone = request.POST['phone']
            change += ' phone / '
        if patient.first_name != request.POST['first_name']:
                patient.first_name = request.POST['first_name']
                change += ' first name / '
        if patient.middle_name != request.POST['middle_name']:
                patient.middle_name = request.POST['middle_name']
                change += ' middle name / '
        if patient.last_name != request.POST['last_name']:
                patient.last_name = request.POST['last_name']
                change += ' last name / '
        if patient.ethnicity != request.POST['ethnicity']:
            change += ' ownership / From ' + patient.ethnicity + ' To ' + request.POST['ethnicity']
            patient.ethnicity = request.POST['ethnicity']
        if patient.memo != request.POST['memo']:
            patient.memo = request.POST['memo']
            change += ' memo / '

        if change != 'updated':
            patient.save()
            log_history(request, 'patient', patient.id, patient.mrn, change)
        return HttpResponseRedirect('/patient/'+pid+'/')
    else:
        patient = Patients.objects.get(pid = pid)
        form = PatientForm(instance=patient)
    logging(request, 'access')
    return render(request, 'tracker/Edit_Patient.html', {'form' : form, 'pid': pid})


@login_required(login_url='/saml/')
def patient_notes(request, pid):
    p_info = functions.getPatientInfo(pid, ['first_name', 'last_name', 'mrn'])
    p_name = p_info['first_name']+' '+p_info['last_name']+'('+ p_info['mrn']+')'
    if request.method == 'POST':
        form = NotesPatientForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            recipients = request.POST.getlist('recipients')
            obj.patient_id = pid
            obj.writer = request.user
            obj.recipients = ','.join(recipients)
            obj.save()
            pname = functions.getPatientInfo(pid, ['first_name', 'last_name'])
            log_history(request, 'patient', pid, pname['first_name'] +'  '+ pname['last_name'], 'new note added ')
            for recipient in recipients:
                message = UserMessage( user_id=recipient, related_note_id = obj.id,
                                       message = 'new note on ' + p_name , sender = request.user)
                message.save()
        notes = Notes.objects.filter(patient_id=pid).order_by('-update_time', 'order_id')
    else:
        try:
            notes = Notes.objects.filter(patient_id = pid).order_by('-update_time', 'order_id')
        except :
            notes=[]
    if len(notes) == 0:
        notes = [{'id': ' --', 'update_time': ' -- ', 'category': ' -- ', 'note': 'no note'}]
    form = NotesPatientForm(initial={'patient_id':pid})
    logging(request, 'access')
    return render(request, 'tracker/Patient_Notes.html', {'form' : form, 'pid': pid, 'notes':notes, 'p_name': p_name})


FAMILY_SQL = 'SELECT * FROM tracker_family f ' \
             'LEFT JOIN tracker_patients p on f.patient_id = p.id left JOIN tracker_familyrole r on f.role_id = r.id ' \
             ' LEFT JOIN tracker_affectedstatus s on f.affectedstatus_id = s.id ' \
             'WHERE family_id in (SELECT family_id FROM tracker_family WHERE patient_id = %s) ORDER BY family_id'


@login_required(login_url='/saml/')
def patient_files(request, pid):
    patient = Patients.objects.get(pid = pid)
    try:
        p_files = PatientFiles.objects.filter(patient_id=patient.id)
    except:
        p_files = []
    return render(request, 'tracker/patient/Files.html', {'p_files':p_files, 'patient':patient} )


@login_required(login_url='/saml/')
def patient_files_action(request, pid, action):
    if 'username' in request.session:
        if 'interpretation' not in request.session.get('role').lower() and 'manager' not in request.session.get(
                'role').lower():
            message = " You do not have permission to load  %s" % request.path_info
            messages.error(request, message)
            logging(request, 'UnAuthorized')
            return HttpResponseRedirect('/')
    else:
        return HttpResponseRedirect('/saml/?slo')
    try:
        patient = Patients.objects.get(pid=pid)
    except Exception as e:
        messages.error(request, e.message)
        return HttpResponseRedirect('/patients/')
    fid = request.GET.get('fid')
    if request.method == 'POST':
        form = PatientFilesForm(request.POST)
        action = request.POST['action']
        if form.is_valid():
            # location = settings.GCLOUD_ROOT + '/Patient/'
            f = request.FILES.get('file')
            if f:
                f_name = request.POST.get('file_name') and request.POST.get('file_name')+f._name[f._name.find('.'):]  or f._name

            if action == 'Add':
                if f:
                    path  = functions.handle_uploaded_file(f, 'Patient', pid, f_name)
                    obj = form.save(commit=False)
                    obj.file_path = path
                    obj.file_name = f_name
                    obj.url = settings.GCLOUD_URL_ROOT + path
                    obj.save()
                    return HttpResponseRedirect('/patient/' + pid + '/Files/')
                else:
                    messages.error(request, 'Please, choose a file')
                    action = request.POST['action']

            else:           #edit

                    obj = PatientFiles.objects.get(id=fid)
                    obj.file_title = request.POST['file_title']
                    obj.desc = request.POST['desc']
                    obj.type = request.POST['type']
                    if f:
                        path = functions.handle_uploaded_file(f, 'Patient', pid, f_name)
                        obj.file_path = path
                        obj.file_name = f_name
                        obj.url = settings.GCLOUD_URL_ROOT + path
                    obj.save()
                    return HttpResponseRedirect('/patient/'+pid+'/Files/')

        else:
            message = form.errors
            messages.error(request, message)
            action = request.POST['action']
    else:
        if action == 'Add':
            form = PatientFilesForm(initial={'patient': patient})
        else:
            edit_file = PatientFiles.objects.get(id=fid)
            data = {'patient': patient, 'file_title':edit_file.file_title, 'desc':edit_file.desc, 'type':edit_file.type}
            form = PatientFilesForm(initial=data)

    try:
        p_files = PatientFiles.objects.filter(patient_id=patient.id)
    except:
        p_files = []

    return render(request, 'tracker/patient/Edit_Files.html',
                  {'form':form, 'pid':pid, 'action':action, 'p_files':p_files, 'fid': fid})


# patient details page
@login_required(login_url='/saml/')
def patient_details(request, pid):
    if 'username' in request.session:
        if 'interpretation' not in request.session.get('role').lower() and 'manager' not in request.session.get(
                'role').lower():
            message = " You do not have permission to load  %s" % request.path_info
            messages.error(request, message)
            logging(request, 'UnAuthorized')
            return HttpResponseRedirect('/')
    else:
        return HttpResponseRedirect('/saml/?slo')

    try:
        patient = Patients.objects.get(pid=pid)
    except Exception as e:
        messages.error(request, e.message)
        return HttpResponseRedirect('/patients/')

    # family = Family.objects.filter(patient_id=patient.id)
    family = functions.doSQL(FAMILY_SQL%patient.id)

    rid = PeopleRelations.objects.get(rel_name='SELF')
    selfs = PatientRelations.objects.filter(main=pid, relationship=rid.id).values('relative')
    pids = [pid]
    for s in selfs:
        pids.append(s['relative'])
    samples = Samples.objects.filter(patient_id__in=pids).order_by('asn')
    orders = Orders.objects.filter(patient_id__in=pids)
    so = SampleOrderRel.objects.filter(patient_id=patient.id)
    ped_file = None
    try:
        files = PatientFiles.objects.filter(patient_id=patient.id)
        for f in files:
            if f.type == 'Pedigree':
                ped_file = f
    except PatientFiles.DoesNotExist:
        files = None

    relative_list = []
    try:
        relatives = PatientRelations.objects.filter(main=pid)
        for f in relatives:
            ethnicity, mrn = getPatientInfo(f.relative, ['ethnicity', 'mrn'])
            relative_list.append({'relative': f.relative, 'relationship': f.relationship, 'ethnicity': ethnicity, 'mrn': mrn})
    except Exception as e:
        messages.error(request, e.message)

    oids=[]
    for order in orders:
        oids.append(int(order.id))

    if len(oids)>0:
        phenotypes = OrderPhenoTypes.objects.filter(order_id__in=oids)
    else:
        phenotypes =[]
    title = 'Patient : ' + pid
    logging(request, 'access', title)
    return render(request, 'tracker/patient/Details.html', {'patient':patient, 'samples':samples, 'ped_file': ped_file,
            'family': family, 'phenotypes': phenotypes,
            'so':so,  'orders':orders, 'relative': relative_list, 'p_files': files, 'title': title})


@login_required(login_url='/saml/')
def patient_relationship(request, pid):

    if request.method == 'POST':
        form = PatientRelationsForm(request.POST)
        action = request.POST['action']
        if form.is_valid():
            main = request.POST['main']
            relative = request.POST['relative']
            relationship = request.POST['relationship']

            if action == 'delete':
                rel1 = PatientRelations.objects.get(main=relative, relative=main)
                rel1.delete()
                rel2 = PatientRelations.objects.get(main=main, relative=relative)
                rel2.delete()
                return HttpResponseRedirect('/patient/' + pid + '/')
            else:

                # relative_sex = getPatientInfo(relative, 'sex')
                relationship_obj = PeopleRelations.objects.get(id=relationship)
                if relationship_obj.rel == 'SELF':
                    relative_relationship = relationship_obj
                else:
                    main_sex = getPatientInfo(main, 'sex')
                    if main_sex == 'Male' or main_sex == 'M':
                        what = 'back_relation_male'
                    else:
                        what = 'back_relation_female'
                    relative_relationship = getPatientRelations(relationship, what)
                if action == 'Add':
                    if PatientRelations.objects.filter(main=relative, relative=main).count() ==0:
                        form.save()
                        rel = PatientRelations(main=relative, relative=main, relationship=relative_relationship)
                        rel.save()
                        # add family group ?  - if necessary here YOUNG

                        return HttpResponseRedirect('/patient/' + pid + '/')
                    else:
                        messages.error(request, 'Relationship Exists')
                        action = 'Edit'
                        form = PatientRelationsForm(
                            initial={'main': main, 'relative': relative, 'relationship': relationship})
                else:
                    rel1 = PatientRelations.objects.get(main=main, relative=relative)
                    rel1.relationship_id = relationship
                    rel1.save()
                    rel2 = PatientRelations.objects.get(main=relative, relative=main)
                    rel2.relationship_id = relative_relationship
                    rel2.save()
                    return HttpResponseRedirect('/patient/' + pid + '/')
        else:
            action=request.POST['action']
            # form = form
    else:
        if not request.META['QUERY_STRING']:
            form = PatientRelationsForm(initial={'main': pid})
            action = 'Add'
        else:
            main = request.GET.get('main')
            relative = request.GET.get('relative')
            relationship = request.GET.get('relationship')
            if PatientRelations.objects.filter(main=relative, relative=main).count() != 0:
                form = PatientRelationsEditForm(initial={'main': main, 'relative': relative, 'relationship': relationship})
                action = 'Edit'
            else:
                form = PatientRelationsForm(initial={'main': pid, 'relative': relative})
                action = 'Add'

    return render(request, 'tracker/Patient_Relationship.html', {'form':form, 'pid': pid, 'action': action})


@login_required(login_url='/saml/')
def patient_family(request, pid):
    patients = Patients.objects.get(pid = pid)
    fid = "F_1"  # default family id

    try:
        family = Family.objects.filter(patient_id=patients.id)
        fid = family[0].family_id
    except Family.DoesNotExist:
        family = []
        fid = fid

    if request.method == 'POST':
        form = FamilyForm(request.POST)
        action = request.POST['action']
        if form.is_valid():
            fid = request.POST['family_id']
            patient_id = request.POST['patient']
            if action == 'Add':
                form.save()
                pname = functions.getPatientInfo(pid, ['first_name', 'last_name'])
                log_history(request, 'patient', pid, pname['first_name'] + '  ' + pname['last_name'], 'Family Member added ')
        else:
            action = request.POST['action']
    else:
        if not request.META['QUERY_STRING']:
            form = FamilyForm(initial={'family_id': fid,  'patient_id': pid})
            action = 'Add'
        else:
            action = 'Edit'
            fid = request.GET.get('fid')
            form = FamilyForm(initial={'family_id': fid, 'patient_id': pid})

    return render(request, 'tracker/Patient_Family.html',
                  {'form': form, 'pid': pid, 'action': action, 'messages': messages, 'family': family })


@login_required(login_url='/saml/')
def families(request):
    fid = None
    pid = None
    if 'fid' in request.META['QUERY_STRING']:
        fid = request.GET.get('fid')
        family = Family.objects.filter(family_id=fid).order_by('family_id', 'patient')
    elif 'pid' in request.META['QUERY_STRING']:
        pid = request.GET.get('pid')
        family = Family.objects.filter(patient_id=pid).order_by('family_id', 'patient')
    else:
        family = Family.objects.filter().order_by('family_id')

    return render(request, 'tracker/Families.html', {'family': family, 'fid' : fid, 'pid' : pid})


@login_required(login_url='/saml/')
def families_action(request, action):
    if request.method == 'POST':
        form = FamilyForm(request.POST)
        action = request.POST['action']
        if form.is_valid():
            fid = request.POST['family_id']
            pid = request.POST['patient']
            if action == 'New':
                form.save()
                patient = Patients.objects.get(id=pid)
                # pname = functions.getPatientInfo(pid, ['first_name', 'last_name'])
                log_history(request, 'patient', pid, patient.first_name + '  ' + patient.last_name,
                            'added to new Family group ' + fid )
            elif action == 'Add':
                if Family.objects.filter(family_id=fid, patient_id=pid).count() > 0:
                    messages.error(request, ' Patient already exists in Family Group ')
                else:
                    form.save()
                    patient = Patients.objects.get(id=pid)
                    # pname = functions.getPatientInfo(pid, ['first_name', 'last_name'])
                    log_history(request, 'patient', pid, patient.first_name + '  ' + patient.last_name,
                                'added to Family Group : ' + fid)
            elif action == 'Edit':
                try:
                    f = Family.objects.get(family_id=fid, patient_id=pid)
                    f.role_id = request.POST['role']
                    f.affectedstatus_id = request.POST['affectedstatus']
                    f.save()
                except Family.DoesNotExist:
                    messages.error(request, ' Patient not exists in Family Group ')
                    return HttpResponseRedirect('/families/Add/?fid=%s' % fid)
                except:
                    messages.error(request, ' Could not update Family Group ')
                return HttpResponseRedirect('/families/Edit/?fid=%s&pid=%s' % (fid, pid))
            return HttpResponseRedirect('/families/Add/?fid=%s'%fid)
        else:
            action = request.POST['action']
    else:
        if action == 'New':      # create new family group
            try:
                family = Family.objects.filter().latest('id')
                fid = 'F_' + str(family.id + 1)
            except Family.DoesNotExist:
                fid = 'F_1'
            pid = request.GET.get('pid')
            family=[]
        else:
            fid = request.GET.get('fid')
            pid = request.GET.get('pid')

        family = Family.objects.filter(family_id=fid)
        form = FamilyForm(initial={'family_id': fid, 'patient': pid})
    return render(request, 'tracker/Patient_Family.html',
                  {'form': form, 'action': action, 'family': family})

# patient pedigree chart
@login_required(login_url='/saml/')
def patient_pedigree(request, pid):
    if 'username' in request.session:
        print(request.session.get('username'), request.session['username'])
        # if 'Interpretation' not in request.session.get('role') and 'Manager' not in request.session.get('role'):
        #     message = " You do not have permission to load  %s" % request.path_info
        #     messages.error(request, message)
        #     logging(request, 'UnAuthorized')
        #     return HttpResponseRedirect('/')
    else:
        return HttpResponseRedirect('/saml/?slo')
    patient = Patients.objects.get(pid=pid)
    try:
        # pedigree = Pedigree.objects.get(patient_id=pid)
        pedigree = functions.getFamily(pid, True)
    except:
        pedigree =[{'id':patient.pid, 'name':patient.first_name+' '+patient.last_name, 'sex':patient.sex, 'carrierStatus':'unknown' }]
    logging(request, 'access')
    return render(request, 'tracker/patient_pedigree.html', {'patient': patient, 'pedigree': json.dumps(pedigree)})


@login_required(login_url='/saml/')
def add_SampleOrderRel(request):
    if request.method == 'POST':
        form = SampleOrderRelForm(request.POST)
        if form.is_valid():
            if request.POST['action'] == 'delete':
                sor = SampleOrderRel.objects.get(order_id=request.POST['order'], sample_id=request.POST['sample'], relation_id=request.POST['relation'])
                sor.delete()
            elif request.POST['action'] == 'edit':
                sor = SampleOrderRel.objects.get(order_id=request.POST['order'], sample_id=request.POST['sample'])
                sor.relation_id = request.POST['relation']
                sor.save()
            else:           # add

                if SampleOrderRel.objects.filter(order_id=request.POST['order'], sample_id=request.POST['sample']).exists():
                    return render(request, 'tracker/SampleOrderRel.html',
                                  {'form': form, 'action': request.POST['action'], 'message':' Record Exists - do you want to update ?'})
                else:
                    form.save()
            return HttpResponseRedirect('/order/'+request.POST['order']+'/')

        return render(request, 'tracker/SampleOrderRel.html', {'form': form, 'action': request.POST['action']})
    else:

        if not request.META['QUERY_STRING']:
            form = SampleOrderRelForm()
            action = 'add'
        else:
            oid = request.GET.get('oid')
            sid = request.GET.get('sid')
            rid = request.GET.get('rid')
            try:
                sor = SampleOrderRel.objects.get(order_id=oid, sample_id=sid, relation_id=rid)
                form = SampleOrderRelForm(instance=sor)
                action = 'edit'
            except SampleOrderRel.MultipleObjectsReturned:
                form = SampleOrderRelForm(initial={'order': oid, 'sample': sid, 'relation': rid})
                action = 'edit'
            except SampleOrderRel.DoesNotExist:
                form = SampleOrderRelForm(initial={'order': oid, 'sample': sid, 'relation': rid})
                action = 'add'
    logging(request, 'access')
    return render(request, 'tracker/SampleOrderRel.html', {'form': form, 'action':action })


@login_required(login_url='/saml/')
def add_patient_order_phenopype(request, oid):
    if request.method == 'POST':

        try:
            c_phenolist = PatientOrderPhenoList.objects.get(order_id=oid)
            c_phenolist.pheno_checklists = request.POST['checkList']
            c_phenolist.pheno_valuelists = request.POST['textInput']
            c_phenolist.save()


        except PatientOrderPhenoList.DoesNotExist:
            c_phenolist = PatientOrderPhenoList(order_id = oid, pheno_checklists = request.POST['checkList'], pheno_valuelists = request.POST['textInput'])
            c_phenolist.save()

        return HttpResponse(json.dumps({'reURL':'/order/'+oid+'/'}))
    else:
        try:
            c_phenolist = PatientOrderPhenoList.objects.get(order_id=oid)
            c_list = {'checkInput':str(c_phenolist.pheno_checklists), 'textInput' : str(c_phenolist.pheno_valuelists)}
            action = 'edit'

        except PatientOrderPhenoList.DoesNotExist:
            c_list = {'checkInput': [], 'textInput': '{}'}
            action = 'add'
        order = Orders.objects.get(id=oid)

    phenolists = PhenoTypeLists.objects.select_related('category').all().order_by('mybackend_phenotypecategory.priority', 'priority', 'name')
    logging(request, 'access')
    return render(request, 'tracker/PatientOrderPhenoType.html', {'phenolists': phenolists, 'c_list':c_list,  'action':action, 'order':order })


@login_required(login_url='/saml/')
def order_phenopypes(request, oid):
    try:
        c_phenolists = OrderPhenoTypes.objects.filter(order_id=oid).order_by('acc')
    except OrderPhenoTypes.DoesNotExist:
        c_phenolists = []
    order = Orders.objects.get(id=oid)

    logging(request, 'access')
    return render(request, 'tracker/OrderPhenoTypes.html', {'phenolists': c_phenolists, 'order': order})


@login_required(login_url='/saml/')
def order_sortedDisease(request, oid):
    order = Orders.objects.get(id=oid)
    try:
        c_phenolists = OrderPhenoTypes.objects.filter(order_id=oid).order_by('acc')
    except OrderPhenoTypes.DoesNotExist:
        c_phenolists = []


    hpolist=[]
    for plist in c_phenolists:
        hpolist.append(int(plist.acc.split(':')[1]))

    if len(hpolist) == 0:
        return render(request, 'tracker/OrderSortedDiseases.html',
                  {'phenolists': [], 'order': order, 'sortedlists': []})
    # print datetime.now()
    str_hpolist = ','.join(str(e) for e in hpolist)
    #
    if cache.get(str_hpolist):
        newList = cache.get(str_hpolist)
        print('disease list  from cache')
    else:

        if cache.get('ontology'):
                    l = cache.get('ontology')
                    print('oncology from cache')
        else:
                    l = LoadOntology.LoadOntology()
                    cache.set('ontology', l)

        unsortedDiseaseList = l.getSortedDiseaseList(hpolist, None)
        sortedList = sorted(unsortedDiseaseList , key=lambda x:x[1], reverse=True)
        diseaseList=''
        for ulist in sortedList:
                diseaseList += ulist[0]+','
        c_diseases = functions.doSQL('Select * from  public_db.external_object_disease where disease_id in (%s)'%diseaseList[:-1])

        newList = []
        for ulist in sortedList:
                    for d in c_diseases:
                        if d['disease_id'] == ulist[0]:
                            newList.append({'id': d['db_name']+':'+d['disease_id'], 'title': d['disease_title'], 'score' : ulist[1]})

        cache.set(str_hpolist, newList)

    logging(request, 'access')
    return render(request, 'tracker/OrderSortedDiseases.html', {'phenolists': c_phenolists, 'order': order, 'sortedlists': newList})


@login_required(login_url='/saml/')
def add_order_phenopype(request, oid):
    if request.method == 'POST':
        try:
            c_phenolist = OrderPhenoTypes.objects.get(order_id=oid, acc=request.POST['acc'])
            message = 'duplicated'
        except OrderPhenoTypes.DoesNotExist:
            c_phenolist = OrderPhenoTypes(order_id=oid, acc=request.POST['acc'], name=request.POST['name'])
            c_phenolist.save()
            message = 'add new'
        return HttpResponse(message)
    else:
        return HttpResponse('error')


@login_required(login_url='/saml/')
def edit_order_phenopype(request, oid):
    if request.method == 'POST':
        try:
            c_phenolist = OrderPhenoTypes.objects.get(order_id=oid, acc=request.POST['acc'])
            c_phenolist.delete()
            message = 'deleted'
        except OrderPhenoTypes.DoesNotExist:
            message = 'cannot find record'
        return HttpResponse(message)
    else:
        return HttpResponse('error')


@login_required(login_url='/saml/')
def phenotype_omim(request, acc):
    omim_data = functions.getOmimData(acc)
    return render(request, 'tracker/PhenoType_OMIM.html', {'omim_data': omim_data['entry']})


def getHsa(hsalist, gid):
    lines = hsalist.split('\n')
    for line in lines:
        line_data = line.split('\t')
        lists = line_data[1].split(',')
        for l in lists:
            if l.strip() == gid:
                return line_data[0]


@login_required(login_url='/saml/')
def phenotype_kegg(request, gid):
    url = 'http://rest.kegg.jp/find/genes/hsa+'+gid

    response = requests.get(url)
    hsa = getHsa(response.content, gid)
    url = 'http://rest.kegg.jp/link/pathway/'+hsa
    response = requests.get(url)
    pathwayHtmlList = []
    if len(response.content) < 10:
        pathwayHtml='No Entry'
        pathwayID ='no-entry'
        pathwayHtmlList.append({'title': 'No Entry', 'details': ' '})
    else:
        pathway = response.content.split('\t')[1]
        pathwayID = pathway[5:-1]
        url = 'http://rest.kegg.jp/get/'+pathwayID+'/'
        response = requests.get(url)
        pathwayHtml = response.content
        pathwayHtmlArray = pathwayHtml.split('\n')
        for line in pathwayHtmlArray:
            linesplit = line.split(' ')
            pathwayHtmlList.append({'title': linesplit[0], 'details' : ' '.join(linesplit[1:])})

        if os.path.isfile(settings.MEDIA_ROOT+'/KEGG/'+pathwayID):
            #file exists
            print(settings.MEDIA_ROOT+'/KEGG/'+pathwayID)
        else:
            url = 'http://rest.kegg.jp/get/'+pathwayID+'/image'
            response = requests.get(url)
            pathwayImage = response.content
            with open(settings.MEDIA_ROOT+'/KEGG/'+pathwayID, 'wb') as f:
                for chunk in pathwayImage:
                    f.write(chunk)

    return render(request, 'tracker/PhenoType_KEGG.html', {'gene':gid, 'pathwayHtml': pathwayHtml, 'htmlList': pathwayHtmlList, 'imagename': pathwayID})


@login_required(login_url='/saml/')
def phenotype_hpo(request, acc):
    tid = str(functions.getTermID('acc', acc))
    details = functions.getTermDetails(tid)

    disease = functions.getDiseaseByTermID(tid)
    dblist =[]
    for d in disease:
        dblist.append({'dbname': d['db_name'].encode('utf8'), 'id': str(d['disease_id'])})
    logging(request, 'access')
    return render(request, 'tracker/PhenoType.html', {'details':details, 'disease': disease, 'acc':acc, 'dblist': dblist})


@login_required(login_url='/saml/')
def phenotype_graph(request, acc):
    tid = str(functions.getTermID('acc', acc))
    details = functions.getTermDetails(tid)
    relations = functions.getTermRelations(tid)
    logging(request, 'access')
    return render(request, 'tracker/PhenoType_Graph.html', {'details':details, 'relations': json.dumps(relations), 'acc':acc})


@login_required(login_url='/saml/')
def genelists(request):
    c_genelists = GeneLists.objects.select_related('category').order_by('category', 'name')
    newlist = []
    for obj in c_genelists:
        newlist.append({'name':obj.name, 'category':obj.category.name, 'list':obj.list, 'desc':obj.desc, 'id':str(obj.id)})
    logging(request, 'access')
    return render(request, 'tracker/GeneLists.html', {'genelists': json.dumps(newlist)})


@login_required(login_url='/saml/')
def edit_genelist(request):
    if request.method == 'POST':
        form = GeneListsForm(request.POST)
        if request.POST['action'] == 'delete':
            gene = GeneLists.objects.get(id=request.POST['gid'])
            gene.delete()
        elif request.POST['action'] == 'edit':
            gid = request.POST['gid']
            gene = GeneLists.objects.get(id=gid)
            gene.name = request.POST['name']
            gene.list = request.POST['list'].replace('\r\n', ' ')
            gene.desc = request.POST['desc']
            gene.save()
        else:       # add
            form.save()
        return HttpResponseRedirect('/GeneLists/')
    else:
        if not request.META['QUERY_STRING']:
            form = GeneListsForm()
            action = 'add'
            gid=0
        else:
            gid = request.GET.get('gid')
            c_genelist = GeneLists.objects.get(id=gid)
            form = GeneListsForm(instance=c_genelist)
            action = 'edit'
    logging(request, 'access')
    return render(request, 'tracker/EditGeneList.html', {'form': form, 'action':action, 'gid':gid})


@login_required(login_url='/saml/')
def add_patient_order_genelist(request, oid):
    if request.method == 'POST':
        form = OrderGeneListForm(request.POST)
        if request.POST['action'] == 'delete':
            c_genelist = OrderGeneList.objects.get(order_id=request.POST['order'],genelist=request.POST['genelist'])
            c_genelist.delete()
            print 'deleted'
        else:
            print('saved')
            if form.is_valid():
                    form.save()
            else:
                message = form.errors
                messages.error(request, message)
                print ('form error', form.errors.__str__())

        return HttpResponseRedirect('/PatientOrderGeneList/' + oid + '/')
    else:
        form = OrderGeneListForm(initial={'order': oid})
        order = Orders.objects.get(id=oid)
        try:
            genelist = OrderGeneList.objects.select_related('genelist').filter(order_id=oid)
        except OrderGeneList.DoesNotExist:
            print (genelist)
    logging(request, 'access')
    return render(request, 'tracker/PatientOrderGeneList.html', {'genelists': genelist,'form': form, 'order':order })


@login_required(login_url='/saml/')
def edit_patient_order_phenopype(request, pid):
    if request.method == 'POST':
        form = PatientOrderPhenoTypeForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/order/'+str(form.cleaned_data['order'].id) + '/')

    else:
        c_phenotype = PatientOrderPhenoType.objects.get(id=pid)
        form = PatientOrderPhenoTypeForm(instance=c_phenotype)
    logging(request, 'access')
    return render(request, 'tracker/PatientOrderPhenoType.html', {'form': form , 'action': 'edit' })
















#
#
# #################################
# @login_required(login_url='/saml/')
# def phenotypes(request):
#     c_phenotypes = PhenoTypes.objects.all().order_by('name')
#     jsonstring_phenotypes = serializers.serialize('json', c_phenotypes)
#     return render(request, 'tracker/PhenoTypes.html', {'phenotypes': jsonstring_phenotypes})

#
# @login_required(login_url='/saml/')
# def add_phenotype(request):
#     if request.method == 'POST':
#         form = PhenoTypesForm(request.POST, request.FILES)
#         if form.is_valid():
#             print(form, form.cleaned_data, form.cleaned_data['image'])
#             form.save()
#             return HttpResponseRedirect('/Phenotypes/')
#         else:
#             action = 'edit'
#     else:
#         if not request.META['QUERY_STRING']:
#             form = PhenoTypesForm()
#             action = 'add'
#         else:
#             pid = request.GET.get('pid')
#             c_phenotype = PhenoTypes.objects.get(id=pid)
#             form = PhenoTypesForm(instance=c_phenotype)
#             action = 'edit'
#
#     return render(request, 'tracker/PhenoType.html', {'form': form, 'action':action })
