from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Prefetch

from accounts.models import UserProfile
from places.models import Place, PlaceAccessibility


def home(request):
    return render(request, 'dashboard/home.html')


def about(request):
    return render(request, 'dashboard/about.html')


@login_required
def user_dashboard(request):
    profile = UserProfile.objects.filter(user=request.user).first()

    if profile is None or profile.role not in ('user', 'admin'):
        raise PermissionDenied

    places = Place.objects.select_related('created_by').prefetch_related(
        Prefetch(
            'accessibility_records',
            queryset=PlaceAccessibility.objects.select_related('feature'),
        )
    )
    community_places = places.order_by('-created_at', '-pk')[:6]
    my_places = places.filter(created_by=request.user).order_by(
        '-created_at', '-pk'
    )[:6]

    display_name = request.user.first_name.strip() or request.user.username
    return render(request, 'dashboard/user_dashboard.html', {
        'community_places': community_places,
        'my_places': my_places,
        'display_name': display_name,
    })


@login_required
def admin_dashboard(request):
    profile = UserProfile.objects.filter(user=request.user).first()

    if profile is None or profile.role != 'admin':
        raise PermissionDenied

    return render(request, 'dashboard/admin_dashboard.html')
