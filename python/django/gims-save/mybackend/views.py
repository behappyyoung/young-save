from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django import template
from django.conf import settings
from .models import MiscMessage,  PhenoTypeLists, PhenoTypeCategory, PhenoTypeListsTypes, GCloudFiles
from .forms import ManagerMessageForm
from logger.models import logging, OrderHistory, PatientHistory, log_history, SampleHistory
from tracker.models import Notes, Family, OrderGroups, PatientFiles, SampleFiles, Samples, Patients, SampleOrderRel
from users.models import UserMessage
from workflows.models import Workflows
from django.contrib import messages
import functions
from django.core import serializers
import sys, json, os
from datetime import datetime
from django.contrib.auth.decorators import login_required
import urllib2
from httplib import BadStatusLine

register = template.Library()
if int(sys.version[4:6]) >=9 :  # for python 2.7.9 above..
    newversion = True
    import ssl
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
else:
    newversion = False

if settings.LOCAL:                  # for python 2.7.9 above..
    import ssl
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE


# settings value
@register.simple_tag
def settings_value(name):
    return getattr(settings, name, "")


@login_required(login_url='/saml/')
def manager_message(request):
    if 'Manager' not in request.session.get('role'):
        logging(request, 'UnAuthorized')
        message = " You do not have permission to load  %s" % request.path_info
        messages.error(request, message)
        return HttpResponseRedirect('/')
    if request.method == 'POST':
        form = ManagerMessageForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/announce/')
    else:
        if not request.META['QUERY_STRING']:
            announce = MiscMessage.objects.last()
        else:
            mid = request.META['QUERY_STRING']
            announce = MiscMessage.objects.filter(id=mid)
        form = ManagerMessageForm(instance=announce)

    return render(request, 'misc/announcement.html', {'title': 'Edit Announcement', 'form':form})


def get_termlist(request):
    if request.method != 'POST':
        re = functions.getTerms()
    else:
        re = functions.getTerms(request.POST.get('str'))
    print(request.method, request.POST, re)
    return HttpResponse(json.dumps(re))


@login_required(login_url='/saml/')
def get_term_details(request, tid):
    definition = functions.getTermDetails(tid)
    disease = functions.getDiseaseByTermID(tid)
    print(type(definition), type(disease))

    try:
        term_definition = definition[0]['term_definition']
    except:
        term_definition = ''
    try:
        synonyms = definition[0]['term_synonym']
    except:
        synonyms = []
    re = {'definition' : term_definition, 'sysnonyms' : synonyms, 'disease' : disease}

    # print (re, type(re))
    return HttpResponse(json.dumps(re))


@login_required(login_url='/saml/')
def get_term_details_byacc(request, acc):
    tid = functions.getTermID('acc', acc)
    re = functions.getTermDetails(str(tid))
    print(re)
    return HttpResponse(json.dumps(re))


@login_required(login_url='/saml/')
def get_diseaselist(request):
    if request.method != 'POST':
        re = functions.getDiseases()
    else:
        re = functions.getDiseases(request.POST.get('str'))
    print(request.method, request.POST)
    return HttpResponse(json.dumps(re))


@login_required(login_url='/saml/')
def getterms_by_disease(request, did):
    re = functions.getTermsByDisease(did)
    return HttpResponse(json.dumps(re))


@login_required(login_url='/saml/')
def get_hpo_by_exid(request, exid):
    re = functions.getTermsByExternalID(exid)
    return HttpResponse(json.dumps(re))


@login_required(login_url='/saml/')
def getOminGenes(request):
    if request.method != 'POST':
        re = []
    else:
        str = request.POST.get('str')
        if str is None:
            re = []
        else:
            re = functions.getOmimGenes(str)
    return HttpResponse(json.dumps(re))


# save pedigree file
def save_pedigree(request):
    re = []
    if request.method != 'POST':
        re = []
    else:
        myFile = request.FILES['files']
        pid = request.POST.get('pid')
        id = request.POST.get('id')
        f_name = 'Pedigree' + myFile._name[myFile._name.find('.'):]
        path = functions.handle_uploaded_file(myFile, 'Patient', pid, f_name, settings.PATIENT_BUCKET_ROOT)
        url = settings.GCLOUD_URL_ROOT + path
        try:
            pedigree = PatientFiles.objects.get(patient_id=id, type='Pedigree')
            pedigree.file_title = 'Pedigree'
            pedigree.file_name=f_name
            pedigree.file_path = path
            pedigree.url = url
            pedigree.by = request.user
            pedigree.save()
        except PatientFiles.DoesNotExist:
            pedigree = PatientFiles(patient_id=id, file_name=f_name, url=url, file_path=path, type='Pedigree', by=request.user)
            pedigree.file_title = 'Pedigree'
            pedigree.save()
        log_history(request, 'patient', id, '', 'upload new pedigree')
    return HttpResponse(json.dumps(re))


