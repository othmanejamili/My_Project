from django.shortcuts import render, redirect
from .models import Profile
from .forms import RegistrerForm, LoginForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required  # Import the decorator

# Home view
@login_required  # Protect the home view
def home(request):
    print(f"User: {request.user}, Authenticated: {request.user.is_authenticated}")
    return render(request, 'restaurent/home.html')



# Register view
def register(request):
    if request.method == 'POST':
        form = RegistrerForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Use the correct backend path for your EmailBackend
            login(request, user, backend='commend_Restaurent.backends.EmailBackend')  
            return redirect('home') 
    else:
        form = RegistrerForm()
    return render(request, 'restaurent/registrer.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            user = authenticate(request, email=email, password=password)  # Authenticate using email
            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                messages.error(request, 'Invalid email or password.')
        else:
            messages.error(request, 'Form is not valid.')
    else:
        form = LoginForm()
    
    return render(request, 'restaurent/login.html', {'form': form})

