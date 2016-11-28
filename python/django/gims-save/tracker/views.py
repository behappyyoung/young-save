from django.shortcuts import render
from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.core import serializers
from .models import Samples, Orders, OrderStatus, SampleOrderRel, Patients, Pedigree, PatientRelations, OrderPhenoTypes, \
    PatientOrderPhenoType, PatientOrderPhenoList, OrderGeneList, Notes, PeopleRelations, PatientRelations
from .forms import OrderForm, OrderGeneListForm, NotesForm, NotesOrderForm, PatientRelationsForm
from mybackend.models import CustomSQL, PhenoTypeLists, GeneLists
from mybackend import functions, LoadOntology
from logger.models import accessLog, loomLog, logging, orderlog, samplelog
import json, requests, os
from gims import settings
from django.contrib import messages
from .forms import SampleOrderRelForm, PatientOrderPhenoTypeForm, PhenoTypesForm, GeneListsForm
from datetime import datetime
from django.core.cache import cache


def custom_proc(request):
    return {
        'LOOMURL': settings.LOOMURL,
    }


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


BASE_SAMPLE_SQL = 'SELECT s.*,  o.id as order_id, o.order_name, rt.rel_name as relation, ot.type_name as order_type FROM tracker_samples s ' \
                  ' left join tracker_sampleorderrel r on s.id = r.sample_id left join tracker_orders o on r.order_id = o.id ' \
                  ' left join tracker_relations rt on r.relation_id = rt.id left join tracker_ordertype ot on o.type_id = ot.id'

BASE_SAMPLEFILES_SQL='SELECT sf.*, s.asn as asn, o.order_name as ordername from tracker_samplefiles sf join tracker_samples s on sf.sample_id = s.id join tracker_orders o on sf.order_id = o.id'


@login_required(login_url='/login/')
def samples_view(request):
    if 'username' in request.session:
        print(request.session.get('username'), request.session['username'])
    else:
        return HttpResponseRedirect('/saml/?slo')
    myc = CustomSQL()
    c_samples = myc.my_custom_sql(BASE_SAMPLE_SQL +' order by s.asn; ')
    logging(request, 'access')
    return render(request, 'tracker/samples.html', {'samples':json.dumps(c_samples)})


SAMPLE_WORKFLOWS_SQL = 'SELECT * from tracker_samples s join logger_loomlog l on s.asn = l.relSample '


@login_required(login_url='/login/')
def sample_details(request, sid):
    if 'username' in request.session:
        print(request.session.get('username'), request.session['username'])
    else:
        return HttpResponseRedirect('/saml/?slo')
    myc = CustomSQL()
    c_samples = myc.my_custom_sql(BASE_SAMPLE_SQL + ' WHERE s.id = "' + sid + '" order by s.asn; ')
    asn = c_samples[0]['asn']
    c_samplefiles = myc.my_custom_sql(BASE_SAMPLEFILES_SQL  + ' WHERE s.id = "' + sid + '" ')

    c_loomlog = loomLog.objects.using('logs').filter(relSample = asn)
    jsonstring_loomlog = serializers.serialize('json', c_loomlog, fields=('analysisID', 'workflowID', 'relOrder', 'acc_time', 'loomResponse'))
    logging(request, 'access')
    return render(request, 'tracker/sample_details.html',
                  {'samples':json.dumps(c_samples), 'samplesfiles': json.dumps(c_samplefiles), 'workflows': jsonstring_loomlog},
                  context_instance=RequestContext(request, processors=[custom_proc]))


BASE_ORDER_SQL = 'SELECT *, o.id as orderid, up.title as ownername FROM tracker_orders o  ' \
                 'left join tracker_sampleorderrel rel on o.id = rel.order_id  ' \
                 'left join tracker_samples s on rel.sample_id = s.id ' \
                 'left join tracker_relations rt on rel.relation_id = rt.id' \
                ' left join tracker_ordertype ot on o.type_id = ot.id ' \
                'left join tracker_orderstatus os on o.status_id = os.id  ' \
                 'left join users_userprofile up on o.owner = up.id'



