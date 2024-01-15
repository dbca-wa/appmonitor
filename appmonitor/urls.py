"""apigw URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
from appmonitor import api 
from appmonitor import models
from appmonitor import views

urlpatterns = [
    path('admin/', admin.site.urls),

    # Home Page
    path("", views.HomePage.as_view(), name="home"),    
    re_path(r'^monitor/history/(?P<pk>[0-9]+)/record/(?P<monitor_history_id>[0-9]+)/$', views.MonitorHistoryRecord.as_view(), name='monitor_history_record'),
    re_path(r'^monitor/history/(?P<pk>[0-9]+)/$', views.MonitorHistory.as_view(), name='monitor_history'),
    
    
    path("platform/status/", views.PlatformStatus.as_view(), name="platform_status"),
    re_path(r'^platform/view/(?P<pk>[0-9]+)/$', views.PlatformView.as_view(), name='platform_view'),      
    re_path(r'^platform/view/(?P<pk>[0-9]+)/packages/(?P<package_pk>[0-9]+)/versions/$', views.PlatformPackageView.as_view(), name='platform_view'),  

    path("packages/status/", views.PackagesStatus.as_view(), name="packages_status"),    
    re_path(r'^package/(?P<pk>[0-9]+)/version/(?P<version_pk>[0-9]+)/advisory/$', views.PythonPackageAdvisoryView.as_view(), name='python_package_advisory'),  

    # API's
    path('api/get-checks/', api.get_checks, name='api_get_checks'),
    path('api/get-checks-alerts/', api.get_checks_alerts, name='api_get_checks_alerts'),    
    path('api/get-platform-info/', api.get_platform_info, name='get_platform_info'),
    path('api/get-platform-packages-info/', api.get_platform_packages_info, name='get_platform_packages_info'),
    path('api/platform/create', api.platform_create, name='platform_create'),
    path('api/platform/update', api.platform_update, name='platform_update'),
    re_path(r'^api/platform/(?P<pk>[0-9]+)/$', api.get_platform_info_by_id, name='python_package_advisory'),  
    path('api/monitor/create', api.monitoring_create, name='monitoring_create'),
    path('api/monitor/update', api.monitoring_update, name='monitoring_update'), 
    re_path(r'^api/monitor/(?P<pk>[0-9]+)/$', api.get_monitor_info_by_id, name='python_package_advisory'),  

    # Strictly used by appmonitor_client
    path('api/update-platform-information/', api.update_platform_information, name='api_update_platform_information'),
]



