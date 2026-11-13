from django.shortcuts import render
from django.shortcuts import render,redirect
from django.contrib import messages

from django.contrib.auth import login as auth_login

from .forms import LoginForm
from .forms import RegistrationForm

# Create your views here.
def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Registration successful!')
            return redirect('login')
    else:
        form = RegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request = request, data=request.POST)

        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            return redirect('user_dashboard')

    else:
        form = LoginForm(request=request)

    return render(request, 'accounts/login.html', {'form': form})