SIMPLE_ORDER_SQL = 'SELECT *, o.id as order_id FROM tracker_orders o ' \
                ' left join tracker_ordertype ot on o.type_id = ot.id ' \
                'left join tracker_orderstatus os on o.status_id = os.id'


@login_required(login_url='/saml/')
def orders_view(request):
    if 'username' in request.session:
        print(request.session.get('username'), request.session['username'])
    else:
        return HttpResponseRedirect('/saml/?slo')
    myc = CustomSQL()
    mysql = SIMPLE_ORDER_SQL+'  order by o.due_date; '
    c_orders = myc.my_custom_sql(mysql)            # raw dict
    logging(request, 'access')
    return render(request, 'tracker/orders.html', {'orders':json.dumps(c_orders)})


@login_required(login_url='/saml/')
def order_details(request, oid):
    if 'username' in request.session:
        print(request.session.get('username'), request.session['username'])
    else:
        return HttpResponseRedirect('/saml/?slo')
    myc = CustomSQL()
    c_orders = myc.my_custom_sql(BASE_ORDER_SQL+' WHERE o.id = "' + oid + '" order by o.due_date; ')            # raw dict
    oname = c_orders[0]['order_name']
    phenolists = PhenoTypeLists.objects.select_related('category').all().order_by('mybackend_phenotypecategory.priority', 'priority', 'name')
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
    title = 'Order : ' + oname
    logging(request, 'access', title)
    return render(request, 'tracker/order_details.html',
                  {'orders':json.dumps(c_orders), 'phenolists' : c_phenolist, 'workflows': jsonstring_loomlog, 'genelists':genelist, 'title': title},
                  context_instance=RequestContext(request, processors=[custom_proc]))


@login_required(login_url='/saml/')
def order_edit(request, oid):
    if request.method == 'POST':
        change = 'updated'
        c_order = Orders.objects.get(id=oid)
        if c_order.phenotype != request.POST['phenotype']:
            c_order.phenotype = request.POST['phenotype']
            change += ' phenotype / '
        if c_order.doctor_phone != request.POST['doctor_phone']:
                c_order.doctor_phone = request.POST['doctor_phone']
                change += ' physician contact info / '
        if c_order.owner != request.POST['owner']:
            change += ' ownership / From ' + functions.getUserInfo(c_order.owner, 'username') + ' To ' + functions.getUserInfo(request.POST['owner'], 'username')
            c_order.owner = request.POST['owner']
        if str(c_order.status_id) != str(request.POST['status']):
            change += ' Status / From ' + str(c_order.status) + ' To ' + getOrderStatus(request.POST['status'])
            c_order.status_id = request.POST['status']
        if c_order.desc != request.POST['desc']:
            c_order.desc = request.POST['desc']
            change += ' description / '

        if change != 'updated':
            c_order.save()
            orderlog(request, oid, c_order.order_name, change)
        return HttpResponseRedirect('/order/'+oid+'/')
    else:
        order = Orders.objects.get(id = oid)
        form = OrderForm(instance=order)
    logging(request, 'access')
    return render(request, 'tracker/EditOrder.html', {'form' : form, 'oid': oid})


@login_required(login_url='/saml/')
def order_notes(request, oid):
    if request.method == 'POST':
        form = NotesOrderForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.order_id = oid
            obj.save()
            orderlog(request, oid, getOrderInfo(oid, 'order_name'), 'new note added ')
        notes = Notes.objects.filter(order_id=oid).order_by('-update_time')
    else:
        try:
            notes = Notes.objects.filter(order_id = oid).order_by('-update_time')
        except :
            notes=[]
    if len(notes) == 0:
        notes = [{'id': ' --', 'update_time': ' -- ', 'category': ' -- ', 'note': 'no note'}]
    pid = getOrderInfo(oid, 'patient_id')
    form = NotesOrderForm(initial={'order': oid, 'patient_id':pid, 'recipient':0})
    logging(request, 'access')
    return render(request, 'tracker/Order_Notes.html', {'form' : form, 'oid': oid, 'notes':notes})