def get_log(request, what):
    if 'username' in request.session:
        print request.session.get('username'), request.session.get('role')
        if what == 'order':

            if 'oid' in request.POST:
                oid = request.POST['oid']
                log = OrderHistory.objects.using('logs').filter(order_id=oid).order_by('-update_time')
            else:
                log = OrderHistory.objects.using('logs').all().order_by('-update_time')

        if what == 'patient':

            if 'pid' in request.POST:
                pid = request.POST['pid']
                log = PatientHistory.objects.using('logs').filter(patient_id=pid).order_by('-update_time')
            else:
                log =  PatientHistory.objects.using('logs').filter().order_by('-update_time')

        if what == 'sample':

            if 'sid' in request.POST:
                sid = request.POST['sid']
                log = SampleHistory.objects.using('logs').filter(sample_id=sid).order_by('-update_time')
            else:
                log = SampleHistory.objects.using('logs').all().order_by('-update_time')

        json_log = serializers.serialize('json', log)
        return HttpResponse(json_log)
    else:
        return HttpResponseRedirect('/saml/?slo')


def get_notes(request):
    if 'username' in request.session:
        print request.session.get('username'), request.session.get('role')

        try:
            if 'pid' in request.POST:
                pid = request.POST['pid']
                notes = Notes.objects.filter(patient_id=pid).select_related('category').order_by('-update_time', 'order_id')
            elif 'oid' in request.POST:
                oid = request.POST['oid']
                notes = Notes.objects.filter(order_id=oid).select_related('category').order_by('-update_time')
            elif 'nid' in request.POST:
                nid = request.GET.get('nid')
                notes =Notes.objects.filter(id=nid).values()
                return HttpResponse(notes)
            else:
                notes = Notes.objects.all()

            if len(notes) >0:
                list = []
                for row in notes:
                    recipients = row.recipients and ', '.join(map(lambda rec: functions.getUserInfo(rec, 'username'), row.recipients.split(',')))
                    list.append({'id': row.id, 'update_time': row.update_time, 'category': row.category.category_name,
                                 'writer': row.writer and row.writer.username,
                                 'recipients': recipients, 'order_name': row.order and row.order.order_name, 'note': row.note})
            else:
                list = [{'id': ' --', 'update_time': ' -- ', 'category': ' -- ', 'note': 'no note', 'order_name': '--'}]
        except:
            list = [{'id':' --', 'update_time': ' -- ', 'category': ' -- ', 'note': 'no note', 'order_name': '--'}]
        json_notes = json.dumps(list)
        return HttpResponse(json_notes)
    else:
        return HttpResponseRedirect('/saml/?slo')


def get_note(request, nid):
    notes = Notes.objects.get(id=nid)
    if str(request.user.id) in notes.recipients.split(',') :
        usermessage = UserMessage.objects.get(related_note_id=nid, user_id=request.user.id)
        usermessage.read = True
        usermessage.save()
    return HttpResponse(json.dumps({'id': notes.id, 'update_time': notes.update_time, 'category': notes.category.category_name,
                                 'writer': notes.writer and notes.writer.username,
                                 'recipients': notes.recipients, 'order_name': notes.order and notes.order.order_name, 'note': notes.note}))


def save_file(request):
    re = []
    if request.method != 'POST':
        re = []
    else:
        myFile = request.FILES['files']
        id = request.POST.get('id')
        id_type = request.POST.get('type')
        file_type = request.POST.get('file_type')
        try:
            path = functions.handle_uploaded_file(myFile, id_type, id, myFile.__name, settings.BUCKET_ROOT)
            url = settings.GCLOUD_URL_ROOT + path
            file_db = GCloudFiles(name=myFile._name, obj_type=id_type, obj_id=id, file_type=file_type, url=url, upload_by=request.user)
            re = file_db.save()
        except:
            re = 'error'
    return HttpResponse(json.dumps(re))


