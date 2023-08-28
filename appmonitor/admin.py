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

@admin.register(models.ResponsibleGroup)
class ResponsibleGroup(admin.ModelAdmin):
     list_display = ('id','group_name','active')

@admin.register(models.ManualCheck)
class ManualCheck(admin.ModelAdmin):
     list_display = ('id','check_name','system_id','group_responsible','active')

@admin.register(models.NotificationEmail)
class ResponsibleGroup(admin.ModelAdmin):
     list_display = ('id','email','created')


class TicketFilterNotificationInline(admin.TabularInline):
    model = models.TicketFilterNotification
    extra = 0

@admin.register(models.TicketFilter)
class TicketFilter(admin.ModelAdmin):
     list_display = ('id','name','url','active')
     list_filter = ('active',)
     search_fields = ('id','name','url')
     inlines = [TicketFilterNotificationInline]


@admin.register(models.Tickets)
class Tickets(admin.ModelAdmin):
     list_display = ('id','ticket_reference_no','created')
