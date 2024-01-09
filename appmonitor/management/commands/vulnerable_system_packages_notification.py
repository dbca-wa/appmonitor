from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth.models import Group
import datetime
from appmonitor import models
from appmonitor import utils
from appmonitor import email_templates
from django.conf import settings
import xlsxwriter
from hashlib import md5
import os
import sys

class Command(BaseCommand):
    help = 'Vunerable System Packages Notifcation Email.  Will attach an excel document.'

    def handle(self, *args, **options):
            print ("Builing a list of Vunerable System Packages")

            for rg in models.ResponsibleGroup.objects.all():
                print (rg)
                date_string = datetime.datetime.now().astimezone().strftime('%Y-%m-%d')
                date_string_au = datetime.datetime.now().astimezone().strftime('%d-%m-%Y')

                platform_packages_info_obj = models.PythonPackage.objects.filter(active=True,vulnerability_total__gt=0,platform__group_responsible=rg)
                if platform_packages_info_obj.count() > 0:
                    platform_packages_info_array = []
                    for ppi in platform_packages_info_obj:
                        row = []
                        row.append(ppi.id)
                        row.append(ppi.platform.system_name)
                        row.append(ppi.package_name)
                        row.append(ppi.current_package_version)
                        row.append(ppi.vulnerability_total)
                        row.append(ppi.platform.group_responsible.group_name)
                        platform_packages_info_array.append(row)


                    platform_packages_info_tuple = tuple(platform_packages_info_array)
                    plaintext = str(datetime.datetime.now()) # Must be a string, doesn't need to have utf-8 encoding
                    md5hash = md5(plaintext.encode('utf-8')).hexdigest()
                    if os.path.isdir(str(settings.BASE_DIR)+'/tmp/') is False:
                        os.makedirs(str(settings.BASE_DIR)+'/tmp/')
                    excel_file = str(settings.BASE_DIR)+'/tmp/'+md5hash+'.xlsx'
                    workbook = xlsxwriter.Workbook(excel_file)
                    print (md5hash)
                    # The workbook object is then used to add new 
                    # worksheet via the add_worksheet() method.
                    worksheet = workbook.add_worksheet("System Advisory {}".format(date_string_au))
                    
                    # Start from the first cell. Rows and
                    # columns are zero indexed.
                    format = workbook.add_format()

                    format.set_pattern(1)
                    format.set_bg_color('black')
                    format.set_font_color('white') 
                    format.set_bold()
                    col = 0 
                    row = 0
                    worksheet.write(row, col, "PACKAGE ID", format)
                    worksheet.set_column(0, 0, 12)
                    worksheet.write(row, col + 1, "SYSTEM NAME",format)
                    worksheet.set_column(1, 1, 30)
                    worksheet.write(row, col + 2, "PACKAGE NAME",format)
                    worksheet.set_column(2, 2, 30)
                    worksheet.write(row, col + 3, "PACKAGE VERSION",format)
                    worksheet.set_column(3, 3, 20)
                    worksheet.write(row, col + 4, "VULNERABILITY TOTAL",format)
                    worksheet.set_column(4, 4, 20)
                    worksheet.write(row, col + 5, "GROUP RESPONSIBLE",format)
                    worksheet.set_column(5, 5, 60)
                    #worksheet.set_column(row, col + 5, 100)
                    row += 1
                    
                    # Iterate over the data and write it out row by row.
                    for id, system_name, package_name, current_package_version, vulnerability_total, group_responsible in (platform_packages_info_tuple):
                        worksheet.write(row, col, id)
                        worksheet.write(row, col + 1, system_name)
                        worksheet.write(row, col + 2, package_name)
                        worksheet.write(row, col + 3, current_package_version)
                        worksheet.write(row, col + 4, vulnerability_total)
                        worksheet.write(row, col + 5, group_responsible)
                        
                        # worksheet.write(row, col + 5, package_name)

                        row += 1
                            
                    # Finally, close the Excel file
                    # via the close() method.
                    workbook.close()

                    
                    file_buffer = None
                    with open(excel_file, 'rb') as f:
                        file_buffer = f.read()                    
                                    
                    t = email_templates.OutstandingAdvisory()
                    t.subject = "Outstanding Advisory for "+rg.group_name
                    to_addresses=[]
                    for notification in models.ResponsibleGroupOutstandingAdvisoryEmail.objects.filter(responsible_group=rg):
                        print ("Preparing to "+notification.email)
                        to_addresses.append(notification.email)
                    t.send(to_addresses=to_addresses, context={"settings": settings, 'rg': rg}, headers={"Reply-To": settings.IT_CHECKS_REPLY_TO_EMAIL},attachments=[('Outstanding Systems Advisory for {} on {}.xlsx'.format(str(rg.group_name),date_string_au), file_buffer, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')])        
            

