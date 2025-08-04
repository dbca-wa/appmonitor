from django.contrib import messages
from django.contrib.gis import admin
from django.contrib.admin import AdminSite
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from nested_inline.admin import NestedStackedInline, NestedModelAdmin


from django.db.models import Q

from appmonitor import models

class MonitorAlertInline(admin.TabularInline):
    model = models.MonitorAlert
    extra = 0    

class MonitorGroupInline(admin.TabularInline):
    model = models.MonitorGroup
    extra = 0
    raw_id_fields = ('group',)

@admin.register(models.Monitor)
class Monitor(admin.ModelAdmin):
     list_display = ('id','check_name','mon_type','json_response','active')
     list_filter = ('active','mon_type')
     search_fields = ('id','check_name',)
     inlines = [MonitorGroupInline, MonitorAlertInline]

@admin.register(models.MonitorHistory)
class MonitorHistory(admin.ModelAdmin):
     list_display = ('id','monitor','status','response','created')

@admin.register(models.MonitorJobLog)
class MonitorJobLog(admin.ModelAdmin):
     list_display = ('id','job','started','finished')
     readonly_fields=('job','started','finished')

class ResponsibleGroupAdvisoryEmailInline(admin.TabularInline):
     list_display = ('id','email','active','created')
     model = models.ResponsibleGroupAdvisoryEmail
     extra = 0   

class ResponsibleGroupOutstandingAdvisoryEmailInline(admin.TabularInline):
     list_display = ('id','email','active','created')
     model = models.ResponsibleGroupOutstandingAdvisoryEmail
     extra = 0 

class ResponsibleGroupAccessUserInline(admin.TabularInline):
     list_display = ('id','email','active','created')     
     model = models.ResponsibleGroupAccessUser
     extra = 0 

class ResponsibleGroupAccessGroupInline(admin.TabularInline):
     list_display = ('id','group','active','created')
     raw_id_fields = ('group',)
     model = models.ResponsibleGroupAccessGroup
     extra = 0 


@admin.register(models.ResponsibleGroup)
class ResponsibleGroup(admin.ModelAdmin):
     list_display = ('id','group_name','active')
     inlines = [ResponsibleGroupAdvisoryEmailInline,ResponsibleGroupOutstandingAdvisoryEmailInline, ResponsibleGroupAccessGroupInline, ResponsibleGroupAccessUserInline]

@admin.register(models.ManualCheck)
class ManualCheck(admin.ModelAdmin):
     list_display = ('id','check_name','system_id','group_responsible','active')

@admin.register(models.NotificationEmail)
class ResponsibleGroup(admin.ModelAdmin):
     list_display = ('id','email','created')


class TicketFilterNotificationInline(admin.TabularInline):
    model = models.TicketFilterNotification
    extra = 0

class NewTicketFilterNotificationInline(admin.TabularInline):
    model = models.NewTicketFilterNotification
    extra = 0

@admin.register(models.TicketFilter)
class TicketFilter(admin.ModelAdmin):
     list_display = ('id','name','url','active')
     list_filter = ('active',)
     search_fields = ('id','name','url')
     inlines = [TicketFilterNotificationInline,NewTicketFilterNotificationInline]

@admin.register(models.Tickets)
class Tickets(admin.ModelAdmin):
     list_display = ('id','ticket_reference_no','last_update_str','created')

@admin.register(models.TicketStatus)
class TicketStatus(admin.ModelAdmin):
     list_display = ('id','status_name','freskdesk_status_id','active','created')

@admin.register(models.TicketSystem)
class TicketSystem(admin.ModelAdmin):
     list_display = ('id','system_name','freskdesk_system_id','active','created')

@admin.register(models.PythonPackage)
class PythonPackageAdmin(admin.ModelAdmin):
     list_display = ('id','package_name','current_package_version','vulnerability_total','severity_rollup','active','updated','created')
     search_fields = ('id','package_name','current_package_version')


@admin.register(models.DebianPackage)
class DebianackageAdmin(admin.ModelAdmin):
     list_display = ('id','package_name','vulnerability_total','severity_rollup','active','updated','created')
     search_fields = ('id','package_name','current_package_version')


class DebianPackageInline(admin.TabularInline):
     list_display = ('id','package_name','vulnerability_total','active','vulnerability_total','severity_rollup','updated','created')
     readonly_fields=('package_name','current_package_version','vulnerability_total','active','updated','created')
     model = models.DebianPackage
     extra = 0

     def has_add_permission(self,request,obj):
          return False

     def has_delete_permission(self, request, obj=None):
          return False


class PythonPackageInline(admin.TabularInline):
     list_display = ('id','package_name','vulnerability_total','severity_rollup','active','updated','created')
     readonly_fields=('severity_rollup','package_name','current_package_version','vulnerability_total','active','updated','created')
     model = models.PythonPackage
     extra = 0

     def has_add_permission(self,request,obj):
          return False

     def has_delete_permission(self, request, obj=None):
          return False

class PlatformAdvisoryEmailInline(admin.TabularInline):
     list_display = ('id','email','created')
     model = models.PlatformAdvisoryEmail
     extra = 0    

