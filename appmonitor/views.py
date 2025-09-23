# Third-Party
from django import http
from django import shortcuts
from django.views.generic import base
from django.contrib import messages
from datetime import datetime
# from django.utils.timezone import utc
from datetime import timezone as datetime_timezone

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
        now = datetime.utcnow().replace(tzinfo=datetime_timezone.utc)
        responsible_group = models.ResponsibleGroup.objects.filter(active=True)
        context['responsible_group'] = responsible_group    
        context['mon_types'] = models.Monitor.MON_TYPE
        context['check_operators'] = models.Monitor.CHECK_OPERATOR
        context['response_types_list'] = models.Monitor.RESPONSE_TYPE
        context['db_type'] = models.Monitor.DB_TYPE
        
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
        # Construct Context
        context: dict[str, Any] = {}
        monitor_history = []
        monitor_id = self.kwargs['pk']
        monitor = models.Monitor.objects.get(id=monitor_id)
        monitor_history_obj = models.MonitorHistory.objects.filter(monitor_id=monitor_id).order_by('-created')
        
        for mh in monitor_history_obj:        
            monitor_history.append({'id': mh.id, 'monitor_id': mh.monitor.id, 'status': mh.status, 'last_changed': mh.created, 'mon_type': mh.monitor.get_mon_type_display(),})
        context['monitor_history'] = monitor_history
        context['monitor'] = monitor
        context['request'] = request
        # Render Template and Return
        return shortcuts.render(request, self.template_name, context)


class MonitorHistoryRecord(base.TemplateView):
    """Home page view."""

    # Template name
    template_name = "appmonitor/monitor_history_record.html"

    def get(self, request: http.HttpRequest, *args: Any, **kwargs: Any) -> http.HttpResponse:
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
    

class PlatformStatus(base.TemplateView):
    """Home page view."""

    # Template name
    template_name = "appmonitor/platform_status.html"

    def get(self, request: http.HttpRequest, *args: Any, **kwargs: Any) -> http.HttpResponse:
        # Construct Context
        context: dict[str, Any] = {}
        
        if request.user.is_authenticated:
            try:
                responsible_group = models.ResponsibleGroup.objects.filter(active=True)
                context['responsible_group'] = responsible_group
            except Exception as e:
                messages.add_message(request, messages.ERROR, str(e))
                print (e)
        #   id = self.kwargs['pk']
        # Render Template and Return
        return shortcuts.render(request, self.template_name, context)


class PlatformView(base.TemplateView):
    """VIew Platform System Information"""

    # Template name
    template_name = "appmonitor/platform_view.html"

    def get(self, request: http.HttpRequest, *args: Any, **kwargs: Any) -> http.HttpResponse:
        # Construct Context
        context: dict[str, Any] = {}
        platform_id = self.kwargs['pk']
        ecosystem = self.kwargs['ecosystem']
        platform_obj = None

        if request.user.is_authenticated:
            only_vulnerable = 'false'
            try:
                only_vulnerable = request.GET.get('only_vulnerable','false')
                python_packages_obj = []
                platform_obj = models.Platform.objects.get(id=platform_id)
                if ecosystem == 'python-packages':
                    if only_vulnerable == 'true':
                        python_packages_obj = models.PythonPackage.objects.filter(platform_id=platform_obj.id,vulnerability_total__gt=0, active=True)
                    else:
                        python_packages_obj = models.PythonPackage.objects.filter(platform_id=platform_obj.id,active=True)                
                elif ecosystem == 'debian-packages':
                    if only_vulnerable == 'true':
                        python_packages_obj = models.DebianPackage.objects.filter(platform_id=platform_obj.id,vulnerability_total__gt=0, active=True)
                    else:
                        python_packages_obj = models.DebianPackage.objects.filter(platform_id=platform_obj.id,active=True)   
                elif ecosystem == 'node-packages':
                    if only_vulnerable == 'true':
                        python_packages_obj = models.NpmPackage.objects.filter(platform_id=platform_obj.id,vulnerability_total__gt=0, active=True)
                    else:
                        python_packages_obj = models.NpmPackage.objects.filter(platform_id=platform_obj.id,active=True)                                                      


            except Exception as e:
                messages.add_message(request, messages.ERROR, str(e))
                print (e)

            context['platform_obj'] = platform_obj
            context['python_packages_obj'] = python_packages_obj
            context['request'] = request
            context['only_vulnerable'] = only_vulnerable
            context['ecosystem'] = ecosystem
        
        # Render Template and Return
        return shortcuts.render(request, self.template_name, context)            

