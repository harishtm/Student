from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'Student.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^api/', include('info.urls', namespace="info")),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^api-token-auth/', 'rest_framework.authtoken.views.obtain_auth_token'),
    url(r'^user-logout/$', 'info.views.user_logout', name="user_logout"),
    url(r'^user-login/$', 'info.views.user_login', name="user_login"),
    #url(r'^api-token-auth/', 'rest_framework.authtoken.views.obtain_auth_token'),
)
