from django.shortcuts import render
from crsapi import settings, functions
import requests, json, yaml
from django.http import HttpResponseRedirect, HttpResponse
from .models import ResponseLog, Chromosome, Accessions, GenomeSnpMap
import ttm_functions


def index(request):
    if request.user:
        print('user', request.user)
    return HttpResponseRedirect('/twothreeandme/consent/')

    # print('GET', request.GET, 'POST', request.POST)
    #
    # if request.GET.get('error'):
    #     error = request.GET.get('error')
    #     error_description = request.GET.get('error_description')
    #     return_data = {'Error': str(error), 'error_description': str(error_description)}
    # else:
    #     message = settings.ANDME_URL + '/authorize/?redirect_uri=' + settings.REDIRECT_URL + '&response_type=code&client_id='+settings.CLIENT_ID+'&scope=basic names email genomes'
    #     return_data = {'Message': str(message)}
    #     return render(request, 'TwoThreeAndMe/index.html', {'title': 'TwoThreeAndMe', 'return_data': return_data,
    #                 'url': settings.ANDME_URL, 'return_url': settings.REDIRECT_URL, 'message': message})
    #
    # return HttpResponse(json.dumps(return_data), content_type="application/json")


def get_grant(request):
    print('GET', request.GET, 'POST', request.POST)

    if request.GET.get('error'):
        error = request.GET.get('error')
        error_description = request.GET.get('error_description')
        return_data = {'Error': str(error), 'error_description': str(error_description)}
    else:
        message = settings.ANDME_URL + '/authorize/?redirect_uri=' + settings.REDIRECT_URL + '&response_type=code&client_id='+settings.CLIENT_ID+'&scope=basic names email genomes'
        return_data = {'Message': str(message)}
        return render(request, 'TwoThreeAndMe/index.html', {'title': 'TwoThreeAndMe', 'return_data': return_data,
                    'url': settings.ANDME_URL, 'return_url': settings.REDIRECT_URL, 'message': message})

    return HttpResponse(json.dumps(return_data), content_type="application/json")


def get_token(code):
    url = settings.ANDME_URL + '/token/'
    payload = {'client_id': settings.CLIENT_ID, 'client_secret' : settings.CLIENT_SECRET, 'grant_type': 'authorization_code', 'code': code,  'redirect_uri': settings.REDIRECT_URL,  'scope': 'basic names email genomes'}
    r = requests.post(url, data=payload)
    print(r, r.__dict__)
    json.loads(r.content)
    if r.status_code == 200:
        json_re = json.loads(r.content)
        return_data = {'status_code': 200, 'access_token': json_re.get('access_token')}
    else:
        return_data = {'status_code': r.status_code, 'error_message': r.content}
    return return_data


def ttm_response_withID(request):
    print('ttm_response test with profile ID' )
    response_list = []
    if request.GET.get('error'):
        error = request.GET.get('error')
        error_description = request.GET.get('error_description')
        return_data = {'Error': str(error), 'error_description': str(error_description)}
    elif request.GET.get('code'):
        code = str(request.GET.get('code'))

        getToken = get_token(code)
        if getToken.get('status_code') == 200:
            token = getToken.get('access_token')
        else:
            return HttpResponse(json.dumps(getToken))

        headers = {'Authorization': 'Bearer ' + token}

        profile_id = ''

        in_c_url = settings.ANDME_URL + '/1/names/' + profile_id + '/'
        try:
                    genome_r = requests.get(in_c_url, headers=headers)
                    in_r_log = ResponseLog(action='get names', url=in_c_url, request_header=headers,
                                           response=genome_r.content)
                    response_list.append('get names %s: %s' % (in_c_url, genome_r.status_code))
        except Exception as e:
                    e_message = e.message if e.message else e.args[1]
                    in_r_log = ResponseLog(action='get names - error', url=in_c_url, request_header=headers, response=e_message)
        in_r_log.save()

        in_c_url = settings.ANDME_URL + '/1/genomes/' + profile_id + '/'
        try:
            genome_r = requests.get(in_c_url, headers=headers)
            in_r_log = ResponseLog(action='get genomes', url=in_c_url, request_header=headers,
                                   response=genome_r.content)
            response_list.append('get genomes %s: %s' % (in_c_url, genome_r.status_code))
        except Exception as e:
            e_message = e.message if e.message else e.args[1]
            in_r_log = ResponseLog(action='get genomes - error', url=in_c_url, request_header=headers,
                                   response=e_message)
        in_r_log.save()

    return HttpResponse(json.dumps(response_list), content_type="application/json")


