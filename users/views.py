from django.shortcuts import render
from leads.models import Lead
from django.contrib.auth import login as login_func
from .forms import LoginForm, RegisterForm
from django.shortcuts import redirect
from django.contrib.auth import logout as logout_func

def homePage(request):
    return render(request, 'base/home.html')

def login(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login_func(request, user)
            return redirect('homePage') # Redirect to homePage which is the name of the URL for home
    else:
        form = LoginForm()
    return render(request, 'base/login.html', {'form': form})

def register(request):
    if request.method == 'POST':
        form = RegisterForm(data=request.POST)
        if form.is_valid():
            user = form.save()
            login_func(request, user)
            return redirect('homePage')
    else:
        form = RegisterForm()
    return render(request, 'base/register.html', {'form': form})


def logout(request):
    logout_func(request)
    return redirect('login')
