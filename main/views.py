
# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.http import HttpResponseRedirect

# Vista para el login
def user_login(request):
    if request.user.is_authenticated:
        return redirect('index')
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect('index')
        else:
            messages.error(request, "Invalid username or password.")
    
    else:
        form = AuthenticationForm()
    
    return render(request, 'main/login.html', {'form': form})

# Vista para el index (restringida a usuarios logueados)
@login_required
def index(request):
    current_time = timezone.now()
    return render(request, 'main/index.html', {'user': request.user, 'current_time': current_time})

# Vista para el logout
def user_logout(request):
    logout(request)
    return redirect('login')
