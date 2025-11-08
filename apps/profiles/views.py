from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User
from .forms import CustomUserCreationForm
from django.contrib import messages


def profile(request, username):
    user = get_object_or_404(User, username=username)
    context = {
        'profile_user': user,
    }
    return render(request, 'profiles/profile.html', context)

def create_profile(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Account created successfully!")
            return redirect('home')
    else:
        form = CustomUserCreationForm()

    return render(request, 'profiles/create_profile.html', {'form': form})