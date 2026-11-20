from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout

from .forms import LoginForm, RegistrationForm, ProfileUpdateForm
from .models import UserProfile
from django.contrib.auth.decorators import login_required



def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)

        if form.is_valid():
            user = form.save()
            UserProfile.objects.create(user=user)

            messages.success(request, 'Registration successful!')
            return redirect('login')
    else:
        form = RegistrationForm()

    return render(request, 'accounts/register.html', {'form': form})


def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request=request, data=request.POST)

        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)

            profile = UserProfile.objects.filter(user=user).first()

            if profile is None:
                profile = UserProfile.objects.create(user=user)

            if profile.role == 'admin':
                return redirect('admin_dashboard')

            return redirect('user_dashboard')

    else:
        form = LoginForm(request=request)

    return render(request, 'accounts/login.html', {'form': form})


def user_logout(request):
    logout(request)
    messages.success(request, 'You have successfully logged out.')
    return redirect('home')


@login_required
def profile(request):
    if request.method == 'POST':
        form = ProfileUpdateForm(
            request.POST,
            instance=request.user
        )

        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('profile')

    else:
        form = ProfileUpdateForm(instance=request.user)

    user_profile = UserProfile.objects.get(user=request.user)

    return render(request, 'accounts/profile.html', {
        'form': form,
        'user_profile': user_profile
    })
