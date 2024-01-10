"""Context processors for the Django project."""


# Third-Party
from django import conf
from django import http
from appmonitor import models
from django.conf import settings
# Typing
from typing import Any


def variables(request):
    """Constructs a context dictionary to be passed to the templates.
    Args:
        request (http.HttpRequest): HTTP request object.
    Returns:
        dict[str, Any]: Context for the templates.
    """
    view_access = False
    edit_access = False

    view_access_groups = models.AccessGroup.objects.filter(active=True, access_type=1)
    view_access_groups_array = []
    for vag in view_access_groups:
        view_access_groups_array.append(vag.group_name)

    edit_access_groups = models.AccessGroup.objects.filter(active=True, access_type=2)
    edit_access_groups_array = []
    for eag in edit_access_groups:
        edit_access_groups_array.append(eag.group_name)

    user_groups = []
    for g in request.user.groups.all():
        user_groups.append(g.name)
    
    for ug in user_groups:
        print (ug)
        if ug in view_access_groups_array:
            view_access = True

    for ug in user_groups:
        if ug in edit_access_groups_array:
            edit_access = True

    # Construct and return context
    return {
        "template_group": "dbcablack",
        "template_title": "App Monitoring",
        "app_build_url": conf.settings.DEV_APP_BUILD_URL,
        "GIT_COMMIT_HASH": conf.settings.GIT_COMMIT_HASH,
        "user_groups" : user_groups,
        "view_access" : view_access,
        "edit_access" : edit_access,
        "DJANGO_SETTINGS" : settings
    }