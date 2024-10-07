from django import forms
from .models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import AuthenticationForm

class RegistrerForm(UserCreationForm):
    email = forms.EmailField(widget=forms.TextInput(attrs={'class': 'input_email','placeholder':'email@gmil.com'}))
    first_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'input_name','placeholder':'first Name'}))
    last_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'input_name','placeholder':'Last Name'}))
    date_of_birth = forms.DateField(
        required=False,
        widget=forms.SelectDateWidget(
            years=range(1970, 2024),
            attrs={'class': 'input_date_of_birth','placeholder':'Date'}
        ),
        help_text="Enter your date of birth."
    )
    phone_number = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'input_Numbre_phone',
            'id': 'phonenumber',
            'pattern': r'\d+',
            'maxlength': '11',
            'placeholder': 'Phone Number*',
        }),
        help_text="Enter your phone number."
    )
    def __init__(self, *args, **kwargs):
        super(RegistrerForm, self).__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'class': 'input_password'})
        self.fields['password2'].widget.attrs.update({'class': 'input_confirm_password'})

    
    class Meta:
        model = User
        fields = ['first_name','last_name','email','date_of_birth','phone_number','gender']


class LoginForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'input_email','placeholder':'email@gmil.com'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'input_password','placeholder':'password'}))

class PasswordResetRequestForm(forms.Form):
    email = forms.EmailField()

class PasswordResetForm(forms.Form):
    new_password1 = forms.CharField(label="New password", widget=forms.PasswordInput)
    new_password2 = forms.CharField(label="Confirm new password", widget=forms.PasswordInput)
