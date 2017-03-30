from bs4 import BeautifulSoup
import requests, json
from .models import CustomSql
from gims import settings
from users.models import UserProfile
from tracker.models import Patients, Notes, Orders, SampleOrderRel, SampleFiles, SampleContainer
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from logger.models import CatargeniaLog
from lib.gcloud import CgsBucket
from lib.cartagenia import BenchLabNgs, AssayRegistrationData, Patient, Check, Upload, ListAnalysis, ReportExport
import urllib2
from epic.models import outgoing_message

import os, hashlib


def date_handler(obj):
    if hasattr(obj, 'isoformat'):
        return obj.isoformat()
    else:
        raise TypeError


def doSQL(csql):
    """
        :param csql: sql statement
        :return: list of result of sql

    """
    myc = CustomSql()
    return myc.custom_sql(csql)


def getUserInfo(uid, what):
    userprofile = UserProfile.objects.get(user_id=uid)
    return getattr(userprofile, what)


def getOrderDetails(date_range_input):
    if isinstance(date_range_input, list):
        date_range = date_range_input
        t = datetime.strptime(date_range[1], '%Y-%m-%d') + timedelta(days=1)
        date_range[1] = t.strftime('%Y-%m-%d')
    else:
        now = datetime.now()
        today_in = now + timedelta(days=1)
        if date_range_input == 30:
            pre_ago = now - relativedelta(months=1)
        elif date_range_input == 7:
            pre_ago = now - timedelta(days=7)
        else:
            pre_ago = now - relativedelta(months=1)
        date_range = [pre_ago.strftime('%Y-%m-%d'), today_in.strftime('%Y-%m-%d')]
    # print date_range
    orders = Orders.objects.filter(order_date__range=[date_range[0], date_range[1]]).prefetch_related('status', 'type')
    return orders


def getSO_List(query=None, incomplete_only=False, forOrder=False):
    if query is None or query == '':
        so = SampleOrderRel.objects.all()
    else:
        qs = query.split('=')
        query_dict = {qs[0]: qs[1]}
        so = SampleOrderRel.objects.filter(**query_dict)
    so_lists = []
    for s in so:
        if incomplete_only and 'COMPLETED' == s.order.status.status:
            continue
        dlist = dict()
        dlist['sample_id'] = s.sample_id
        dlist['asn'] = str(s.sample.asn)
        dlist['pname'] = urllib2.quote(str(s.patient.name()))
        dlist['order_type'] = urllib2.quote(str(s.order.type.type_name))
        dlist['order_id'] = str(s.order_id)
        dlist['sample_type'] = str(s.sample.type)
        dlist['sample_status'] = str(s.sample.status.status_name)
        dlist['order_status'] = str(s.order.status.status_name)
        dlist['due_date'] = s.order.due_date
        dlist['flag'] = s.order.flag
        dlist['physician'] = str(s.order.physician_firstname + ' ' + s.order.physician_lastname)
        dlist['owner'] = str(s.order.owner.username if s.order.owner else '')
        dlist['pid'] = s.patient.pid
        dlist['mrn'] = s.patient.mrn

        so_lists.append(dlist)

    return so_lists


def getSampleContainer_list():
    list = {}
    containers = SampleContainer.objects.all()
    for c in containers:
        l = list.get(c.sample_id)
        if l:
            l.append(c.cid)
        else:
            l = [c.cid]
        list[c.sample_id] = l

    return list


