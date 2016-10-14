from django.contrib.auth.models import User
from django.shortcuts import render, HttpResponse, HttpResponseRedirect, get_object_or_404
from info.serializers import *
from info.models import *
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics as g, viewsets, permissions as p
from authentication import *
from django.contrib.auth import authenticate, login as auth_login, logout
from rest_framework.authentication import SessionAuthentication, BasicAuthentication, TokenAuthentication, BaseAuthentication
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from django.http import HttpResponse
from rest_framework.renderers import TemplateHTMLRenderer, JSONRenderer
from rest_framework.parsers import JSONParser
from django.views.generic import TemplateView
from rest_framework.decorators import api_view, renderer_classes, detail_route, list_route
import json
import requests
from rest_framework.pagination import PageNumberPagination
from django.db.models.signals import post_save
from django.core.cache import cache
from hashlib import md5 as md5_constructor
from django.utils.http import urlquote
from django.core.cache.utils import make_template_fragment_key
from django.views.decorators.cache import cache_page



class StudentList(g.ListAPIView):
    """
        Student ListAPIView we can use either queryset or get_queryset() 
        to return queryset
        Similarly for serializer_class or override get_serializer_class()
    """

    #queryset = Student.objects.all()
    #serializer_class = StudentSerializer
    renderer_classes = [JSONRenderer]
    authentication_classes = (ExpiringTokenAuthentication, )
    paginate_by = 5

    def get_serializer_class(self):
        return StudentSerializer

    def get_queryset(self):
        student_list = Student.objects.all().order_by('-id')
        return student_list


class AddStudent(g.CreateAPIView):
    """
        Similar to class based views (CreateView) CreateAPIView does same
        form_class is equal to serializer_class or even override post method
    """

    serializer_class = StudentListSerializers
    renderer_classes = [JSONRenderer,TemplateHTMLRenderer]

    def get(self, request, format=None):
        serializer = StudentSerializer()
        return Response({'serializer':serializer},template_name="add-student.html")

    def post(self, request, format=None):
        serializer = StudentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            #return Response(serializer.data, status=status.HTTP_201_CREATED)
            response = {'success':True,'messages':"Record Created Successfully"}
            return Response(response, status=status.HTTP_201_CREATED, template_name="add-student.html")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserView(g.CreateAPIView):
    model = User
    permissin_classes = [
        p.AllowAny # Or anon users can't register
    ]
    serializer_class = UserSerializer


"""
class AuthView(APIView):

    #authentication_classes = (QuietBasicAuthentication, )
    #authentication_classes = (SessionAuthentication, BasicAuthentication)
    authentication_classes = (TokenAuthentication,)
    #permission_classes = (p.IsAuthenticated,)
    permission_classes = (p.IsAdminUser,)
    serializer_class = UserAuthSerializer

    def post(self, request, *args, **kwargs):
        login(request, request.user)
        return Response(self.serializer_class(request.user).data)
"""



"""
class AuthView(BaseAuthentication):

    def authenticate(self, request):
        username = request.META.get('X_USERNAME')
        if not username:
            return None

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise exceptions.AuthenticationFailed('No such user')

        return (user, None)
"""


#class AuthView(APIView):
#    authentication_classes = (QuietBasicAuthentication, )
#    serializer_class = UserAuthSerializer

#    def post(self, request, *args, **kwargs):
#        pass


class ObtainExpiringAuthToken(ObtainAuthToken):
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            token, created =  Token.objects.get_or_create(user=serializer.validated_data['user'])

            utc_now = datetime.datetime.utcnow().replace(tzinfo=utc)
            if not created and token.created < utc_now - datetime.timedelta(minutes=30):
                token.delete()
                token = Token.objects.create(user=serializer.validated_data['user'])
                token.created = datetime.datetime.utcnow()
                token.save()

            #return Response({'token': token.key})
            response_data = {'token': token.key}
            return HttpResponse(json.dumps(response_data), content_type="application/json")

        return HttpResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

obtain_expiring_auth_token = ObtainExpiringAuthToken.as_view()



class EditStudent(g.UpdateAPIView):

    authentication_classes = (ExpiringTokenAuthentication,)

    def post(self, request, *args, **kwargs):
        student_id = kwargs.get('sid','')
        try:
            student_obj = Student.objects.get(id=int(student_id))
        except:
            student_obj = None
        if student_id and student_obj:
            serializer = StudentSerializer(data=request.data, instance=student_obj, partial=True)
            if serializer.is_valid():
                serializer.save()
                response = {'status':True,'messages':'Successfully Updated'}
            else:
                response = {'status':False,'messages':'Error','error':serializer.errors}
        else:
            response = {'status':False,'messages':'Error','error':'Please pass valid student Id'}
        return Response(response)