class PlatformDependaBotPackageView(base.TemplateView):
    """VIew Platform System Information"""

    # Template name
    template_name = "appmonitor/platform_dependabot_package_view.html"

    def get(self, request: http.HttpRequest, *args: Any, **kwargs: Any) -> http.HttpResponse:
        # Construct Context
        context: dict[str, Any] = {}
        platform_id = self.kwargs['pk']
        state = request.GET.get('state','open')
        
        platform_obj = None
        python_packages_versions_obj = None
        platform_dependabot_obj = None

        if request.user.is_authenticated:
            try:      
                python_packages_versions_array = []
                platform_dependabot_array=[]
                platform_obj = models.Platform.objects.get(id=platform_id)
                platform_dependabot_obj_open_count = models.PlatformDependaBotAdvisory.objects.filter(platform=platform_obj,state='open').count()
                platform_dependabot_obj_fixed_count = models.PlatformDependaBotAdvisory.objects.filter(platform=platform_obj,state='fixed').count()
                platform_dependabot_obj = models.PlatformDependaBotAdvisory.objects.filter(platform=platform_obj,state=state)
                           
                for pdb in platform_dependabot_obj:
                    row = {}
                    row['number'] = pdb.number
                    row['state'] = pdb.state
                    row['package_name'] = pdb.package_name
                    row['ecosystem'] = pdb.ecosystem
                    row['severity'] = pdb.severity
                    row['cve_id'] = pdb.cve_id
                    row['created'] = pdb.created.astimezone().strftime('%d/%m/%Y %H:%M %p')
                    row['updated'] = pdb.updated.astimezone().strftime('%d/%m/%Y %H:%M %p')
                    platform_dependabot_array.append(row)

            except Exception as e:
                messages.add_message(request, messages.ERROR, str(e))
                print (e)

            context['platform_obj'] = platform_obj
            context['platform_dependabot_array'] = platform_dependabot_array
            context['platform_dependabot_obj_open_count'] = platform_dependabot_obj_open_count
            context['platform_dependabot_obj_fixed_count'] = platform_dependabot_obj_fixed_count
            context['state'] = state
        #     context['python_package_obj'] = python_package_obj
        #     context['python_packages_versions_array'] = python_packages_versions_array
        #     context['python_packages_versions_obj'] = python_packages_versions_obj
            context['request'] = request
        
        # Render Template and Return
        return shortcuts.render(request, self.template_name, context)  


