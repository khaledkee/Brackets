"""Brackets URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, re_path
from django.contrib.auth import views as auth_views
from BracketsOJ import views

admin.autodiscover()
urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', auth_views.login, {'template_name': 'login.html'}, name='login'),
    re_path(r'login', auth_views.login, {'template_name': 'login.html'}, name='loginre'),
    path('logout/', auth_views.logout, {'template_name': 'logout.html'}, name='logout'),
    # path('customtest', views.submitView, name='customtest'),
    re_path(r'problems/?', views.problemsView, name='problems'),
    re_path(r'contests/?', views.contestsView, name='contests'),
    path('problem/<int:problem_id>', views.problemView, name='problem'),
    path('problem/<int:problem_id>/submit', views.submitView, name='submit'),
    re_path(r'^submissions/?(?P<page_id>\d+)?$', views.submissionView, name='submissions'),
    re_path(r'^user/(?P<user_id>\d+)/submissions/?(?P<page_id>\d+)?$', views.submissionView, name='submissions'),
    re_path('^contest/(?P<contest_id>\d+)/?$', views.dashboardView, name='dashboard'),
    path('contest/<int:contest_id>/problem/<int:problem_id>', views.problemView, name='problem'),
    re_path(r'^contest/(?P<contest_id>\d+)/scoreboard/?$', views.scoreboardView, name='scoreboard'),
    path('contest/<int:contest_id>/problem/<int:problem_id>/submit', views.submitView, name='submit'),
    re_path(r'^contest/(?P<contest_id>\d+)/submissions/?(?P<page_id>\d+)?$', views.submissionView, name='submissions'),
    re_path(r'^contest/(?P<contest_id>\d+)/user/(?P<user_id>\d+)/submissions/?(?P<page_id>\d+)?$', views.submissionView, name='submissions'),
    re_path(r'', views.contestsView, name="otherwise")
]