def getProcessingTime(date_range_input=''):
    if isinstance(date_range_input, list):
        date_range_text = 'and prev_time > "%s" and update_time <= "%s"' % (date_range_input[0], date_range_input[1])
    else:
        date_range_text =''

    sql = 'SELECT "APPROVED" as name, prev_status,update_status, COALESCE(sum(processing_day), 0) as days, COALESCE(sum(processing_time), 0) as times, count(id) as count '  \
          'FROM lims_log_db.logger_orderprocessinglog WHERE prev_status="CREATED" and update_status="APPROVED" ' + date_range_text + \
          'union SELECT "REVIEW" as name, prev_status,update_status, COALESCE(sum(processing_day), 0), COALESCE(sum(processing_time), 0), count(id) as count ' \
          'FROM lims_log_db.logger_orderprocessinglog WHERE prev_status="APPROVED" and update_status="PRE ANALYSIS REVIEW" ' + date_range_text + \
          'union SELECT "SENDOUT" as name, prev_status,update_status, COALESCE(sum(processing_day), 0), COALESCE(sum(processing_time), 0), count(id) as count ' \
          'FROM lims_log_db.logger_orderprocessinglog WHERE prev_status="PRE ANALYSIS REVIEW" and update_status="SENDOUT" ' + date_range_text + \
          'union  SELECT "LAB" as name,  COALESCE(prev_status, "SENDOUT"),COALESCE(update_status, "QC READY"), COALESCE(sum(processing_day), 0), COALESCE(sum(processing_time), 0), count(id) as count  ' \
          'FROM lims_log_db.logger_orderprocessinglog WHERE prev_status="SENDOUT" and update_status="QC READY"' + date_range_text

    result = doSQL(sql)
    pTimeObj={}
    for r in result:
        pTimeObj[r['name']] = r

    # pTimeObj = {'APPROVED': r[0], 'REVIEW':r[1], 'SENDOUT': r[2], 'LAB':r[3]}
    return pTimeObj


def getAverageProcessingTime(date_range_input=None):
    now = datetime.now()
    today_in = now + timedelta(days=1)
    if not date_range_input:
        date_range = ['2016-01-01', today_in.strftime('%Y-%m-%d')]
    elif isinstance(date_range_input, list):
        date_range = date_range_input
        t = datetime.strptime(date_range[1], '%Y-%m-%d') + timedelta(days=1)
        date_range[1] = t.strftime('%Y-%m-%d')
    else:
        if date_range_input == 30:
            pre_ago = now - relativedelta(months=1)
        elif date_range_input == 7:
            pre_ago = now - timedelta(days=7)
        else:
            pre_ago = now - relativedelta(months=1)
        date_range = [pre_ago.strftime('%Y-%m-%d'), today_in.strftime('%Y-%m-%d')]

    pObj = getProcessingTime(date_range)
    for p in pObj:
        c = pObj[p].get('count')
        if c != 0:
            a_time = pObj[p].get('times') / c
        else:
            a_time = 0
        pObj[p]['a_time'] = int(a_time)
        pObj[p]['a_time_str'] = str(timedelta(seconds=int(a_time)))

    return pObj


def getAverageProcessingTime_org(date_range_input=None):
    now = datetime.now()
    today_in = now + timedelta(days=1)
    if not date_range_input:
        date_range = ['2016-01-01', today_in.strftime('%Y-%m-%d')]
    elif isinstance(date_range_input, list):
        date_range = date_range_input
        t = datetime.strptime(date_range[1], '%Y-%m-%d') + timedelta(days=1)
        date_range[1] = t.strftime('%Y-%m-%d')
    else:
        if date_range_input == 30:
            pre_ago = now - relativedelta(months=1)
        elif date_range_input == 7:
            pre_ago = now - timedelta(days=7)
        else:
            pre_ago = now - relativedelta(months=1)
        date_range = [pre_ago.strftime('%Y-%m-%d'), today_in.strftime('%Y-%m-%d')]

    pObj = getProcessingTime(date_range)
    pick_day = True
    for p in pObj:
        c = pObj[p].get('count')
        if c != 0:
            if pick_day:
                pObj[p]['a_day'] = pObj[p].get('days') / c
                if pObj[p]['a_day'] == 0:
                    pick_day = False
            pObj[p]['a_time'] = pObj[p].get('times') / c
        else:
            pObj[p]['a_day'] = 0
            pObj[p]['a_time'] = 0

    if pick_day:
        pObj['type'] = 'days'
    else:
        pObj['type'] = 'times'
    return pObj


def getPatientInfo(pid, what):
    try:
        patient = Patients.objects.get(pid=pid)
        if isinstance(what, list):
            result = {}
            for i in what:
                result[i] = getattr(patient, i)
        else:
            result = getattr(patient, what)
        return result
    except Patients.DoesNotExist:
        return {}


def getPulseDiv():

    url = 'https://stanfordhealthcare.org'

    # using requests
    try:
        response = requests.get(url)
        message = response.content
        soup = BeautifulSoup(message, 'html.parser')
        mydiv = str(soup.find("div", class_="stanford-now-pulse"))
        file_ = open('mybackend/pulseDiv', 'w')
        file_.write(mydiv)
        file_.close()
    except requests.exceptions.RequestException as e:  # This is the correct syntax
        print (e)
        message = "could not fetch %s" % url
        print (message)
        file_ = open('mybackend/pulseDiv', 'r')
        mydiv = file_.read()
        file_.close()
    mydiv = mydiv.replace('-4', '-12').replace('-8', '-12').replace('/content/', url+'/content/')\
        .replace('h2>', 'h5>').replace('container', 'container-fluid').replace('\n', '')
    #parsed_mydiv = BeautifulSoup(mydiv,  'html.parser')

    return mydiv


