"""aroundme URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from django.contrib.auth.views import login as django_login
from django.contrib.auth.views import logout as django_logout

from . import views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^login/$', django_login,
        {'template_name' : 'registration/login.html'},
        name='django_login'),
    url(r'^logout/$', django_logout,
        {'next_page' : '/login/'},
        name='django_logout'),
    url(r'^signup/$', views.view_member_signup, name='view_member_signup'),
    url(r'^$', views.view_event_list, name='view_event_list'),
    #url(r'^$', views.view_main_page, name='view_main_page'),
    url(r'^add_schedule/$', views.event_save_schedule, name='event_save_schedule'),
    url(r'^delete_schedule/$', views.event_delete_schedule, name='event_delete_schedule')
]
