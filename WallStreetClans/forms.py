from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import WallStreetUser, ROLE_CHOICES, OTP
from django.contrib.auth import get_user_model

User = get_user_model()

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    role = forms.ChoiceField(choices=ROLE_CHOICES)
    terms_accepted = forms.BooleanField(required=True, label="I accept the terms and conditions")

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'role', 'terms_accepted']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.username = self.cleaned_data['username']
        user.role = self.cleaned_data['role']  # Remove the extra space after 'role'
        user.terms_accepted = self.cleaned_data['terms_accepted']
        if commit:
            user.save()
        return user

    def clean_terms_accepted(self):
        terms_accepted = self.cleaned_data.get('terms_accepted')
        if not terms_accepted:
            raise forms.ValidationError('You must accept the terms and conditions to register.')
        return terms_accepted

class LoginForm(forms.Form):
    email = forms.EmailField(required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)
    role = forms.ChoiceField(choices=ROLE_CHOICES, required=True)

class OTPForm(forms.Form):
    email = forms.EmailField(label='Email', required=True)
    otp = forms.CharField(label='OTP', max_length=6, required=True)

class PaymentForm(forms.Form):
    email = forms.EmailField(required=True)
    amount = forms.DecimalField(max_digits=10, decimal_places=2, required=True)
    listing_id = forms.IntegerField(widget=forms.HiddenInput(), required=True)  # Ensure proper field requirement
