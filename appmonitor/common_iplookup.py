from appmonitor import models
import ipaddress

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

# def api_allow(clientip,api_id):
#     allow = False
#     if models.APIService.objects.filter(id=api_id,enabled=True).count() > 0:
#         api = models.APIService.objects.filter(id=api_id)[0]
#         if api.network_restriction_enabled is True:
#             allowed_ips = api.allowed_ips.splitlines()
#             for line in allowed_ips:
#                 if ipaddress.ip_address(clientip) in ipaddress.ip_network(line):
#                     allow = True
#         else:
#              allow = True
#     return allow