def mybackend_magic(request, func):
    message =''
    if request.method != 'POST':
        message = 'Only POST requests are accepted'
    else:
        if func == 'delete_member':
            fid = request.POST.get('fid')
            pid = request.POST.get('pid')
            if fid and pid:
                try:
                    family = Family.objects.get(family_id=fid, patient_id=pid)
                    result = family.delete()
                    message = 'Done'
                    patient = Patients.objects.get(id=pid)
                    # pname = functions.getPatientInfo(pid, ['first_name', 'last_name'])
                    log_history(request, 'patient', pid, patient.first_name + '  ' + patient.last_name,
                                ' deleted from Family Group : ' + fid )
                except:
                    message  = 'Error'
            else:
                message = 'input error'
        elif func == 'delete_order':
            gid = request.POST.get('gid')
            oid = request.POST.get('oid')
            if gid and oid:
                try:
                    group = OrderGroups.objects.get(group_id=gid, order_id=oid)
                    result = group.delete()
                    message = 'Done'
                except:
                    message  = 'Error'
            else:
                message = 'input error'
        elif func == 'delete_patient_file':
            fid = request.POST.get('fid')
            if fid:
                try:
                    pfile = PatientFiles.objects.get(id=fid)
                    result = pfile.delete()
                    message = 'Done'
                except:
                    message = 'Error'
            else:
                message = 'input error'
    return HttpResponse(message)


def testing_index(request):
    if '127.0.0.1' in request.environ['REMOTE_ADDR'] and 's0199669' in request.environ['USER'] :
        if 'request' in request.META['QUERY_STRING']:
            return HttpResponse(str(request.__dict__))
        import os
        os.chdir('/Users/s0199669/github/PythonSampleCodes/SampleCodes')
        re = functions.executeCommand('python readFile.py row_text.txt')
        print (re, type(re))
        return HttpResponse(str(request.__dict__) + '========' + re.replace('\n','<br />'))
    else:
        return HttpResponseRedirect('/')


'''
    loom
'''


@login_required(login_url='/saml/')
def get_workflows(request):
    # url =
    file = open( settings.BASE_DIR+'/files/imported-workflows.json', 'r' )
    workflow_json = file.read()
    workflows = json.loads(workflow_json)
    for w in workflows:
        print type(w), w.get('inputs')
        print w.get('id'), w.get('name')
        exists = Workflows.objects.filter(workflow_id=w.get('id')).values()
        if len(exists) > 0:
            pass
        else:
            wf = Workflows(workflow_id=w.get('id'), name=w.get('name'), inputs=w.get('inputs'), fixed_inputs=w.get('fixed_inputs'))
            wf.save()

    return HttpResponse(workflow_json)
'''
    Cartagenia
'''


def sso_cartagenia(request):
    url = functions.sso_catargenia()
    # import webbrowser
    # webbrowser.open(url)
    return HttpResponseRedirect(url)


def run_cartagenia(request, group):
    groups = OrderGroups.objects.filter(group_id=group).select_related('order')
    type = None
    patients =[]
    for g in groups:
        if type is None:
            type = g.order.type.type
        else:
            if type != g.order.type.type:
                message = 'order types are not match ( %s: %s )'%(type, g.order.type.type)
                return HttpResponse(json.dumps({'Error': True, 'message': message}))
        c_so = SampleOrderRel.objects.get(order_id=g.order_id, relation_id=1)
        patients.append({'relation': g.relation.rel_name, 'p_id': c_so.patient_id, 'o_id': g.order.id})

    if 'TRIO' in type:
        run_result = functions.register_trio_assay(patients, 'TRIO')
    else:
        run_result = functions.register_single_assay(patients[0].get('p_id'), patients[0].get('o_id'), 'Single')

    re = json.loads(run_result)
    error = True
    if re.get('status_code') == 200:
        error = False
        OrderGroups.objects.filter(group_id=group).update(run_result=re.get('assay_id'))

    return HttpResponse(json.dumps({'Error': error, 'Message': re.get('status_message')}))


def checkstatus_cartagenia(request, mrn):
    re =  json.loads(functions.cartagenia_checkstatus(mrn))
    if re.get('status_code') == 200:
        return HttpResponse(json.dumps({'Error': False, 'Message': re.get('status_message'), 'Analyses': re.get('analyses')}))
    else:
        return HttpResponse(json.dumps({'Error': True, 'Message': re.get('status_message')}))


