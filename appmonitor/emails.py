"""Kaartdijin Boodja Emails Django Application Functionality."""


# Standard
import logging

# Third-Party
from django import conf
from django import template
from django.core import mail
from django.template import loader
from django.utils import html

# Typing
from typing import Any, Optional, Union

# email
from wagov_utils.components.utils.email import TemplateEmailBase as WAGovUtilsTemplateEmailBase

# Logging
log = logging.getLogger(__name__)

class TemplateEmailBase(WAGovUtilsTemplateEmailBase):

    def send_to(
        self,
        *users: Any,
        context: Optional[dict[str, Any]] = None,
    ) -> None:
        """Sends an email individually to many users.

        Args:
            *users (Any): Possible users to send the email to.
            context (Optional[dict[str, Any]]): Context for the template.
        """
        # Filter the supplied users to only objects that have an `email`
        # attribute, and cast them to a set to eliminate any duplicated
        filtered_emails = set(u.email for u in users if hasattr(u, "email"))
        # Loop through users
        for email in filtered_emails:
            # Send the email!
            self.send(email, context=context)



