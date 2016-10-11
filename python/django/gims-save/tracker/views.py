from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.core import serializers
from .models import Samples, Orders, SampleOrderRel, Patients, PhenoTypes, OrderPhenoTypes, PatientOrderPhenoType, PatientOrderPhenoList, OrderGeneList
from .forms import OrderForm, OrderGeneListForm
from mybackend.models import CustomSQL, PhenoTypeLists, GeneLists
from mybackend import functions
from logger.models import accessLog, loomLog, logging
import json
from gims import settings
from django.contrib import messages
from .forms import SampleOrderRelForm, PatientOrderPhenoTypeForm, PhenoTypesForm, GeneListsForm

def custom_proc(request):
    return {
        'LOOMURL': settings.LOOMURL,
    }

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
    return render(request, 'tracker/sample_details.html', {'samples':json.dumps(c_samples), 'samplesfiles': json.dumps(c_samplefiles), 'workflows': jsonstring_loomlog}, context_instance=RequestContext(request, processors=[custom_proc]))


BASE_ORDER_SQL = 'SELECT *, o.id as orderid FROM tracker_orders o  left join tracker_sampleorderrel rel on o.id = rel.order_id ' \
                 ' left join tracker_samples s on rel.sample_id = s.id left join tracker_relations rt on rel.relation_id = rt.id' \
                ' left join tracker_ordertype ot on o.type_id = ot.id ' \
                'left join tracker_orderstatus os on o.status_id = os.id'


SIMPLE_ORDER_SQL = 'SELECT *, o.id as order_id FROM tracker_orders o ' \
                ' left join tracker_ordertype ot on o.type_id = ot.id ' \
                'left join tracker_orderstatus os on o.status_id = os.id'

BASE_PHENOTYPE_SQL = 'select * from tracker_phenotypes p '

@login_required(login_url='/saml/')
def orders_view(request):
    if 'username' in request.session:
        print(request.session.get('username'), request.session['username'])
    else:
        return HttpResponseRedirect('/saml/?slo')
    myc = CustomSQL()
    mysql = SIMPLE_ORDER_SQL+'  order by o.due_date; '
    c_orders = myc.my_custom_sql(mysql)            # raw dict
    print(mysql, c_orders)
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

    print (c_phenolist)
    c_loomlog = loomLog.objects.using('logs').filter(relOrder=oname)
    jsonstring_loomlog = serializers.serialize('json', c_loomlog,
                                               fields=('analysisID', 'workflowID', 'relSample', 'acc_time', 'loomResponse'))

    logging(request, 'access')
    return render(request, 'tracker/order_details.html', {'orders':json.dumps(c_orders), 'phenolists' : c_phenolist, 'workflows': jsonstring_loomlog, 'genelists':genelist}, context_instance=RequestContext(request, processors=[custom_proc]))


@login_required(login_url='/saml/')
def order_new(request):
    form = OrderForm(request.POST)
    if form.is_valid():
        form.save()

    else:
        form = OrderForm()

    return render(request, 'tracker/order_new.html', {'form' : form})


@login_required(login_url='/saml/')
def patients(request):
    if 'username' in request.session:
        print(request.session.get('username'), request.session['username'])
        if 'Interpretation' not in request.session.get('role') and 'Manager' not in request.session.get('role'):
            accessLog(url=request.path_info, remote_address=request.environ['REMOTE_ADDR'], result='redirect',
                      access_type="UnAuthorized",
                      user_id=request.user).log()
            message = " You do not have permission to load  %s" % request.path_info
            messages.error(request, message)
            return HttpResponseRedirect('/')
    else:
        return HttpResponseRedirect('/saml/?slo')
    c_patients = Patients.objects.all()
    print(c_patients)
    jsonstring_patients = serializers.serialize('json', c_patients)
    logging(request, 'access')
    return render(request, 'tracker/patients.html', {'patients':jsonstring_patients})


BASE_PATIENT_SQL = 'SELECT *  FROM tracker_patients p '
#
SAMPLE_PATIENT_SQL = 'SELECT s.*, p.*, s.id as sample_id FROM tracker_patients p ' \
                   ' join tracker_samples s on p.pid = s.patient_id '

ORDER_PATIENT_SQL = 'SELECT p.*, o.*, os.*, o.id as order_id, o.order_name, ot.type_name as order_type FROM tracker_patients p ' \
                   ' join tracker_orders o on o.patient_id = p.pid join tracker_ordertype ot on o.type_id = ot.id join tracker_orderstatus os on o.status_id = os.id'

PHENOTYPE_PATIENT_SQL = 'SELECT *  FROM tracker_patients p ' \
                   ' left join tracker_patientorderphenotype pop on p.id = pop.patient_id left join tracker_phenotypes ph on ph.id = pop.phenotype_id '


