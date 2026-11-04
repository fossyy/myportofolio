from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from rest_framework.permissions import BasePermission, SAFE_METHODS


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


class IsPortfolioOwnerOrEditorOrReadOnly(BasePermission):
    """Public reads, Editor updates, and owner-only create/delete."""

    def has_permission(self, request, view):
        # Let DRF return 405 for methods the view does not implement.
        if request.method not in getattr(view, "allowed_methods", ()):
            return True
        if request.method in SAFE_METHODS:
            return True
        if request.method in ("PUT", "PATCH"):
            return can_edit_content(request.user)
        if request.method in ("POST", "DELETE"):
            return request.user.is_authenticated and request.user.is_superuser
        return True
