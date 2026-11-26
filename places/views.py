from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from accounts.models import UserProfile

from .forms import PlaceAccessibilityFormSet, PlaceForm
from .models import Place


def _user_role(user):
    return UserProfile.objects.filter(user=user).values_list(
        'role', flat=True
    ).first()


def _require_place_manager(user, place):
    if _can_manage_place(user, place):
        return

    raise PermissionDenied


def _can_manage_place(user, place):
    if not user.is_authenticated:
        return False

    role = _user_role(user)
    return role == 'admin' or (
        role == 'user' and place.created_by_id == user.pk
    )


def place_list(request):
    places = Place.objects.select_related('created_by').prefetch_related(
        'accessibility_features'
    )
    return render(request, 'places/place_list.html', {'places': places})


def place_detail(request, pk):
    place = get_object_or_404(
        Place.objects.select_related('created_by').prefetch_related(
            'accessibility_records__feature'
        ),
        pk=pk,
    )
    return render(request, 'places/place_detail.html', {
        'place': place,
        'can_manage': _can_manage_place(request.user, place),
    })


@login_required
@require_http_methods(['GET', 'POST'])
def place_create(request):
    role = _user_role(request.user)
    if role not in ('user', 'admin'):
        raise PermissionDenied

    place = Place()
    form = PlaceForm(request.POST or None, instance=place)
    formset = PlaceAccessibilityFormSet(request.POST or None, instance=place)

    if request.method == 'POST':
        form_is_valid = form.is_valid()
        formset_is_valid = formset.is_valid()

        if form_is_valid and formset_is_valid:
            with transaction.atomic():
                place = form.save(commit=False)
                place.created_by = request.user
                place.save()
                formset.instance = place
                formset.save()

            messages.success(request, 'Place created successfully.')
            return redirect('places:detail', pk=place.pk)

    return render(request, 'places/place_form.html', {
        'form': form,
        'formset': formset,
        'place': place,
    })


@login_required
@require_http_methods(['GET', 'POST'])
def place_update(request, pk):
    place = get_object_or_404(Place, pk=pk)
    _require_place_manager(request.user, place)

    form = PlaceForm(request.POST or None, instance=place)
    formset = PlaceAccessibilityFormSet(request.POST or None, instance=place)

    if request.method == 'POST':
        form_is_valid = form.is_valid()
        formset_is_valid = formset.is_valid()

        if form_is_valid and formset_is_valid:
            with transaction.atomic():
                form.save()
                formset.save()

            messages.success(request, 'Place updated successfully.')
            return redirect('places:detail', pk=place.pk)

    return render(request, 'places/place_form.html', {
        'form': form,
        'formset': formset,
        'place': place,
    })


@login_required
@require_http_methods(['GET', 'POST'])
def place_delete(request, pk):
    place = get_object_or_404(Place, pk=pk)
    _require_place_manager(request.user, place)

    if request.method == 'POST':
        place.delete()
        messages.success(request, 'Place deleted successfully.')
        return redirect('places:list')

    return render(request, 'places/place_confirm_delete.html', {'place': place})