def getMednewsDiv():

    url = 'http://med.stanford.edu'

    # using requests
    try:
        response = requests.get(url)
        message = response.content
        soup = BeautifulSoup(message, 'html.parser')
        mydiv = str(soup.find("div", class_="panel-builder-100-col"))
        file_ = open('mybackend/medDiv', 'w')
        file_.write(mydiv)
        file_.close()
    except requests.exceptions.RequestException as e:  # This is the correct syntax
        print (e)
        message = "could not fetch %s" % url
        print (message)
        file_ = open('mybackend/medDiv', 'r')
        mydiv = file_.read()
        file_.close()
    mydiv = mydiv.replace('<h2', '<h4').replace('h2>', 'h4>').replace('<h3', '<h5').replace('h3>', 'h5>') \
        .replace('/news/', url+'/news/').replace('container', 'container-fluid').replace('\n', '')

    return mydiv


def getOmimGenesByDisease(disease):
    mimstr_list = []
    count=1
    mimstr = ''
    for d in disease:
        if d['db_name'] == 'OMIM':
            mimstr += '&mimNumber='+ d['disease_id']
            count += 1
            if count == 20:
                mimstr_list.append(mimstr)
                count = 1
                mimstr = ''
    if(mimstr != ''):
        mimstr_list.append(mimstr)
    if len(mimstr_list) > 0 :

        try:
            message = []
            for mimstr in mimstr_list:
                url = (
                'http://api.omim.org/api/entry?apiKey=%s&include=geneMap&format=json%s' % (settings.OMIM_apiKey, mimstr))
                response = requests.get(url)
                jdata =  json.loads(response.content)
                entryList = jdata['omim']['entryList']
                for entry in entryList:
                    print  entry
                    if 'phenotypeMapList' in entry['entry']:
                        message.append({'id': str(entry['entry']['mimNumber']),
                                        'title': str(entry['entry']['titles']['preferredTitle'].encode('utf8')),
                                        'symbols': entry['entry']['phenotypeMapList'][0]['phenotypeMap']['geneSymbols'].encode('utf8')})
        #except requests.exceptions.RequestException as e:
        except Exception as e:
            print (e)
            message = "could not fetch %s" % url
            print (message)

    else:
        message =[]
    return message


def getOmimData(mimNumber):
    try:
            # message = []
            url = (
                'http://api.omim.org/api/entry?apiKey=%s&include=all&format=json&mimNumber=%s' % (settings.OMIM_apiKey, mimNumber))
            response = requests.get(url)
            jdata =  json.loads(response.content)
            return  jdata['omim']['entryList'][0]
    except requests.exceptions.RequestException as e:
            print (e)
            message = "could not fetch %s" % url
            print ('error : %s' % message)
    return message


def getOmimGenes(mimstr):
    try:
            message = []
            url = (
                'http://api.omim.org/api/entry?apiKey=%s%s&include=geneMap&format=json' % (settings.OMIM_apiKey, mimstr))
            response = requests.get(url)
            jdata =  json.loads(response.content)
            entryList = jdata['omim']['entryList']
            for entry in entryList:
                print  entry
                if 'phenotypeMapList' in entry['entry']:
                        message.append({'id': str(entry['entry']['mimNumber']),
                                        'title': str(entry['entry']['titles']['preferredTitle'].encode('utf8')),
                                        'symbols': entry['entry']['phenotypeMapList'][0]['phenotypeMap']['geneSymbols'].encode('utf8')})
    except requests.exceptions.RequestException as e:
            print (e)
            message = "could not fetch %s" % url
            print (message)
    return message


def getTermsAll(str=None):
    myc = CustomSql()
    if not str:
        mysql = 'select * from public_db.term order by acc'
    else:
        mysql = 'select * from public_db.term where name like "%'+str+'%" order by name'
    try:
        hpo_terms = myc.custom_sql(mysql)
        return hpo_terms
    except Exception as e:  # This is the correct syntax
        print (e)
        return 'error'


