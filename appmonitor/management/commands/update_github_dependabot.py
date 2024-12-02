from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth.models import Group
from django.conf import settings
import datetime
import requests
from appmonitor import models

class Command(BaseCommand):
    help = 'Connect to github and pull a list of dependabot alerts.'

    def handle(self, *args, **options):
        print ("Updating Dependabot Alerts")

        ghsa_id_hashses = []
        platforms = models.Platform.objects.filter(active=True)
        for p in platforms:

            if len(p.git_repo_name) > 0:
                resp = requests.get("https://api.github.com/repos/dbca-wa/{}/dependabot/alerts".format(p.git_repo_name),headers={"Accept": "application/vnd.github+json", "Authorization": "Bearer "+settings.GIT_API_TOKEN, "X-GitHub-Api-Version":"2022-11-28"})
                jsonresp = resp.json()
                total_count = 0
                for jr in jsonresp:
                    total_count = total_count + 1
                    ghsa_id_hashses.append(jr["security_advisory"]["ghsa_id"])
                    print (jr['number'])
                    print (jr['state'])
                    # print (jr["security_advisory"]["ghsa_id"])
                    # print (jr["security_advisory"]["vulnerabilities"][0]["package"]["ecosystem"])
                    # print (jr["security_advisory"]["vulnerabilities"][0]["package"]["name"])
                    # print (jr["security_advisory"]["vulnerabilities"][0]["severity"])
                    # print (jr["security_advisory"]["cve_id"])
                    
                    if models.PlatformDependaBotAdvisory.objects.filter(platform=p, number=jr['number']).count() > 0:
                        print ("Updating {}".format(jr["security_advisory"]["ghsa_id"]))
                        pdba = models.PlatformDependaBotAdvisory.objects.get(platform=p, number=jr['number'])
                        pdba.state = jr['state']
                        pdba.number = jr['number']
                        pdba.ecosystem = jr["security_advisory"]["vulnerabilities"][0]["package"]["ecosystem"]
                        pdba.package_name = jr["security_advisory"]["vulnerabilities"][0]["package"]["name"]
                        pdba.severity = jr["security_advisory"]["vulnerabilities"][0]["severity"]
                        pdba.cve_id = jr["security_advisory"]["cve_id"]
                        pdba.save()
                        
                    else:  
                        print ("Creating {}".format(jr["security_advisory"]["ghsa_id"]))                      
                        models.PlatformDependaBotAdvisory.objects.create(
                            platform=p,
                            state = jr['state'],
                            number = jr['number'],
                            ghsa_id=jr["security_advisory"]["ghsa_id"],
                            ecosystem=jr["security_advisory"]["vulnerabilities"][0]["package"]["ecosystem"],
                            package_name=jr["security_advisory"]["vulnerabilities"][0]["package"]["name"],
                            severity= jr["security_advisory"]["vulnerabilities"][0]["severity"],
                            cve_id = jr["security_advisory"]["cve_id"],
                        )
                # all_pdba = models.PlatformDependaBotAdvisory.objects.all().delete() 
                all_pdba = models.PlatformDependaBotAdvisory.objects.filter(platform=p) 
                for a in all_pdba:
                    if a.ghsa_id not in ghsa_id_hashses:
                        print ("Deleting: {}".format(a.ghsa_id))
                        models.PlatformDependaBotAdvisory.objects.filter(ghsa_id=a.ghsa_id).delete()
                    #[0]["package"]
                # curl -L -H "Accept: application/vnd.github+json" -H "Authorization: Bearer <git_api_token>" -H "X-GitHub-Api-Version: 2022-11-28" https://api.github.com/repos/dbca-wa/gokart-sss-django/dependabot/alerts |
                platform_dependabot_total = models.PlatformDependaBotAdvisory.objects.filter(platform=p,state='open').count()
                p.dependabot_vulnerability_total=platform_dependabot_total
                p.save()


        print (total_count)
