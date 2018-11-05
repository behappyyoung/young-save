from django.shortcuts import render
from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.contrib.auth import authenticate, login,logout
from crsapi import settings
from .models import UserProfile
import usersFunctions
from django.contrib.auth.models import User
import json
from django.contrib import messages


# Create your views here.
def user_login(request, uid):
    """
        Allow user login without onelogin when TESTING is True
        :param request:
        :param uid: uid for user
        :return:
    """
    if settings.TESTING:
        logout(request)
        try:
            c_user = User.objects.get(username=uid)
            # c_user.save()
        except User.DoesNotExist:
            print('no users')
            c_user = User.objects.create_user(uid, uid + '@cgs-dev.stanfordmed.org', 'saml')
            c_user.save()
        try:
            c_profile = UserProfile.objects.get(username=uid)
            c_profile.save()
        except UserProfile.DoesNotExist:
            print('no user profile ')
            if uid == settings.MANAGER_ACCOUNT:
                role = 'Admin'
                group = 'Manager'
                title = 'Manager'
            elif uid == settings.ADMIN_ACCOUNT:
                role = 'Admin'
                group = 'Admin'
                title = 'Admin'
            else:
                role = 'User'
                group = 'NEW'
                title = 'User'
            c_profile = UserProfile(user=c_user, username=uid,
                                      title=title, group=group, role=role)
            c_profile.save()
        user = authenticate(username=uid, password='saml')
        request.session['username'] = uid
        request.session['role'] = c_profile.role
        request.session['group'] = c_profile.group
        login(request, user)

    else:
        return HttpResponseRedirect('/adfs/login/')

    if c_profile.group == 'NEW':
        return HttpResponseRedirect('/user/profile/')
    else:
        return HttpResponseRedirect('/')


def profile(request):
    username = str(request.user)
    user_dict = usersFunctions.get_userinfo(username)
    if len(user_dict) == 0:
        message = 'User %s Profile does not exist ' % username
        messages.error(request, message)
        return HttpResponseRedirect('/adfs/login/')
    # usermessage = UserMessage.objects.filter(user=request.user).order_by('-update_time')
    title = 'Profile : ' + username
    # logging(request, 'access', title)

    return render(request, 'Users/Profile.html',
                      {'user_list': json.dumps(user_dict), 'title': title})