def getTerms(str=None):
    myc = CustomSql()
    if not str:
        mysql = 'select id as tid, acc, name as term from public_db.term  WHERE is_obsolete =0 ' \
                'union select term_id as tid, acc, term_synonym as term from public_db.term_synonym ts, public_db.term t ' \
                'WHERE  ts.term_id=t.id and t.is_obsolete =0 '
    else:
        mysql = 'select id as tid, acc, name, name as term from public_db.term  WHERE is_obsolete =0 ' \
                'and name like  "%'+str+'%"  union select term_id as tid, acc, name,  concat(term_synonym, "(synonym)") as term from public_db.term_synonym ts' \
                ' left join public_db.term t on ts.term_id=t.id WHERE  ts.term_synonym like  "%'+str+'%" '
    try:
        hpo_terms = myc.custom_sql(mysql)
        return hpo_terms
    except Exception as e:  # This is the correct syntax
        print (e)
        return 'error'


def getTermID(by, str):
    if by == 'acc':
        mysql = 'SELECT id FROM public_db.term WHERE acc="'+str+'"'
    else:
        mysql = 'SELECT id FROM public_db.term'
    term_id = doSQL(mysql)
    print(term_id)
    return term_id[0]['id']


def getTermDetails(tid):
    mysql = 'select def.term_definition, syn.term_synonym , term.name from public_db.term as term ' \
            'left join public_db.term_definition as def on def.term_id = term.id ' \
            'left join public_db.term_synonym as syn on syn.term_id = term.id WHERE term.id = "'+tid+'" '
    terms = doSQL(mysql)
    return terms


def getTermRelations(tid):
    mysql = 'select * from ( SELECT  GROUP_CONCAT(acc,"/",  name) as children FROM public_db.term t left join  public_db.term2term tt on t.id = tt.term2_id ' \
            'WHERE tt.term1_id ="'+tid+'") children, (SELECT  GROUP_CONCAT(acc,"/",  name) as parents  FROM public_db.term t left join  public_db.term2term tt ' \
                                       'on t.id = tt.term1_id WHERE tt.term2_id ="'+tid+'" ) parents '
    term_rel = doSQL(mysql)
    return term_rel
#
# def getTermRelations(tid):
#     mysql = 'SELECT * FROM ' \
#             '( SELECT GROUP_CONCAT(term2_id) AS children FROM public_db.term2term WHERE term1_id ="'+tid+'") parent, ' \
#             '(SELECT GROUP_CONCAT(term1_id) AS parent FROM public_db.term2term WHERE term2_id="'+tid+'") children '
#     term_rel = doSQL(mysql)
#     return term_rel


def getTermsByDisease(did):
    mysql = 'SELECT t.*, t.id as tid FROM  public_db.external_object_disease d left join public_db.annotation a ' \
            'on a.external_object_disease_id = d.external_object_id left join  public_db.term t on t.id = a.term_id ' \
            'WHERE d.disease_id ="'+did+'" and t.is_obsolete =0  order by d.db_name'
    terms = doSQL(mysql)
    return terms


def getTermsByExternalID(exid):
    return ''


def getDiseases(str=None):
    myc = CustomSql()
    if not str:
        mysql = 'SELECT external_object_id as exid, disease_id as did, db_name as dbname, disease_title as name FROM public_db.external_object_disease;'
    else:
        mysql = 'SELECT external_object_id as exid, disease_id as did, db_name as dbname, disease_title as name FROM public_db.external_object_disease' \
                ' WHERE  disease_title like  "%'+str+'%" or disease_longtitle like "%'+str+'%" '
    try:
        hpo_terms = myc.custom_sql(mysql)
        print(str, mysql)
        return hpo_terms
    except Exception as e:  # This is the correct syntax
        print (e)
        return 'error'


def getDiseaseByTermID(tid):
    disease = doSQL('SELECT distinct d.* FROM  public_db.external_object_disease d '
                    'left join public_db.annotation a on a.external_object_disease_id = d.external_object_id'
                    ' WHERE  a.term_id ="%s" order by d.db_name, cast(d.disease_id as SIGNED)' % tid)
    return disease


