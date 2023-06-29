# email
from wagov_utils.components.utils.email import TemplateEmailBase as WAGovUtilsTemplateEmailBase

class TestEmail(WAGovUtilsTemplateEmailBase):
    """Catalogue Entry Locked Email Abstraction."""
    subject = "Test Email"
    html_template = "appmonitor/email/test_email.html"
    txt_template = "appmonitor/email/test_email.txt"


class AppCheckList(WAGovUtilsTemplateEmailBase):
    """Catalogue Entry Locked Email Abstraction."""
    subject = "On call Applications Team IT Checks"
    html_template = "appmonitor/email/app_check_list.html"
    txt_template = "appmonitor/email/no_txt_support.txt"    