#
@login_required(login_url='/saml/')
def patient_details(request, pid):
    if 'username' in request.session:
        print(request.session.get('username'), request.session['username'])
        if 'interpretation' not in request.session.get('role').lower() and 'manager' not in request.session.get(
                'role').lower():
            accessLog(url=request.path_info, remote_address=request.environ['REMOTE_ADDR'], result='redirect',
                      access_type="UnAuthorized",
                      user_id=request.user).log()
            message = " You do not have permission to load  %s" % request.path_info
            messages.error(request, message)
            return HttpResponseRedirect('/')
    else:
        return HttpResponseRedirect('/saml/?slo')
    myc = CustomSQL()
    mysql = BASE_PATIENT_SQL + ' WHERE p.pid = "' + pid + '" '
    c_patients = myc.my_custom_sql(mysql)            # raw dict
    mysql = SAMPLE_PATIENT_SQL + ' WHERE p.pid = "' + pid + '" '
    s_patients = myc.my_custom_sql(mysql)            # raw dict
    mysql = ORDER_PATIENT_SQL + ' WHERE p.pid = "' + pid + '" '
    o_patients = myc.my_custom_sql(mysql)            # raw dict
    mysql = PHENOTYPE_PATIENT_SQL + ' WHERE p.pid = "' + pid + '" '
    ph_patients = myc.my_custom_sql(mysql)            # raw dict

    logging(request, 'access')
    return render(request, 'tracker/patient_details.html', {'patients':json.dumps(c_patients), 'spatients':json.dumps(s_patients), 'opatients':json.dumps(o_patients), 'phpatients': json.dumps(ph_patients)})


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
            print('oid', oid, 'sid', sid, rid)
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
        print(c_list, order.__dict__)

    phenolists = PhenoTypeLists.objects.select_related('category').all().order_by('mybackend_phenotypecategory.priority', 'priority', 'name')

    return render(request, 'tracker/PatientOrderPhenoType.html', {'phenolists': phenolists, 'c_list':c_list,  'action':action, 'order':order })


@login_required(login_url='/saml/')
def order_phenopypes(request, oid):
    try:
        c_phenolists = OrderPhenoTypes.objects.filter(order_id=oid).order_by('acc')
        # phenolists =[]
        #
        # for plist in c_phenolists:
        #     print(plist)
        #     detail = functions.getTermDetails(str(plist.id))
        #     print(plist.id, 'detail', detail)
        #     # phenolists.append({'id':plist.id, 'definition':detail[0]['term_definition'], 'synonym':detail[0]['term_synonym']})
        # print(phenolists)

    except OrderPhenoTypes.DoesNotExist:
        c_phenolists = []
    order = Orders.objects.get(id=oid)
    return render(request, 'tracker/OrderPhenoTypes.html', {'phenolists': c_phenolists, 'order': order})


@login_required(login_url='/saml/')
def add_order_phenopype(request, oid):
    if request.method == 'POST':
        print (request.POST)
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
        print (request.POST)
        try:
            c_phenolist = OrderPhenoTypes.objects.get(order_id=oid, acc=request.POST['acc'])
            c_phenolist.delete()
            message = 'deleted'
        except OrderPhenoTypes.DoesNotExist:
            message = 'cannot find record'
        return HttpResponse(message)
    else:
        return HttpResponse('error')


def phenotype_hpo(request, acc):
    tid = str(functions.getTermID('acc', acc))
    details = functions.getTermDetails(tid)
    disease = functions.getDiseaseByTermID(tid)
    genes = functions.getOmimGenes(disease)
    print 'genes =>', genes
    return render(request, 'tracker/PhenoType.html', {'details':details, 'disease': disease, 'acc':acc, 'genes': genes})


def phenotype_graph(request, acc):
    tid = str(functions.getTermID('acc', acc))
    details = functions.getTermDetails(tid)
    relations = functions.getTermRelations(tid)
    print (relations, type(relations), json.dumps(relations))
    return render(request, 'tracker/PhenoType_Graph.html', {'details':details, 'relations': json.dumps(relations), 'acc':acc})


@login_required(login_url='/saml/')
def genelists(request):
    c_genelists = GeneLists.objects.select_related('category').order_by('category', 'name')
    newlist = []
    for obj in c_genelists:
        newlist.append({'name':obj.name, 'category':obj.category.name, 'list':obj.list, 'desc':obj.desc, 'id':obj.id})
    return render(request, 'tracker/GeneLists.html', {'genelists': json.dumps(newlist)})


@login_required(login_url='/saml/')
def edit_genelist(request):
    if request.method == 'POST':
        form = GeneListsForm(request.POST)
        print(request.POST)
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
    return render(request, 'tracker/EditGeneList.html', {'form': form, 'action':action, 'gid':gid})

@login_required(login_url='/saml/')
def add_patient_order_genelist(request, oid):
    if request.method == 'POST':
        print request.POST['action']
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

    return render(request, 'tracker/PatientOrderGeneList.html', {'genelists': genelist,'form': form, 'order':order })


@login_required(login_url='/saml/')
def edit_patient_order_phenopype(request, pid):
    if request.method == 'POST':
        form = PatientOrderPhenoTypeForm(request.POST)
        if form.is_valid():
            form.save()
            print(form.cleaned_data, form.cleaned_data['order'].__dict__, form.cleaned_data['order'].id)
            return HttpResponseRedirect('/order/'+str(form.cleaned_data['order'].id) + '/')

    else:
        c_phenotype = PatientOrderPhenoType.objects.get(id=pid)
        form = PatientOrderPhenoTypeForm(instance=c_phenotype)
    return render(request, 'tracker/PatientOrderPhenoType.html', {'form': form , 'action': 'edit' })


















#################################
@login_required(login_url='/saml/')
def phenotypes(request):
    c_phenotypes = PhenoTypes.objects.all().order_by('name')
    jsonstring_phenotypes = serializers.serialize('json', c_phenotypes)
    return render(request, 'tracker/PhenoTypes.html', {'phenotypes': jsonstring_phenotypes})

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