@login_required(login_url='/saml/')
def patient_notes(request, pid):
    if request.method == 'POST':
        form = NotesForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.patient_id = pid
            obj.save()
            # orderlog(request, oid, getOrderInfo(oid, 'order_name'), 'new note added ')
        notes = Notes.objects.filter(patient_id=pid).order_by('-update_time', 'order_id')
    else:
        try:
            notes = Notes.objects.filter(patient_id = pid).order_by('-update_time', 'order_id')
        except :
            notes=[]
    if len(notes) == 0:
        notes = [{'id': ' --', 'update_time': ' -- ', 'category': ' -- ', 'note': 'no note'}]
    form = NotesForm(initial={'patient_id':pid, 'recipient':0})
    logging(request, 'access')
    return render(request, 'tracker/Patient_Notes.html', {'form' : form, 'pid': pid, 'notes':notes})


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
    jsonstring_patients = serializers.serialize('json', c_patients)
    logging(request, 'access')
    return render(request, 'tracker/patients.html', {'patients':jsonstring_patients})


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
    patient = Patients.objects.get(pid=pid)
    samples = Samples.objects.filter(patient_id=pid).order_by('asn')
    orders = Orders.objects.filter(patient_id=pid)
    family_list = []
    try:
        # family = PatientRelations.objects.filter(main=pid).exclude(relationship=7)
        family = PatientRelations.objects.filter(main=pid)
        for f in family:
            ethnicity, mrn = getPatientInfo(f.relative, ['ethnicity', 'mrn'])
            family_list.append({'relative': f.relative, 'relationship': f.relationship, 'ethnicity': ethnicity, 'mrn': mrn})
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
    return render(request, 'tracker/patient_details.html',
                  {'patient':patient, 'samples':samples, 'phenotypes': phenotypes,'orders':orders, 'family': family_list, 'title': title})


@login_required(login_url='/saml/')
def patient_relationship(request, pid):
    if request.method == 'POST':
        form = PatientRelationsForm(request.POST)
        action = request.POST['action']
        if form.is_valid():
            main = request.POST['main']
            relative = request.POST['relative']
            relationship = request.POST['relationship']
            relative_sex = getPatientInfo(relative, 'sex')

            if relative_sex == 'male':
                what = 'back_relation_male'
            else:
                what = 'back_relation_female'
            relative_relationship = getPatientRelations(relationship, what)
            if action == 'Add':
                if PatientRelations.objects.filter(main=relative, relative=main).count() ==0:
                    form.save()
                    rel = PatientRelations(main=relative, relative=main, relationship=relative_relationship)
                    rel.save()
                    return HttpResponseRedirect('/patient/' + pid + '/')
                else:
                    messages.error(request, 'Relationship Exists')
                    action = 'Edit'
                    form = PatientRelationsForm(
                        initial={'main': main, 'relative': relative, 'relationship': relationship})
            else:
                rel1 = PatientRelations.objects.get(main=relative, relative=main)
                rel1.relationship = request.POST['relationship']
                rel1.save()
                rel2 = PatientRelations(main=relative, relative=main)
                rel2.relationship = relative_relationship
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
            main = request.POST.get('main')
            relative = request.POSE.get('relative')
            relationship = request.POSE.get('relationship')
            if PatientRelations.objects.filter(main=relative, relative=main).count() != 0:
                form = PatientRelationsForm(initial={'main': main, 'relative': relative, 'relationship': relationship})
                action = 'Edit'
            else:
                form = PatientRelationsForm(initial={'main': pid, 'relative': relative})
                action = 'Add'

    return render(request, 'tracker/Patient_Relationship.html', {'form':form, 'pid': pid, 'action': action, 'messages': messages})


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
        pedigree = Pedigree.objects.get(patient_id=pid)
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
        newlist.append({'name':obj.name, 'category':obj.category.name, 'list':obj.list, 'desc':obj.desc, 'id':obj.id})
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