def getFamily(pid, sub=False):
    family = doSQL('SELECT p.*, pr.relative, r.rel_name FROM lims_db.tracker_patients p  join tracker_patientrelations pr on p.pid =pr.main '
                   'join tracker_peoplerelations r on pr.relationship_id = r.id WHERE pid ="%s"' % pid)
    family_list=[]
    myinfo = {'id': pid, 'name': family[0]['first_name']+' '+family[0]['last_name'], 'sex': family[0]['sex']}
    for f in family:
        relationship = f['rel_name']
        rid = f['relative']
        if relationship =='Father':
            myinfo['father'] = rid
            if sub:  # if sub.. do not go down more
                temp = getPatientInfo(rid, ['sex', 'first_name', 'last_name'])
                tempinfo = {'id': rid, 'name': temp['first_name'] + ' ' + temp['last_name'], 'sex': temp['sex']}
                family_list.append(tempinfo)
            else:
                family_list.extend(getFamily(rid, True))
        elif relationship =='Mother':
            myinfo['mother'] = rid
            if sub:             # if sub.. do not go down more
                temp = getPatientInfo(rid, ['sex', 'first_name', 'last_name'])
                tempinfo = {'id': rid, 'name': temp['first_name']+' '+temp['last_name'], 'sex': temp['sex']}
                family_list.append(tempinfo)
            else:
                family_list.extend(getFamily(rid, True))
        elif relationship == 'Son' or relationship == 'Daughter':
            # myinfo['children'].append(rid)
            if sub:             # if sub.. do not go down more
                temp = getPatientInfo(rid, ['sex', 'first_name', 'last_name'])
                tempinfo = {'id': rid, 'name': temp['first_name']+' '+temp['last_name'], 'sex': temp['sex']}
                if f['sex'] == 'Male':
                    tempinfo['father'] = pid
                elif f['sex'] == 'Female':
                    tempinfo['mother'] = pid
                family_list.append(tempinfo)
            else:
                family_list.extend(getFamily(rid, True))

    family_list.append(myinfo)
    return family_list


def get_notes(withwhat, id):

    if withwhat == 'pid':
        notes = Notes.objects.filter(patient_id=id).select_related('category').order_by('-update_time', 'order_id')
    elif withwhat =='oid':
        notes = Notes.objects.filter(order_id=id).select_related('category').order_by('-update_time')
    else:
        notes = Notes.objects.filter(id=id).values()
        return notes
    if len(notes) > 0:
        list = []
        for row in notes:
                    recipients = row.recipients and ', '.join(map(lambda rec: getUserInfo(rec, 'username'), row.recipients.split(',')))
                    list.append({'id': row.id, 'update_time': row.update_time, 'category': row.category.category_name,
                                 'writer': row.writer and row.writer.username,
                                 'recipients': recipients, 'order_name': row.order and row.order.order_name, 'note': row.note})
    else:
                list = [{'id': ' --', 'update_time': ' -- ', 'category': ' -- ', 'note': 'no note', 'order_name': '--'}]
    return json.dumps(list)


'''

    Workflows /  Loom

'''


def loom_register_samplefile(file_name, gcloud_url, checksum):
    url = settings.LOOMURL+'files/'
    data = {
        # "source_type": "imported",
        # "type": "file",
        # "file_content": {
        #     "filename": file_name,
        #     "unnamed_file_content": {
        #         "hash_value": checksum,
        #         "hash_function": "md5"
        #     }
        # },
        # "file_location": {
        #     "url": gcloud_url,
        #     "status": "complete"
        # }
        # "uuid": "",
        "file_resource": {
            # "uuid": "",
            "file_url": gcloud_url,
            "md5": checksum,
            "upload_status": 'complete'
        },
        "file_import": 'imported',
        "type": 'file',
        "is_array": False,
        "filename": file_name,
        "md5": checksum,
        "source_type": 'imported'
    }
    json_data = json.dumps(data)
    r = requests.post(url, json=data)
    print data, json_data, r, r.content
    return r.content
# def get_labworkflows_details(request, type='', period=None):
# 	c_workflows=[]
# 	if type:
# 		if period:
# 			labworkflows = LabWorkFlows.objects.filter(type=type, created_date__range=[period.startdate, period.enddate])
# 		else:
# 			labworkflows = LabWorkFlows.objects.filter(type=type)
# 	else:
# 		if period:
# 			labworkflows = LabWorkFlows.objects.filter(created_date__range=[period.startdate, period.enddate])
# 		else:
# 			labworkflows = LabWorkFlows.objects.all()
# 	for lw in labworkflows:
# 		sample_list = lw.samples_list.split(',')
# 		for s in sample_list:
# 			o_list = s.split('-')
# 			print o_list[1]
#
# 	return c_workflows

