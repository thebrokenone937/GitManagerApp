from django.conf.urls import patterns, include, url
from gitmanager.apps.manager.views.registration import *
from gitmanager.apps.contact.views import *
from gitmanager.apps.manager.views.repository import *
from django.contrib import admin
from django.contrib.auth.views import login, logout
from django.conf.urls.static import static
from django.conf import settings

admin.autodiscover()

urlpatterns = patterns('',
    (r'^accounts/login/$',  login),
    (r'^accounts/logout/$', logout),
) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

urlpatterns += patterns('',
    url(r'^admin/', include(admin.site.urls)),
)

urlpatterns += patterns('gitmanager.apps.manager.views.registration',
    url(r'^accounts/registration/$', register),     
    url(r'^accounts/forgot-password/$', forgot_password),   
    url(r'^accounts/reset-password/(?P<user_id>.+?)/(?P<token>.+?)/$', reset_password),            
)

urlpatterns += patterns('gitmanager.apps.manager.views.repository',
    url(r'^manager/create-repository/$', create_repository),
    url(r'^manager/list-repositories/$', list_repositories),  
    url(r'^manager/list-commits/(?P<repository_id>.+?)/(?P<branch>.+?)/$', list_commits), 
    url(r'^manager/show-diff/(?P<repository_id>.+?)/(?P<commit_hash>.+?)/$', show_diff),                
    url(r'^manager/add-comment/(?P<repository_id>.+?)/(?P<commit_hash>.+?)/$', add_comment),
    url(r'^manager/edit-comment/(?P<repository_id>.+?)/(?P<commit_hash>.+?)/(?P<comment_id>.+?)/$', edit_comment),
    url(r'^manager/list-comments/(?P<repository_id>.+?)/(?P<commit_hash>.+?)/$', list_comments),
)