def ttm_response(request):
    print('ttm_response', 'GET', request.GET, 'POST', request.POST)
    response_list = []
    token = ''
    profile_id = ''

    if request.GET.get('error'):
        error = request.GET.get('error')
        error_description = request.GET.get('error_description')
        return_data = {'Error': str(error), 'error_description': str(error_description)}
    elif request.GET.get('code'):
        code = str(request.GET.get('code'))

        getToken = get_token(code)
        if getToken.get('status_code') == 200:
            token = getToken.get('access_token')
        else:
            return HttpResponse(json.dumps(getToken))

        headers = {'Authorization': 'Bearer ' + token}

        c_url = settings.ANDME_URL + '/3/report/'
        try:
            r = requests.get(c_url, headers=headers)
            r_log = ResponseLog(action='get report', url=c_url, request_header=headers, response=r.content)
            response_list.append('Get Report:  %s , Status: %s'%(c_url, r.status_code))
        except Exception as e:
            e_message = e.message if e.message else e.args[1]
            r_log = ResponseLog(action='get report', url=c_url, request_header=headers, response=e_message)
            response_list.append('Get Report %s, Error:  %s' % (c_url, e_message))
        r_log.save()

        c_url = settings.ANDME_URL + '/3/account/'
        try:
            acount_r = requests.get(c_url, headers=headers)
            r_log = ResponseLog(action='get acount', url=c_url, request_header=headers, response=acount_r.content)
            response_list.append(' Get Account: %s, Status:  %s' % (c_url, acount_r.status_code))
        except Exception as e:
            e_message = e.message if e.message else e.args[1]
            r_log = ResponseLog(action='get acount', url=c_url, request_header=headers, response=e_message)
            response_list.append(' Get Account: %s, Error:  %s' % (c_url, e_message))
        r_log.save()

        # c_url = settings.ANDME_URL + '/1/user/'
        # try:
        #     user_r = requests.get(c_url, headers=headers)
        #     r_log = ResponseLog(action='get user', url=c_url, request_header=headers, response=user_r.content)
        #     response_list.append(' Get User %s: %s' % (c_url, user_r.status_code))
        #
        #     json_re = json.loads(user_r.content)
        #     print(user_r, json_re)
        #     profile = json_re.get('profiles')
        #     if profile:
        #         profile_id = profile[0].get('id')
        #     else:
        #         response_list.append(' Can not get profile ID from user from profile: %s   ' %profile)
        #         profile_id = None
        #
        # except Exception as e:
        #     e_message = e.message if e.message else e.args[1]
        #     response_list.append(e_message)
        #     r_log = ResponseLog(action='get user - error', url=c_url, request_header=headers, response=e_message)
        # r_log.save()

    else:
        response_list.append(request.GET)
        ttm_authurl = settings.ANDME_URL + '/authorize/?redirect_uri=' + settings.REDIRECT_URL + '&response_type=code&client_id=' + settings.CLIENT_ID + '&scope=basic names email genomes'

    return render(request, 'TwoThreeAndMe/ttm_response.html',
                  {'title': 'TwoThreeAndMe Response', 'token': token, 'ttm_authurl': ttm_authurl,
                   'profile_id': profile_id, 'response_list': response_list})


def get_account(request, token):
    message =''
    if token:
        headers = {'Authorization': 'Bearer ' + token}
        in_c_url = settings.ANDME_URL + '/3/account/'
        try:
            account_r = requests.get(in_c_url, headers=headers)
            in_r_log = ResponseLog(action='get account', url=in_c_url, request_header=headers,
                                   response=account_r.content)
            message = account_r.content
        except Exception as e:
            message = e.message if e.message else e.args[1]
            in_r_log = ResponseLog(action='get account - error', url=in_c_url, request_header=headers,
                                   response=message)
        in_r_log.save()
    else:
        message = 'Data - token %s: missing'%token

    return HttpResponse(message, content_type="application/json")