def getreport_cartagenia(request):
    if request.method != 'POST':
        message = ' Request Error : Only POST requests are accepted'
        return HttpResponse(json.dumps({'Error': True, 'Message': message}),
                            content_type="application/json")
    else:
        sid = request.POST.get('sid')
        pid = request.POST.get('pid')
        if sid is None or pid is None:
            return HttpResponse(json.dumps({'Error': True, 'Message': 'Data ( sample id/patient id ) is Missing'}),
                                content_type="application/json")

    so = SampleOrderRel.objects.get(sample_id=sid, patient_id=pid, relation_id=1)
    ref = so.sample.asn + '_' + so.patient.mrn
    re =  json.loads(functions.cartagenia_getreport(ref))

    if re.get('status_code') == 200:
        reports = re.get('reports')
        functions.export_epic(so.id, reports[0].get('encoded_content'))

        return HttpResponse(json.dumps({'Error': False, 'Message': re.get('status_message')}))
    else:
        return HttpResponse(json.dumps({'Error': True, 'Message': re.get('status_message')}))



'''
    Personalis API
'''


def moveFile(src, file_path, asn):

    cbs = functions.get_bucket(settings.BUCKET_PROJECT, settings.THIRD_BUCKET_ROOT)  # source cloud bucket
    cbd = functions.get_bucket(settings.BUCKET_PROJECT, settings.SAMPLE_BUCKET_ROOT)  # destination cloud bucket

    dest_dir = asn + '/personalis-' + datetime.now().strftime('%Y%m%d') + '/import-files/'
    src_cloud_path = src + '/' + file_path
    return src_cloud_path # return without moving file for now TEMP
    dest_cloud_path = dest_dir + file_path

    if cbs.fileExists(src_cloud_path):
            re = cbs.copyFileFromBucketToBucket(src_cloud_path, cbd, dest_cloud_path, )
    else:
            message = 'Cannot access ' + src_cloud_path + ' file '
            return HttpResponse(json.dumps({'status_code': 400, 'status_message': 'Data Error : ' + message}),
                                content_type="application/json")

    return dest_cloud_path


def saveSampleFiles(asn, cloud_path, file_name, file_type, loom_id):
    try:
            sample = Samples.objects.get(asn=asn)

            try:
                sample_file = SampleFiles.objects.get(sample_id=sample.id, file_type=file_type)
                sample_file.file_location = cloud_path
                sample_file.file_name = file_name
                sample_file.loom_id = loom_id
                sample_file.save()
            except SampleFiles.DoesNotExist:
                s = SampleFiles(file_location=cloud_path, file_type=file_type, sample_id=sample.id, file_name=file_name, loom_id=loom_id)
                s.save()

    except Samples.DoesNotExist:
            message = 'Cannot access sample : ' + asn
            return HttpResponse(json.dumps({'status_code': 400, 'status_message': 'Data Error : ' + message}),
                                content_type="application/json")

    return 'Saved'


def getSampleFiles(request):
    if request.method != 'POST':
        message = ' Request Error : Only POST requests are accepted'
        return HttpResponse(json.dumps({'status_code': 406, 'status_message': message}), content_type="application/json")
    else:
        input_json = json.loads(request.body)
        sid = input_json.get('sid')
    re = []
    try:
        samples = SampleFiles.objects.filter(sample_id=sid)
        for s in samples:
            re.append({'sample_id': s.id, 'file_type': s.file_type, 'file_location': s.file_location, 'loom_id': s.loom_id, 'file_name': s.file_name})
    except SampleFiles.DoesNotExist:
        message = 'There is no Files register for this sample'
        return HttpResponse(json.dumps({'status_code': 400, 'status_message': message}))

    return HttpResponse(json.dumps({'status_code': 200, 'file_data': json.dumps(re), 'status_message': 'Done'}))


def get_sampleorderlist(request):
    if request.method != 'POST':
        message = ' Request Error : Only POST requests are accepted'
        return HttpResponse(json.dumps({'status_code': 406, 'status_message': message}), content_type="application/json")
    else:
        input_json = json.loads(request.body)
        try:
            sid = input_json.get('sid')
            oid = input_json.get('oid')
            if sid is not None:
                query = 'sample_id=%s'%sid
            elif oid is not None:
                query = 'order_id=%s'%oid
            else:
                query = input_json.get('query')
            so_list = functions.getSO_List(query, True)
        except Exception as e:
            message = 'Cannot access sample order list '
            return HttpResponse(json.dumps({'status_code': 400, 'status_message': 'Data Error : ' + message}),
                                content_type="application/json")
    return HttpResponse(json.dumps({'status_code': 200, 'return_data': json.dumps(so_list), 'status_message': 'Done'}))


