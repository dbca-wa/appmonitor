# Third-Party
from django import http
from django import shortcuts
from django.views.generic import base
from django.contrib import messages
from datetime import datetime
from django.utils.timezone import utc

# Typing
from typing import Any
from appmonitor import models

class HomePage(base.TemplateView):
    """Home page view."""

    # Template name
    template_name = "appmonitor/home.html"

    def get(self, request: http.HttpRequest, *args: Any, **kwargs: Any) -> http.HttpResponse:
        """Provides the GET request endpoint for the HomePage view.
        Args:
            request (http.HttpRequest): The incoming HTTP request.
            *args (Any): Extra positional arguments.
            **kwargs (Any): Extra keyword arguments.
        Returns:
            http.HttpResponse: The rendered template response.
        """
        # Construct Context
        context: dict[str, Any] = {}
        context['request'] = request
        context['current_time'] = datetime.today
        now = datetime.utcnow().replace(tzinfo=utc)
       
        mjl = models.MonitorJobLog.objects.all().order_by('-id').first()
        if mjl is not None:
            if mjl.started:
                timediff = now - mjl.started
                context['last_job_run'] = mjl.started
                context['time_differnce_last_job'] = int(timediff.total_seconds() / 60)
            else:
                context['last_job_run'] = "No last run date time"
                context['time_differnce_last_job'] = 1000
        else:
            context['last_job_run'] = "No last run date time"
            context['time_differnce_last_job'] = 1000
            
        # Render Template and Return
        return shortcuts.render(request, self.template_name, context)
    

class MonitorHistory(base.TemplateView):
    """Home page view."""

    # Template name
    template_name = "appmonitor/monitor_history.html"

    def get(self, request: http.HttpRequest, *args: Any, **kwargs: Any) -> http.HttpResponse:
        """Provides the GET request endpoint for the HomePage view.
        Args:
            request (http.HttpRequest): The incoming HTTP request.
            *args (Any): Extra positional arguments.
            **kwargs (Any): Extra keyword arguments.
        Returns:
            http.HttpResponse: The rendered template response.
        """
        # Construct Context
        context: dict[str, Any] = {}
        monitor_history = []
        monitor_id = self.kwargs['pk']
        monitor_history_obj = models.MonitorHistory.objects.filter(monitor_id=monitor_id).order_by('-created')
        
        for mh in monitor_history_obj:        
            monitor_history.append({'id': mh.id, 'monitor_id': mh.monitor.id, 'status': mh.status, 'last_changed': mh.created, 'mon_type': mh.monitor.get_mon_type_display(),})
        context['monitor_history'] = monitor_history
        context['request'] = request
        # Render Template and Return
        return shortcuts.render(request, self.template_name, context)


class MonitorHistoryRecord(base.TemplateView):
    """Home page view."""

    # Template name
    template_name = "appmonitor/monitor_history_record.html"

    def get(self, request: http.HttpRequest, *args: Any, **kwargs: Any) -> http.HttpResponse:
        """Provides the GET request endpoint for the HomePage view.
        Args:
            request (http.HttpRequest): The incoming HTTP request.
            *args (Any): Extra positional arguments.
            **kwargs (Any): Extra keyword arguments.
        Returns:
            http.HttpResponse: The rendered template response.
        """
        # Construct Context
        context: dict[str, Any] = {}
        monitor_id = self.kwargs['pk']
        monitor_history_id = self.kwargs['monitor_history_id']
        monitor_history_obj = None
        
        try:                    
            monitor_history_obj = models.MonitorHistory.objects.get(monitor_id=monitor_id,id=monitor_history_id)
        except Exception as e:
            messages.add_message(request, messages.ERROR, str(e))
            print (e)

        context['monitor_history_obj'] = monitor_history_obj
        context['request'] = request
        
        # Render Template and Return
        return shortcuts.render(request, self.template_name, context)            