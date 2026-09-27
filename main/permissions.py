from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied


def can_edit_content(user):
    return user.is_authenticated and (
        user.is_superuser or user.groups.filter(name="Editor").exists()
    )


def owner_required(view):
    @wraps(view)
    def check_owner(request, *args, **kwargs):
        if not request.user.is_superuser:
            raise PermissionDenied
        return view(request, *args, **kwargs)

    return login_required(check_owner, login_url="/login/")


def editor_required(view):
    @wraps(view)
    def check_editor(request, *args, **kwargs):
        if not can_edit_content(request.user):
            raise PermissionDenied
        return view(request, *args, **kwargs)

    return login_required(check_editor, login_url="/login/")
