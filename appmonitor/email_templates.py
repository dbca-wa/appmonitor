# email
from wagov_utils.components.utils.email import TemplateEmailBase as WAGovUtilsTemplateEmailBase

class TestEmail(WAGovUtilsTemplateEmailBase):
    """Test Email."""
    subject = "Test Email"
    html_template = "appmonitor/email/test_email.html"
    txt_template = "appmonitor/email/test_email.txt"


class AppCheckList(WAGovUtilsTemplateEmailBase):
    """On call IT checks."""
    subject = "On call Applications Team IT Checks"
    html_template = "appmonitor/email/app_check_list.html"
    txt_template = "appmonitor/email/no_txt_support.txt"    


class MonitorSensorAlert(WAGovUtilsTemplateEmailBase):
    """Monitor Sensor Alert Changes"""
    subject = "Monitor Sensor Alert Changes"
    html_template = "appmonitor/email/monitor_sensor_alert.html"
    txt_template = "appmonitor/email/monitor_sensor_alert.txt"   

class TicketList(WAGovUtilsTemplateEmailBase):
    """Tickets Outstanding"""
    subject = "Tickets Outstanding"
    html_template = "appmonitor/email/tickets_outstanding.html"
    txt_template = "appmonitor/email/tickets_outstanding.txt"        


class TicketNew(WAGovUtilsTemplateEmailBase):
    """New Ticket."""
    subject = "New Ticket"
    html_template = "appmonitor/email/ticket_new.html"
    txt_template = "appmonitor/email/ticket_new.txt"      

class TicketUpdated(WAGovUtilsTemplateEmailBase):
    """Updated Ticket Email."""
    subject = "Updated Ticket Email"
    html_template = "appmonitor/email/ticket_updated.html"
    txt_template = "appmonitor/email/ticket_updated.txt"          


class NewAdvisory(WAGovUtilsTemplateEmailBase):
    """New Advisory."""
    subject = "New Advisory"
    html_template = "appmonitor/email/advisory_new.html"
    txt_template = "appmonitor/email/advisory_new.txt"      

class OutstandingAdvisory(WAGovUtilsTemplateEmailBase):
    """Outstanding Advisory."""
    subject = "Outstanding Advisory"
    html_template = "appmonitor/email/advisory_outstanding.html"
    txt_template = "appmonitor/email/advisory_outstanding.txt"      


class SystemError(WAGovUtilsTemplateEmailBase):
    """New Advisory."""
    subject = "New Advisory"
    html_template = "appmonitor/email/system_error.html"
    txt_template = "appmonitor/email/system_error.txt"       