class PlatformPackageView(base.TemplateView):
    """VIew Platform System Information"""

    # Template name
    template_name = "appmonitor/platform_package_view.html"

    def get(self, request: http.HttpRequest, *args: Any, **kwargs: Any) -> http.HttpResponse:
        # Construct Context
        context: dict[str, Any] = {}
        platform_id = self.kwargs['pk']
        python_package_id = self.kwargs['package_pk']
        ecosystem = self.kwargs['ecosystem']
        platform_obj = None
        python_packages_versions_obj = None
        python_package_obj={}
        if request.user.is_authenticated:
            try:      
                python_packages_versions_array = []
                platform_obj = models.Platform.objects.get(id=platform_id)
                if ecosystem == 'python':
                    python_package_obj = models.PythonPackage.objects.get(platform_id=platform_obj.id, id=python_package_id)
                    python_packages_versions_obj = models.PythonPackageVersionHistory.objects.filter(python_package=python_package_id)

                    python_package_vunerability_obj_id = None
                    python_package_vunerability_obj = None
                    if models.PythonPackageVulnerability.objects.filter(package_name=python_package_obj.package_name).count() > 0:
                        python_package_vunerability_obj = models.PythonPackageVulnerability.objects.get(package_name=python_package_obj.package_name)
                        python_package_vunerability_obj_id = python_package_vunerability_obj.id                
                elif ecosystem == 'debian':
                    python_package_obj = models.DebianPackage.objects.get(platform_id=platform_obj.id, id=python_package_id)
                    python_packages_versions_obj = models.DebianPackageVersionHistory.objects.filter(debian_package=python_package_id)

                    python_package_vunerability_obj_id = None
                    python_package_vunerability_obj = None
                    if models.DebianPackageVulnerability.objects.filter(package_name=python_package_obj.package_name).count() > 0:
                        python_package_vunerability_obj = models.DebianPackageVulnerability.objects.get(package_name=python_package_obj.package_name)
                        python_package_vunerability_obj_id = python_package_vunerability_obj.id         

                elif ecosystem == 'node':
                    python_package_obj = models.NpmPackage.objects.get(platform_id=platform_obj.id, id=python_package_id)
                    python_packages_versions_obj = models.NpmPackageVersionHistory.objects.filter(npm_package=python_package_id)

                    python_package_vunerability_obj_id = None
                    npm_package_vunerability_obj = None
                    
                    if models.NpmPackageVulnerability.objects.filter(package_name=python_package_obj.package_name).count() > 0:                        
                        npm_package_vunerability_obj = models.NpmPackageVulnerability.objects.get(package_name=python_package_obj.package_name)
                        python_package_vunerability_obj_id = npm_package_vunerability_obj.id                                                    
                    # work required to compile node packages data
                    pass
                    
                for ppv in python_packages_versions_obj:
                    row = {}
                    
                    row['package_version'] = ppv.package_version
                    row['created'] = ppv.created.astimezone().strftime('%d/%m/%Y %H:%M %p')
                    row['ppv_id'] = python_package_vunerability_obj_id
                    row['ppvv_id'] = None

                    if ecosystem == 'python':
                        row['package_name'] = ppv.python_package
                        python_package_vunerability_version_advisory_information_obj = 0
                        if python_package_vunerability_obj:
                            python_package_vunerability_version_obj = models.PythonPackageVulnerabilityVersion.objects.filter(python_package=python_package_vunerability_obj,package_version=ppv.package_version)
                                        
                            if python_package_vunerability_version_obj.count() > 0:
                                python_package_vunerability_version_advisory_information_obj = models.PythonPackageVulnerabilityVersionAdvisoryInformation.objects.filter(package_version=python_package_vunerability_version_obj[0]).count()

                                row['ppvv_id'] = python_package_vunerability_version_obj[0].id
                        row['vulnerability_total'] = python_package_vunerability_version_advisory_information_obj
                    elif ecosystem == 'debian':
                        
                        row['package_name'] = ppv.debian_package
                        debian_package_vunerability_version_advisory_information_obj = 0
                        if python_package_vunerability_obj:
                            debian_package_vunerability_version_obj = models.DebianPackageVulnerabilityVersion.objects.filter(debian_package=python_package_vunerability_obj,package_version=ppv.package_version)
                                        
                            if debian_package_vunerability_version_obj.count() > 0:
                                debian_package_vunerability_version_advisory_information_obj = models.DebianPackageVulnerabilityVersionAdvisoryInformation.objects.filter(package_version=debian_package_vunerability_version_obj[0]).count()

                                row['ppvv_id'] = debian_package_vunerability_version_obj[0].id
                        
                        row['vulnerability_total'] = debian_package_vunerability_version_advisory_information_obj
                    elif ecosystem == 'node':

                        row['package_name'] = ppv.npm_package
                        npm_package_vunerability_version_advisory_information_obj = 0
                        if npm_package_vunerability_obj:
                            print ("NN1")
                            npm_package_vunerability_version_obj = models.NpmPackageVulnerabilityVersion.objects.filter(npm_package=npm_package_vunerability_obj,package_version=ppv.package_version)
                                        
                            if npm_package_vunerability_version_obj.count() > 0:
                                print ("NN2")
                                npm_package_vunerability_version_advisory_information_obj = models.NpmPackageVulnerabilityVersionAdvisoryInformation.objects.filter(package_version=npm_package_vunerability_version_obj[0]).count()
                                row['ppvv_id'] = npm_package_vunerability_version_obj[0].id
                                print ("NN3")                                
                        
                        row['vulnerability_total'] = npm_package_vunerability_version_advisory_information_obj

                        # work required to compile node packages data
                        # row['vulnerability_total'] = 0
                        # row['ppvv_id'] = None
                    
                    python_packages_versions_array.append(row)
            except Exception as e:
                messages.add_message(request, messages.ERROR, str(e))
                print (e)

            context['platform_obj'] = platform_obj
            context['python_package_obj'] = python_package_obj
            context['python_packages_versions_array'] = python_packages_versions_array
            context['python_packages_versions_obj'] = python_packages_versions_obj
            context['ecosystem'] = ecosystem
            context['request'] = request
        
        # Render Template and Return
        return shortcuts.render(request, self.template_name, context)            

