from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth import authenticate, login
from rest_framework.authtoken.models import Token



class AuthenticationHeader(object):

    def process_request(self, request):
#        import ipdb;ipdb.set_trace()
        path_list = request.path.split('/')
        allowed_list = ['admin','user-login','token']
        if request.META.get('HTTP_AUTHORIZATION',False):
            pass
        elif request.user.is_authenticated():
            try:
                token = Token.objects.get(user=request.user).key
                request.META['HTTP_AUTHORIZATION'] = "Token " + str(token)
            except:
                pass
        elif any(pt.lower() in path_list for pt in allowed_list):
            pass
        else:
            return HttpResponse("Invalid authorization token please login to access")