'''

    Google storage / file upload

'''


def getHash_md5(file_location, local=False):
    if not local:
        get_from_storage(file_location, file_location)
    f = open(file_location)
    content = f.read().strip()
    hash_md5 = hashlib.md5(content).hexdigest()
    return hash_md5


def handle_uploaded_file(f, file_type, file_type_id, f_name=None, bucket_root=settings.BUCKET_ROOT):
    try:
        f_name = f_name or f._name
        file_path = file_type + '/' + file_type_id + '/' + f_name
        local_path_root = settings.GCLOUD_ROOT + file_type + '/' + file_type_id
        if not os.path.exists(local_path_root):
            os.makedirs(local_path_root)

        local_file_path = settings.GCLOUD_ROOT + file_path
        # local_url = settings.GCLOUD_URL_ROOT + file_path
        with open(local_file_path, 'wb+') as destination:
            for chunk in f.chunks():
                destination.write(chunk)
        gcloud_path = file_path
        c = CgsBucket(bucket_root, project=settings.BUCKET_PROJECT, log_level='debug')
        c.copyFileToBucket(local_file_path, gcloud_path)

    except Exception as e:
            return "File uploading failed : %s" % e.message

    return file_path  # local_path for now.. URL for later


def handle_get_file(file_type, file_type_id, f_name, force=False):  # force => get from storage only
    file_path = file_type + '/' + file_type_id + '/' + f_name

    local_file_path = settings.GCLOUD_ROOT + file_path
    local_url = settings.GCLOUD_URL_ROOT + file_path
    if not force:
        if os.path.exists(local_file_path):
            return local_url
    local_path_root = settings.GCLOUD_ROOT + file_type + '/' + file_type_id
    if not os.path.exists(local_path_root):
        os.makedirs(local_path_root)

    gcloud_path = file_path

    c = CgsBucket(settings.BUCKET_ROOT, project=settings.BUCKET_PROJECT)
    c.copyFileFromBucket(gcloud_path, local_file_path)
    if os.path.exists(local_file_path):
        return local_url
    else:
        return 'File Download Error'


def get_bucket(bucket_root=settings.BUCKET_ROOT, project=settings.BUCKET_PROJECT):
    c = CgsBucket(bucket_root, project=project, log_level='debug')
    return c


def save_to_storage(local_path, file_path):
    c = CgsBucket(settings.BUCKET_ROOT, project=settings.BUCKET_PROJECT)
    c.copyFileToBucket(local_path, file_path)


def get_from_storage(file_path, local_path, root=settings.BUCKET_ROOT):
    c = CgsBucket(root, project=settings.BUCKET_PROJECT)
    r = c.copyFileFromBucket(file_path, local_path)
    return r
'''
    Cartagenia
'''


def register_check(mrn):
    check = Check('bcm', mrn)
    cwb = BenchLabNgs(settings.CARTAGENIA_IP, 443, 'bcm', log_level='debug')
    r = cwb.assayRegistration('check', check.getJson())
    return 'assay_id' in r.content


def register_patient(pid):
    '''

    '''
    patient = Patients.objects.get(id=pid)
    if patient.ethnicity == '':
        return 'Ethnicity is Mandatory'
    cart_patient = Patient(None)
    cart_patient.firstName(str(patient.first_name)).lastName(str(patient.last_name)).middleName(str(patient.middle_name))\
        .dateOfBirth(patient.dob.month,patient.dob.day,patient.dob.year).medicalRecordNumber(str(patient.mrn)).ethnicity(str(patient.ethnicity)).sex(str(patient.sex))
    cwb = BenchLabNgs(settings.CARTAGENIA_IP, 443, settings.CARTAGENIA_USERNAME, log_level='debug')
    assay_registration_data = AssayRegistrationData('debug')
    assay_registration_data.userName(settings.CARTAGENIA_USERNAME).patientFolder('Default').proband(cart_patient, True).trioStrictChecking('No')
    assay_registration_data_json = assay_registration_data.getJson()
    if register_check(patient.mrn):
        operation = 'update'
    else:
        operation = 'create'
    r = cwb.assayRegistration(operation, assay_registration_data_json)
    print operation, r, r.content
    json_result = json.loads(r.content)
    status_code = json_result.get('status_code')
    message = status_code
    if status_code == 500:
        message = json_result.get('status_message')
    return message


