from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth.models import Group
from django.conf import settings
import datetime
import requests
from appmonitor import models
from django.core.cache import cache

class Command(BaseCommand):
    help = 'Connect to mitre CVE database'

    def handle(self, *args, **options):
        print ("Updating mitre CVE")

        ppvia = models.PythonPackageVulnerabilityVersionAdvisoryInformation.objects.all().order_by("-id")
        for p in ppvia:

            if len(p.cve) > 0:
                print (p.cve)
                cve_url = "https://cveawg.mitre.org/api/cve/{}".format(p.cve)
                cve_url_cache = cache.get(cve_url)
                data_resp = {}
                if cve_url_cache is None:
                    resp = requests.get(cve_url)
                    status_code = resp.status_code
                    data_resp = {"status_code": status_code, "content": {}}

                    
                    if resp.status_code == 200:
                        content = resp.json()
                        data_resp["content"] = content

                    cache.set(cve_url, data_resp,  86400)   
                else:                    
                    data_resp = cve_url_cache
                    
                if data_resp["status_code"] == 200:
                    jsonresp = data_resp["content"]
                    #print (jsonresp)
                    total_count = 0
                    
                    total_count = total_count + 1
                    if "metrics" in jsonresp["containers"]["cna"]:
                        # print (jsonresp["containers"]["cna"]["metrics"].keys())
                        # print (jsonresp["containers"]["cna"]["metrics"].keys()[0])
                        print (list(jsonresp["containers"]["cna"]["metrics"][0].keys())[0])
                        baseSeverity = jsonresp["containers"]["cna"]["metrics"][0][list(jsonresp["containers"]["cna"]["metrics"][0].keys())[0]]["baseSeverity"]
                        baseScore = jsonresp["containers"]["cna"]["metrics"][0][list(jsonresp["containers"]["cna"]["metrics"][0].keys())[0]]["baseScore"]
                        
                        print (baseSeverity)
                        print (baseScore)

                        p.baseSeverity = baseSeverity
                        p.baseScore = float(baseScore)
                        p.save()

        print (total_count)