class PlatformDependaBotAdvisory(admin.TabularInline):
     list_display = ('id','ghsa_id','package_name','ecosystem','severity','cve_id','updated','created')
     model = models.PlatformDependaBotAdvisory
     readonly_fields=('number','state','ghsa_id','package_name','ecosystem','severity','cve_id','updated','created')
     extra = 0   

@admin.register(models.Platform)
class Platform(admin.ModelAdmin):
     list_display = ('id','system_name','operating_system_name','operating_system_version','python_version','django_version','platform_current_severity','updated','created')
     search_fields = ('id','system_name')
     readonly_fields=('platform_current_severity','operating_system_name','operating_system_version','python_version','django_version','json_response','updated','created')
     #exclude = ('json_response',)
     inlines = [PlatformAdvisoryEmailInline,PlatformDependaBotAdvisory,PythonPackageInline, DebianPackageInline]

@admin.register(models.PythonPackageVersionHistory)
class PythonPackageVersionHistory(admin.ModelAdmin):
     list_display = ('id','python_package','package_version','created')

@admin.register(models.AccessGroup)
class AccessGroupAdmin(admin.ModelAdmin):
     list_display = ('id','access_type','group_name','active', 'created')
     list_filter = ('access_type','group_name')

@admin.register(models.PythonPackageVulnerabilityVersion)
class PythonPackageVulnerabilityVersionAdmin(admin.ModelAdmin):
     list_display = ('id','python_package','package_version','updated','created')
     search_fields = ('id','package_version','cve')
     raw_id_fields = ('python_package',)

@admin.register(models.PythonPackageVulnerabilityVersionAdvisoryInformation)
class PythonPackageVulnerabilityVersionAdvisoryInformationAdmin(admin.ModelAdmin):
     list_display = ('id','package_version','advisory','cve','baseSeverity','baseScore','updated','created')
     search_fields = ('id','package_version__package_version','cve','baseSeverity')
     raw_id_fields = ('package_version',)

class PythonPackageVulnerabilityVersionAdvisoryInformationInline(NestedStackedInline):
     list_display = ('id','package_version','advisory','cve','updated','created')
     readonly_fields=('package_version','advisory','cve','updated','created')
     model = models.PythonPackageVulnerabilityVersionAdvisoryInformation
     extra = 1
     
     def has_add_permission(self,request,obj):
          return False

     def has_delete_permission(self, request, obj=None):
          return False

class PythonPackageVulnerabilityVersionInline(NestedStackedInline):
     list_display = ('id','python_package','package_version','updated','created')
     readonly_fields=('python_package','package_version','updated','created')
     model = models.PythonPackageVulnerabilityVersion
     extra = 1
     inlines = [PythonPackageVulnerabilityVersionAdvisoryInformationInline,]

     def has_add_permission(self,request,obj):
          return False

     def has_delete_permission(self, request, obj=None):
          return False

@admin.register(models.DebianPackageVulnerabilityVersionAdvisoryInformation)
class DebianPackageVulnerabilityVersionAdvisoryInformationAdmin(admin.ModelAdmin):
     #list_display = ('id','package_version','advisory','cve','baseSeverity','baseScore','updated','created')
     list_display = ('id','package_version','advisory','cve','baseSeverity','baseScore','updated','created')
     search_fields = ('id','package_version__package_version','cve','baseSeverity')
     raw_id_fields = ('package_version',)

class DebianPackageVulnerabilityVersionAdvisoryInformationInline(NestedStackedInline):
     list_display = ('id','package_version','advisory','cve','updated','created')
     readonly_fields=('package_version','advisory','cve','updated','created')
     model = models.DebianPackageVulnerabilityVersionAdvisoryInformation
     extra = 1
     
     def has_add_permission(self,request,obj):
          return False

     def has_delete_permission(self, request, obj=None):
          return False

class DebianPackageVulnerabilityVersionInline(NestedStackedInline):
     list_display = ('id','debian_package','package_version','updated','created')
     readonly_fields=('debian_package','package_version','updated','created')
     model = models.DebianPackageVulnerabilityVersion
     extra = 1
     inlines = [DebianPackageVulnerabilityVersionAdvisoryInformationInline,]

     def has_add_permission(self,request,obj):
          return False

     def has_delete_permission(self, request, obj=None):
          return False     

@admin.register(models.DebianPackageVersionHistory)
class DebianPackageVersionHistory(admin.ModelAdmin):
     list_display = ('id','debian_package','package_version','created')
     
     
@admin.register(models.PythonPackageVulnerability)
class PythonPackageVulnerability(NestedModelAdmin):
     save_as = True
     list_display = ('id','package_name','vulnerability_json','updated','created')
     inlines = [PythonPackageVulnerabilityVersionInline,]
     readonly_fields=('package_name','vulnerability_json','updated','created')

     # def has_change_permission(self,request, obj=None):
     #      return False

     def has_delete_permission(self, request, obj=None):
          return False

@admin.register(models.DebianPackageVulnerability)
class DebianPackageVulnerability(NestedModelAdmin):
     save_as = True
     list_display = ('id','package_name','vulnerability_json','updated','created')
     inlines = [DebianPackageVulnerabilityVersionInline,]
     readonly_fields=('package_name','vulnerability_json','updated','created')

     # def has_change_permission(self,request, obj=None):
     #      return False

     def has_delete_permission(self, request, obj=None):
          return False          