def upload_vcf(cwb, mrn, asn, file_path, pipeline='Test'):
    upload = Upload().userName('bcm').medicalRecordNumber(mrn).specimenType('blood'). \
        sampleAccessionId(asn). \
        filePath(file_path).fileType('VCF_FILE').analysisReference(asn+'_'+mrn). \
        trioStrictChecking('no').analysisPipeline(pipeline)

    upload_json = upload.getJson()
    response = cwb.assayRegistration('upload', upload_json)
    return response


def register_single_assay(pid, oid,  type=None):
    patient = Patients.objects.get(id=pid)
    if patient.ethnicity == '':
        return json.dumps({'status': 'Error', 'message': 'Ethnicity is Mandatory'})
    cart_patient = Patient(None)
    p_sex = 'male' if patient.sex == 'M' or patient.sex == 'Male' or patient.sex == 'male' else 'female'
    cart_patient.firstName(str(patient.first_name)).lastName(str(patient.last_name)).middleName(str(patient.middle_name))\
        .dateOfBirth(patient.dob.month,patient.dob.day,patient.dob.year).medicalRecordNumber(str(patient.mrn)).ethnicity(str(patient.ethnicity)).sex(p_sex)
    cwb = BenchLabNgs(settings.CARTAGENIA_IP, 443, settings.CARTAGENIA_USERNAME, log_level='debug')
    assay_registration_data = AssayRegistrationData('debug')
    assay_registration_data.userName(settings.CARTAGENIA_USERNAME).patientFolder('Default').proband(cart_patient, True).trioStrictChecking('No')
    assay_registration_data_json = assay_registration_data.getJson()
    if register_check(patient.mrn):
        operation = 'update'
    else:
        operation = 'create'
    r = cwb.assayRegistration(operation, assay_registration_data_json)

    sor = SampleOrderRel.objects.get(order_id=oid, relation_id=1)
    asn = sor.sample.asn
    try:
        vcf_file = SampleFiles.objects.get(file_type='vcf', sample_id=sor.sample_id)
    except SampleFiles.DoesNotExist:
        return json.dumps({'status_code': '400', 'status_message': 'VCF file is missing .. '})

    u = upload_vcf(cwb, str(patient.mrn), str(asn), 'gs://'+settings.SAMPLE_BUCKET_ROOT+'/'+str(vcf_file.file_location))
    print operation, r, r.content, sor, u, u.content
    clog = CatargeniaLog(type=type, input=assay_registration_data_json, result=r.content)
    clog.log()
    # json_result = json.loads(r.content)
    return u.content


def register_trio_assay(patient_list, type='TRIO'):
    cwb = BenchLabNgs(settings.CARTAGENIA_IP, 443, settings.CARTAGENIA_USERNAME, log_level='debug')
    assay_registration_data = AssayRegistrationData('debug')
    assay_registration_data.userName(settings.CARTAGENIA_USERNAME).patientFolder('Default').trioStrictChecking('No')
    for p in patient_list:
        c_patient = Patients.objects.get(id=p.get('p_id'))
        p_sex = 'male' if c_patient.sex == 'M' or c_patient.sex == 'Male' or c_patient.sex == 'male' else 'female'
        if c_patient.ethnicity =='':
            return json.dumps({'status_code': '400', 'status_message': 'Ethnicity is Mandatory'})
        relation = str(p.get('relation')).lower()
        if relation == 'proband':
            proband_patient = Patient(None)
            proband_patient.firstName(str(c_patient.first_name)).lastName(str(c_patient.last_name)).middleName(
                str(c_patient.middle_name)) \
                .dateOfBirth(c_patient.dob.month, c_patient.dob.day, c_patient.dob.year).medicalRecordNumber(
                str(c_patient.mrn)).ethnicity(str(c_patient.ethnicity)).sex(p_sex)
            assay_registration_data.proband(proband_patient, True)
            o_id = p.get('o_id')
            mrn = c_patient.mrn
        else:
            re_patient = Patient(None)
            re_patient.firstName(str(c_patient.first_name)).lastName(str(c_patient.last_name)).middleName(
                str(c_patient.middle_name)) \
                .dateOfBirth(c_patient.dob.month, c_patient.dob.day, c_patient.dob.year).medicalRecordNumber(
                str(c_patient.mrn+relation)).ethnicity(str(c_patient.ethnicity)).sex(p_sex).relationShipToProband(relation)
            assay_registration_data.addRelatedSamples(re_patient, relation)

    if not proband_patient:
        return json.dumps({'status_code': '400', 'status_message': 'Proband Data is missing .. '})

    assay_registration_data_json = assay_registration_data.getJson()
    if register_check(proband_patient.json.get('medical_record_number')):
        operation = 'update'
    else:
        operation = 'create'
    r = cwb.assayRegistration(operation, assay_registration_data_json)

    sor = SampleOrderRel.objects.get(order_id=o_id, relation_id=1)
    asn = sor.sample.asn
    try:
        vcf_file = SampleFiles.objects.get(file_type='vcf',  sample_id=sor.sample_id)
    except SampleFiles.DoesNotExist:
        return json.dumps({'status_code': '400', 'status_message': 'VCF file is missing .. '})

    u = upload_vcf(cwb, str(mrn), str(asn),
                   'gs://' + settings.SAMPLE_BUCKET_ROOT + '/' + str(vcf_file.file_location))
    print operation, u, u.content
    json_result = json.loads(u.content)
    clog = CatargeniaLog(type=type, input=assay_registration_data_json, result=r.content)
    clog.log()
    # status_code = json_result.get('status_code')
    # message = status_code
    # if status_code == 500:
    #     message = json_result.get('status_message')
    return u.content


