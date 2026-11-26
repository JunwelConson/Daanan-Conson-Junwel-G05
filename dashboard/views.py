from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.core.exceptions import PermissionDenied

from accounts.models import UserProfile


def home(request):
    return render(request, 'dashboard/home.html')


def about(request):
    return render(request, 'dashboard/about.html')


@login_required
def user_dashboard(request):
    profile = UserProfile.objects.filter(user=request.user).first()

    if profile is None or profile.role != 'user':
        raise PermissionDenied

    return render(request, 'dashboard/user_dashboard.html')


@login_required
def admin_dashboard(request):
    profile = UserProfile.objects.filter(user=request.user).first()

    if profile is None or profile.role != 'admin':
        raise PermissionDenied

    return render(request, 'dashboard/admin_dashboard.html')
