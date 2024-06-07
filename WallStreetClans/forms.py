# forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import OTP, ROLE_CHOICES
from django.contrib.auth import get_user_model
User = get_user_model()

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    role = forms.ChoiceField(choices=ROLE_CHOICES)
    terms_accepted = forms.BooleanField(required=True, label="I accept the terms and conditions")

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'role', 'terms_accepted']

    def clean_terms_accepted(self):
        terms_accepted = self.cleaned_data.get('terms_accepted')
        if not terms_accepted:
            raise forms.ValidationError('You must accept the terms and conditions to register.')
        return terms_accepted

class LoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)
    role = forms.ChoiceField(choices=ROLE_CHOICES)
    # fingerprint_auth = forms.BooleanField(required=False, label="Use fingerprint authentication")

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        role = cleaned_data.get('role')
        
        if not email:
            raise forms.ValidationError('Email is required.')
        
        if not role:
            raise forms.ValidationError('Role is required.')

        return cleaned_data

class OTPForm(forms.Form):
    email = forms.EmailField(label='Email', required=True)
    otp = forms.CharField(label='OTP', max_length=6, required=True)

class PaymentForm(forms.Form):
    email = forms.EmailField()
    amount = forms.DecimalField(max_digits=10, decimal_places=2)
    property_id = forms.IntegerField(widget=forms.HiddenInput())
