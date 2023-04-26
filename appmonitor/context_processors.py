"""Context processors for the Django project."""


# Third-Party
from django import conf
from django import http

# Typing
from typing import Any


def variables(request):
    """Constructs a context dictionary to be passed to the templates.
    Args:
        request (http.HttpRequest): HTTP request object.
    Returns:
        dict[str, Any]: Context for the templates.
    """
    # Construct and return context
    return {
        "template_group": "dbcablack",
        "template_title": "App Monitoring",
        "app_build_url": conf.settings.DEV_APP_BUILD_URL,
        "GIT_COMMIT_HASH": conf.settings.GIT_COMMIT_HASH
    }