def sso_catargenia(mode='error'):
    cwb = BenchLabNgs(settings.CARTAGENIA_IP, 443, 'bcm', log_level=mode)
    sso = cwb.singleSignOn(settings.CARTAGENIA_USERNAME, settings.CARTAGENIA_SSO_URL)
    sso_json = json.loads(sso.content)
    url = sso_json['ssoSignResponse']['url']
    return url


def cartagenia_checkstatus(mrn):
    cwb = BenchLabNgs(settings.CARTAGENIA_IP, 443, settings.CARTAGENIA_USERNAME, log_level='debug')
    list_analysis = ListAnalysis(settings.CARTAGENIA_USERNAME, mrn)
    list_analysis_json = list_analysis.getJson()
    a = cwb.analysis('list', list_analysis_json)
    return json.dumps(a.json())


def cartagenia_getreport(ref):
    cwb = BenchLabNgs(settings.CARTAGENIA_IP, 443, settings.CARTAGENIA_USERNAME, log_level='debug')
    report_export = ReportExport(settings.CARTAGENIA_USERNAME, ref)
    report_export_json = report_export.getJson()
    r = cwb.analysis('report', report_export_json)
    return json.dumps(r.json())


def export_epic(so_id, pdf):
    so = SampleOrderRel.objects.get(id=so_id)
    om = outgoing_message(pdf_report=pdf, message_type='ORM')
    om.patient_mrn = so.patient.mrn
    om.patient_firstname = so.patient.first_name
    om.patient_lastname = so.patient.last_name
    om.patient_middlename = so.patient.middle_name
    om.patient_dob = so.patient.dob
    om.patient_sex = so.patient.sex
    om.patient_address1 = so.patient.address1
    om.patient_address2 = so.patient.address2
    om.patient_city = so.patient.city
    om.patient_state = so.patient.state
    om.patient_zip = so.patient.zip
    om.patient_phone = so.patient.phone
    om.patient_work_phone = so.patient.work_phone
    om.specimen_accession_id = so.sample.asn
    om.specimen_type = so.sample.type
    om.specimen_source = so.sample.source
    om.specimen_collection_date = so.sample.collection_date
    om.containers = so.container
    om.order_id = so.order_id
    om.order_name = so.order.order_name
    om.order_type = so.order.type
    om.ordering_physician_id = so.order.physician_id
    om.ordering_physician_lastname = so.order.physician_lastname
    om.ordering_physician_firstname = so.order.physician_firstname
    om.ordering_provider_name = so.order.provider_name
    om.ordering_provider_address = so.order.provider_address
    om.ordering_provider_city = so.order.provider_city
    om.ordering_provider_state = so.order.provider_state
    om.ordering_provider_zipcode = so.order.provider_zipcode
    om.save()


def executeCommand(cmd):
    import subprocess
    re = subprocess.check_output(cmd, shell=True)
    return re