class PackageAdvisoryView(base.TemplateView):
    """VIew Platform System Information"""

    # Template name
    template_name = "appmonitor/python_package_advisory_view.html"

    def get(self, request: http.HttpRequest, *args: Any, **kwargs: Any) -> http.HttpResponse:
        # Construct Context
        context: dict[str, Any] = {}
        package_id = self.kwargs['pk']
        package_version_id = self.kwargs['version_pk']
        ecosystem = self.kwargs['ecosystem']
        python_package_vunerability_obj = None
        python_package_vunerability_version_obj = None
        # platform_obj = None
        # python_packages_versions_obj = None
        if request.user.is_authenticated:
            try:      
                python_packages_versions_array = []                
                package_advisory = []
                vunerability_total = 0

                if ecosystem == 'python':
                    if models.PythonPackageVulnerability.objects.filter(id=package_id).count() > 0:
                        python_package_vunerability_obj = models.PythonPackageVulnerability.objects.get(id=package_id)

                        python_package_vunerability_version_obj = models.PythonPackageVulnerabilityVersion.objects.get(python_package=python_package_vunerability_obj,id=package_version_id)
                        python_package_vunerability_version_advisory_information_obj = models.PythonPackageVulnerabilityVersionAdvisoryInformation.objects.filter(package_version=python_package_vunerability_version_obj)
                        
                        vunerability_total = python_package_vunerability_version_advisory_information_obj.count()
                        for av in python_package_vunerability_version_advisory_information_obj:
                            row = {}

                            row['advisory'] = av.advisory
                            row['cve'] = av.cve
                            row["baseScore"] = av.baseScore 
                            row["baseSeverity"] = av.baseSeverity
                            row['package_version'] = av.package_version.package_version
                            row['created'] = av.created.astimezone().strftime('%d/%m/%Y %H:%M %p')

                            package_advisory.append(row)
                elif ecosystem == 'debian':
                    if models.DebianPackageVulnerability.objects.filter(id=package_id).count() > 0:
                        debian_package_vunerability_obj = models.DebianPackageVulnerability.objects.get(id=package_id)

                        debian_package_vunerability_version_obj = models.DebianPackageVulnerabilityVersion.objects.get(debian_package=debian_package_vunerability_obj,id=package_version_id)
                        debian_package_vunerability_version_advisory_information_obj = models.DebianPackageVulnerabilityVersionAdvisoryInformation.objects.filter(package_version=debian_package_vunerability_version_obj)
                        
                        vunerability_total = debian_package_vunerability_version_advisory_information_obj.count()
                        for av in debian_package_vunerability_version_advisory_information_obj:
                            row = {}

                            row['advisory'] = av.advisory
                            row['cve'] = av.cve
                            row["baseScore"] = av.baseScore 
                            row["baseSeverity"] = av.baseSeverity
                            row['package_version'] = av.package_version.package_version
                            row['created'] = av.created.astimezone().strftime('%d/%m/%Y %H:%M %p')

                            package_advisory.append(row)                    

            except Exception as e:
                messages.add_message(request, messages.ERROR, str(e))
                print (e)

            context['python_package_vunerability_obj'] = python_package_vunerability_obj
            context['python_package_vunerability_version_obj'] = python_package_vunerability_version_obj
            context['python_package_advisory'] = package_advisory
            context['request'] = request
            context['vunerability_total'] = vunerability_total
        
        # Render Template and Return
        return shortcuts.render(request, self.template_name, context)  


class PackagesStatus(base.TemplateView):
    """Home page view."""

    # Template name
    template_name = "appmonitor/packages_status.html"

    def get(self, request: http.HttpRequest, *args: Any, **kwargs: Any) -> http.HttpResponse:
        # Construct Context
        context: dict[str, Any] = {}
        #id = self.kwargs['pk']
        # Render Template and Return
        return shortcuts.render(request, self.template_name, context)



    