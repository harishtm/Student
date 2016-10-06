from django.conf.urls import patterns, include, url
from rest_framework import routers
from info.views import *
from web_views import *
#from info.alternate_views import StudentList, AddStudent

router = routers.DefaultRouter()
router.register(r'users-list', UserViewSet, 'list')



urlpatterns = patterns('',
    url(r'^list-student/$', StudentList.as_view(), name='list_student'),
    url(r'^add-student/$', AddStudent.as_view(), name='add_student'),
    url(r'^add-user/$', UserView.as_view(), name='add_user'),
    #url(r'^auth/$', AuthView, name="user_authenticate"),
    url(r'^token/', 'info.views.obtain_expiring_auth_token'),
    url(r'^edit-student/(?P<sid>.*)/$',EditStudent.as_view(), name="edit_student"),
)


urlpatterns += patterns('',
    url(r'^studentList/$', ListAllStudents.as_view(),name="liststudentweb"),
    url(r'^studentAdd/$', StudentAdd.as_view(),name="student_add"),
)


urlpatterns += router.urls
