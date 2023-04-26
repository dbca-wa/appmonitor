from django.contrib import messages
from django.contrib.gis import admin
from django.contrib.admin import AdminSite
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group

from django.db.models import Q

from appmonitor import models

class MonitorGroupInline(admin.TabularInline):
    model = models.MonitorGroup
    extra = 0
    raw_id_fields = ('group',)

@admin.register(models.Monitor)
class Monitor(admin.ModelAdmin):
     list_display = ('id','check_name','mon_type','json_response','active')
     list_filter = ('active','mon_type')
     search_fields = ('id','check_name',)
     inlines = [MonitorGroupInline]

@admin.register(models.MonitorHistory)
class MonitorHistory(admin.ModelAdmin):
     list_display = ('id','monitor','status','response','created')

@admin.register(models.MonitorJobLog)
class MonitorJobLog(admin.ModelAdmin):
     list_display = ('id','job','started','finished')
     readonly_fields=('job','started','finished')

# @admin.register(models.APIService)
# class APIService(admin.ModelAdmin):
#     list_display = ('id','service_slug_url','service_type','service_endpoint_url','cache_enabled','cache_limit','enabled')
#     list_filter = ('enabled',)
#     search_fields = ('service_slug_url','service_endpoint_url',)
#     fieldsets = (
#               ("Default",{
#                    'fields': ( 'service_slug_url', 'service_type', 'service_endpoint_url')
#               }),
#               ('Basic Auth', {
#                    'fields': ('basic_auth_enabled','basic_auth_username', 'basic_auth_password'),
#               }),
#               ('Amazon Web Services (AWS)', {
#                    'fields': ('aws_access_key','aws_secret_access_key', 'aws_token','aws_host','aws_region','aws_service'),
#               }),
#               ('OAuth2', {
#                    'fields': ('oauth2_url','oauth2_client_id', 'oauth2_secret','oauth2_api_ocp_apim_subscription_key'),
#               }),              
#               ('Cache', {
#                    'fields': ('cache_enabled','cache_limit',),
#               }),
#               ('Group Access', {
#                    'fields': ('group',),
#               }),
#               ('Network Access', {
#                    'fields': ('network_restriction_enabled','allowed_ips'),
#               }),
#               ('Throttling', {
#                    'fields': ('throttling_enabled','throttle_limit','throttle_period'),
#               }),
#               ('Notes', {
#                    'fields': ('notes',),
#               }),
#               ('Status', {
#                    'fields': ('enabled',),
#               }),              
#      )


# @admin.register(models.APIServiceLog)
# class APIServiceLog(admin.ModelAdmin):
#      list_display = ('service_slug_url','server_ip','client_ip','parameters_get','parameters_post','parameters_urlappendGET','error','allowed','created')
#      readonly_fields=('api_service','service_slug_url','server_ip','client_ip','parameters_get','parameters_post','error','allowed','created')

