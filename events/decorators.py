from django.shortcuts import redirect
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import user_passes_test

def group_required(group_name):
    def in_group(u):
        if not u.is_authenticated:
            return False
        return u.groups.filter(name=group_name).exists() or u.is_superuser
    return user_passes_test(in_group, login_url="/login/")

def groups_required(*group_names):
    def _check(u):
        if not u.is_authenticated:
            return False
        if u.is_superuser:
            return True
        return u.groups.filter(name__in=group_names).exists()
    return user_passes_test(_check, login_url="/login/")