def get_genomes(request, profile_id, token):
    message =''
    if profile_id and token:
        headers = {'Authorization': 'Bearer ' + token}
        in_c_url = settings.ANDME_URL + '/1/genomes/' + profile_id + '/'
        try:
            genome_r = requests.get(in_c_url, headers=headers)
            in_r_log = ResponseLog(action='get genomes', url=in_c_url, request_header=headers,
                                   response=genome_r.content)
            message = genome_r.content
        except Exception as e:
            message = e.message if e.message else e.args[1]
            in_r_log = ResponseLog(action='get genomes - error', url=in_c_url, request_header=headers,
                                   response=message)
        in_r_log.save()
    else:
        message = 'Data - profile %s:  - token %s: missing'%(profile_id, token)

    return HttpResponse(message, content_type="application/json")


def update_chromosome(request, cid=1, offset=0):
    try:
        message = ttm_functions.update_chromosome(cid, offset)

    except Exception as e:
        e_message = e.message if e.message else ','.join(map(str, e.args))
        message = '%s : Update Chromosome Error -   %s'%e_message

    return HttpResponse(message, content_type="application/json")


def update_accessions(request, cid=1):
    count = 0
    try:
        message = ttm_functions.update_accessions(cid)
    except Exception as e:
        e_message = e.message if e.message else ','.join(map(str, e.args))
        message = 'Update Accession Error -   %s'%e_message

    return HttpResponse(message, content_type="application/json")


def json_testing(request):
    my_json = '{"data":[{"id":"2e6ed1728b80b0aa","first_name":"young","last_name":"park","email":"ypark@stanfordhealthcare.org","profiles":[]}],"links":{"next":null}}'

    return render(request, 'TwoThreeAndMe/json_testing.html', {'title': 'TwoThreeAndMe Response','my_json': my_json})


def get_auth(request):
    url = settings.ANDME_URL + '?' + settings.REDIRECT_URL + '&response_type=code&client_id=32da67f11903bb408596baeb4ff8b750&&scope=basic rs123'
    print(url)
    try:
        r = requests.get(url)
        print(r)
        return r.content
    except Exception as e:
        print 'Fail to auth  to 23andme', url, e
        e_message = e.message if e.message else ','.join(map(str, e.args))
        return 'Error - %s'%e_message


def insert_map(request):
    try:
        message = ttm_functions.insert_map()

    except IOError as e:
        e_message = e.message if e.message else ','.join(map(str, e.args))
        message = 'Update Accession Error -   %s' % e_message

    return HttpResponse(message, content_type="application/json")


def get_consent(request):
    # try:
    #     c_sample = Samples.objects.get(id=sid)
    # except Samples.DoesNotExist:
    #     message = 'Sample %s does not exist '%sid
    #     messages.error(request, message)
    #     return HttpResponseRedirect('/samples/')

    # if request.method == 'POST':
        # try:
        #     if c_sample.note != request.POST['note']:
        #         c_sample.note = request.POST['note']
        #         change += ' Note / '
        #     # if c_sample.desc != request.POST['desc']:
        #     #     c_sample.desc = request.POST['desc']
        #     #     change += ' description / '
        #     if c_sample.volume != float(request.POST['volume']):
        #         change += ' volume from %s to %s ' % (c_sample.volume, request.POST['volume'])
        #         c_sample.volume = float(request.POST['volume'])
        #     if change != 'updated':
        #         messages.error(request, change)
        #         c_sample.save()
        #         samplelog(request, sid, change)
        # except Exception as e:
        #     e_message = e.message if e.message else ','.join(map(str, e.args))
        #     message = 'Error - Could not update sample %s : %s' % (sid, e_message)
        #     messages.error(request, message)
        # return HttpResponseRedirect('/sample/'+sid+'/Edit/')
    # else:
    #     form = SampleForm(instance=c_sample)
    title = 'Consent Form'
    return render(request, 'Consent/info.html', {'title':title})


def consent_form(request):
    title = 'Consent Form'
    return render(request, 'Consent/form.html', {'title': title})
