from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django import template
import functions
import settings


def privacy(request):
    """
        Privacy Page
    """
    return render(request, 'privacy.html', {'title': 'Privacy'})


# system check
def crsapi_system(request):
    sys_message = ['GIT Version : %s' % settings.GIT_BRANCH]
    remote_ip = functions.get_remote_id(request)
    sys_message.append('IP Address : %s' % request.META.get('HTTP_HOST'))
    sys_message.append('Remote IP Address : %s' % remote_ip)
    sys_message.append('Login User : %s' % request.user)
    return HttpResponse('\n'.join(sys_message), content_type="application/json")