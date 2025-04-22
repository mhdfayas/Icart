# views.py - Updated views for registration and profile
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import UserProfile
from .forms import UserRegistrationForm, UserProfileUpdateForm, ProfileImageUpdateForm

def register_view(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            # Create user but don't save yet
            new_user = form.save(commit=False)
            # Set password
            new_user.set_password(form.cleaned_data['password'])
            # Save user
            new_user.save()
            
            # Set profile image if provided
            if 'profile_image' in request.FILES:
                new_user.profile.profile_image = request.FILES['profile_image']
                new_user.profile.save()
            
            # Log in the user
            user = authenticate(username=form.cleaned_data['username'],
                               password=form.cleaned_data['password'])
            login(request, user)
            messages.success(request, 'Registration successful')
            return redirect('home')
        else:
            for error in form.errors:
                messages.error(request, form.errors[error])
    else:
        form = UserRegistrationForm()
        
    return render(request, 'accounts/register.html', {'form': form})

@login_required
def profile_view(request):
    if request.method == 'POST':
        user_form = UserProfileUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileImageUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Profile updated successfully')
            return redirect('profile')
    else:
        user_form = UserProfileUpdateForm(instance=request.user)
        profile_form = ProfileImageUpdateForm(instance=request.user.profile)
    
    return render(request, 'store/profile.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })
# views.py - Updated login_view with profile creation

from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import UserProfile

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            # Check if the user has a profile, create one if not
            try:
                profile = user.profile
            except:
                # Profile doesn't exist, create one
                UserProfile.objects.create(user=user)
            
            login(request, user)
            messages.success(request, 'Login successful')
            
            # Redirect to the page user was trying to access
            next_url = request.GET.get('next', 'home')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password')
            
    return render(request, 'accounts/login.html')

def logout_view(request):
    logout(request)
    messages.success(request, 'Logout successful')
    return redirect('home')