def personalis(request):
    if request.method != 'POST':
        message = ' Request Error : Only POST requests are accepted'
        return HttpResponse(json.dumps({'status_code': 406, 'status_message': message}), content_type="application/json")
    else:
        body = request.body

    try:
        input_json = json.loads(body)
        personalis = input_json.get('personalis')
    except ValueError:
        return HttpResponse(json.dumps({'status_code': 400, 'status_message': 'Input Error : Wrong Json format'}), content_type="application/json")

    errors = []
    for p in personalis:
        sequencing_run_id = p.get('sequencing-run-id')
        if not sequencing_run_id:
            errors.append('Missing sequencing_run_id')
        sample_accession_id = p.get('sample-accession-id')
        if not sample_accession_id:
            errors.append('Missing sample-accession-id')
        vcf_path = p.get('vcf-path')
        if not vcf_path:
            errors.append('Missing vcf-path')
        bam_path = p.get('bam-path')
        if not bam_path:
            errors.append('Missing bam-path')
        bai_path = p.get('bai-path')
        if not bai_path:
            errors.append('Missing bai-path')
        qd_path = p.get('qcreports-path')
        if not qd_path:
            errors.append('Missing qcreports-path')
        checksum_path = p.get('checksum-path')
        if not checksum_path:
            errors.append('Missing checksum-path')
        fastq1_path = p.get('fastq1-path')
        if not fastq1_path:
            errors.append('Missing fastq1-path')
        fastq2_path = p.get('fastq2-path')
        if not fastq2_path:
            errors.append('Missing fastq2-path')

        if errors:
            return HttpResponse(json.dumps({'status_code': 400, 'status_message': 'Data Error : ' + ', '.join(errors)}), content_type="application/json")

        cbd = functions.get_bucket(settings.SAMPLE_BUCKET_ROOT, settings.BUCKET_PROJECT)         # destination cloud bucket

        src_dir = sequencing_run_id + '/' + sample_accession_id

        dest_path = moveFile(src_dir, vcf_path, sample_accession_id)
        slash_p = vcf_path.find('/')
        file_name = vcf_path[slash_p:]
        re = saveSampleFiles(sample_accession_id, dest_path, file_name, 'vcf', 'None')

        dest_path = moveFile(src_dir, fastq1_path, sample_accession_id)
        slash_p = fastq1_path.find('/')
        file_name = fastq1_path[slash_p:]

        checksum = str(cbd.getMD5Checksum(dest_path))
        gcloud_url = "gs://" + settings.SAMPLE_BUCKET_ROOT + '/' + dest_path
        re = functions.loom_register_samplefile(file_name, gcloud_url, checksum)
        loom_id = json.loads(re).get('uuid')
        re = saveSampleFiles(sample_accession_id, dest_path, file_name, 'fastq1', loom_id)

        slash_p = fastq2_path.find('/')
        file_name = fastq2_path[slash_p:]

        checksum = str(cbd.getMD5Checksum(dest_path))
        gcloud_url = "gs://" + settings.SAMPLE_BUCKET_ROOT + '/' + dest_path
        re = functions.loom_register_samplefile(file_name, gcloud_url, checksum)
        loom_id = json.loads(re).get('uuid')
        re = saveSampleFiles(sample_accession_id, dest_path, file_name, 'fastq2', loom_id)

        # move bam file
        dest_path = moveFile(src_dir, bam_path, sample_accession_id)
        slash_p = bam_path.find('/')
        file_name = bam_path[slash_p:]
        re = saveSampleFiles(sample_accession_id, dest_path, file_name, 'bam', 'None')

        # move bai file
        dest_path = moveFile(src_dir, bai_path, sample_accession_id)
        slash_p = bai_path.find('/')
        file_name = bai_path[slash_p:]
        re = saveSampleFiles(sample_accession_id, dest_path, file_name, 'bai', 'None')


    # print body, type(body), errors
    if len(errors) == 0:
        message = '{"status_code":200, "status_message": "Done"}'
    else:
        error_message = ''
        message = '{"status_code":400,, "status_message": "Error", "error_message" : "%s" }'%', '.join(errors)

    return HttpResponse(message, content_type="application/json")