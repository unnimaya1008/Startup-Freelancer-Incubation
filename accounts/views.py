from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import LoginForm
from projects.models import Project
from freelancer.models import FreelancerProfile
from startup.models import StartupProfile
from mentors.models import MentorProfile


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                # Redirect based on role
                if user.role == 'STARTUP':
                    return redirect('startup:startup_dashboard')
                elif user.role == 'FREELANCER':
                    return redirect('freelancer:freelancer_dashboard')
                elif user.role == 'MENTOR':
                    return redirect('mentors:dashboard')
                elif user.role == 'INVESTOR':
                    return redirect('investor_dashboard')
                else:
                    return redirect('admin:index')
            else:
                messages.error(request, "Invalid credentials")
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    return redirect('login')


def index(request):
    context = {
        'projects_count': Project.objects.count(),
        'freelancers_count': FreelancerProfile.objects.count(),
        'startups_count': StartupProfile.objects.count(),
        'mentors_count': MentorProfile.objects.count(),
    }
    return render(request, 'index.html', context)