class ListAllStudents(TemplateView):

    template_name = 'student_list.html'

    def get_context_data(self, **kwargs):
        return dict(super(ListAllStudents, self).get_context_data(**kwargs), **{'request':self.request})




class StudentAdd(APIView):

    renderer_classes = (JSONRenderer, TemplateHTMLRenderer, )
    template_name = 'add-student.html'

    def get(self, request,format=None):
        if request.accepted_renderer.format == 'html':
            serializer = StudentSerializer()
            return Response({'serializer':serializer})

    def post(self, request, format=None):
        serializer = StudentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            #return Response(serializer.data, status=status.HTTP_201_CREATED)
            if request.accepted_renderer.format == 'html':
                return HttpResponseRedirect('/api/studentList/')
            response = {'success':True,'messages':"Record Created Successfully"}
            return Response(response, status=status.HTTP_201_CREATED)
        else:
            return Response({'serializer':serializer.data,'errors':serializer.errors}, status=status.HTTP_400_BAD_REQUEST)





"""
@api_view(('GET',))
@renderer_classes((TemplateHTMLRenderer, JSONRenderer))
def student_add(request):

    if request.method == 'GET':
        if request.accepted_renderer.format == 'html':
            # TemplateHTMLRenderer takes a context dict,
            # and additionally requires a 'template_name'.
            # It does not require serialization.
            serializer = StudentSerializer()
            return Response(serializer, template_name='add-student.html')

    if request.method == 'POST':
    # JSONRenderer requires serialized data as normal.
        serializer = StudentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            #return Response(serializer.data, status=status.HTTP_201_CREATED)
            response = {'success':True,'messages':"Record Created Successfully"}
            return Response(response, status=status.HTTP_201_CREATED, template_name="add-student.html")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
"""


def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user_obj = User.objects.filter(username = username).exists()
        if user_obj:
            user = User.objects.get(username = username)
            if user.is_active:
                valid_pwd = user.check_password(password)
                if valid_pwd:
                    # username and email are same
                    user = authenticate(username=str(username),password=str(password))
                    auth_login(request, user)
                    success = True
                    url = 'http://127.0.0.1:8000/api/token/'
                    params = {'username':username,'password':password}
                    result = requests.post(url,data=params)
                    request.session['HTTP_AUTHORIZATION'] = result.json().get('token')
                    return HttpResponseRedirect('/api/studentList/')
                else:
                    error_msg = "Invalid Password"
            else:
                error_msg = "User is inactive"
        else:
            error_msg = "Email does not exist"
    return render(request, 'login.html', locals())


def user_logout(request):
    logout(request)
    return HttpResponse('Logged out successfully')


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 1
    page_size_query_param = 'page_size'
    max_page_size = 1


class UserViewSet(viewsets.ViewSet):

    """
        A simple ViewSet for listing or retrieving users.
        http://stackoverflow.com/questions/18969798/adding-more-views-to-a-router-or-viewset-django-rest-framework
    """

    queryset = User.objects.all()
    pagination_class = StandardResultsSetPagination

    def list(self, request):
        "GET Method"
        serializer = UserSerializer(self.queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        "GET Method"
        user = get_object_or_404(self.queryset, pk=pk)
        serializer = UserSerializer(user)
        return Response(serializer.data)

    def create(self, request):
        "POST Method"
        return Response(status.HTTP_200_OK)

    def update(self, request, pk=None):
        "PUT Method"
        return Response(status.HTTP_200_OK)

    def partial_update(self, request, pk=None):
        "PATCH Method"
        return Response(status.HTTP_200_OK)

    def destroy(self, request, pk=None):
        "DELETE Method"
        pass

    @list_route()
    def recent_users(self, request):
        recent_users = User.objects.all().order_by('-last_login')
        serializer = UserSerializer(recent_users, many=True)
        return Response(serializer.data)


#============================ Tried Memcached =================================#



def invalidate_template_fragment(fragment_name, *variables):
    cache_key = make_template_fragment_key(fragment_name, vary_on=variables) 
    cache.delete(cache_key)


@cache_page(30) # 600 seconds
def cache_student_list(request):
    object_list = []
    if request.method == 'GET':
        cache_key = 'my_heavy_view_cache_key'
        #cache_time = 30 # time to live in seconds
        cache.delete(cache_key)
        result = cache.get(cache_key)
        if not result:
            object_list = Student.objects.all()
            result = object_list# some calculations here
            cache.set(cache_key, result)
        invalidate_template_fragment(cache_key)
    return render(request, 'cache-student-list.html', locals())


def clear_cache(sender, **kwargs):
    cache._cache.flush_all()


post_save.connect(clear_cache, sender=Student)




#====================================== End of Memcached ======================#








