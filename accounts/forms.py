from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordResetForm, SetPasswordForm
from .models import User
from applicant_profile.models import ApplicantProfile
from employer_profile.models import EmployerProfile
from django.contrib.auth import get_user_model

User = get_user_model() 

# --- Base Registration Form for both Applicant and Employer ---
class ApplicantRegistrationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'placeholder': 'Email address',
            'class': 'form-control'
        })
    )
    full_name = forms.CharField(
        required=True,
        max_length=300,
        widget=forms.TextInput(attrs={
            'placeholder': 'Full name',
            'class': 'form-control'
        })
    )
    username = forms.CharField(
        required=True,
        max_length=150,
        widget=forms.TextInput(attrs={
            'placeholder': 'Username',
            'class': 'form-control'
        }),
        help_text='Username cannot be changed after registration.'
    )
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Password',
            'class': 'form-control'
        })
    )
    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Confirm password',
            'class': 'form-control'
        })
    )
    terms_and_conditions = forms.BooleanField(required=True)
    account_type = forms.ChoiceField(
        choices=[('applicant', 'Applicant'), ('employer', 'Employer')],
        widget=forms.Select(attrs={'class': 'form-select'}),
        initial='applicant' 
    )

    class Meta:
        model = User
        fields = [
            'full_name',
            'username',
            'email',
            'password1',
            'password2',
            'account_type',
        ]

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('This username is already taken.')
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('An account with this email already exists.')
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        
        user.username = self.cleaned_data['username']
        user.email = self.cleaned_data['email']
        user.set_name_from_full_name(self.cleaned_data['full_name'])
        user.user_type = self.cleaned_data.get('account_type', 'applicant') 

        # Persist accepted terms flag if present on the form
        accepted = self.cleaned_data.get('terms_and_conditions')
        if accepted:
            user.accepted_terms = True

        if commit:
            user.save()

            if user.user_type == 'applicant':
                ApplicantProfile.objects.create(
                    user=user,
                    first_name=user.first_name,
                    last_name=user.last_name
                )
            elif user.user_type == 'employer':
                EmployerProfile.objects.create(
                    user=user,
                    company_name=self.cleaned_data['full_name']
                )

        return user

class EmployerRegistrationForm(ApplicantRegistrationForm):
    account_type = forms.ChoiceField(
        choices=[('applicant', 'Applicant'), ('employer', 'Employer')],
        widget=forms.Select(attrs={'class': 'form-select'}),
        initial='employer'
    )

class UserLoginForm(AuthenticationForm):
    username = forms.CharField(
        label="Email address",
        widget=forms.TextInput(attrs={
            'placeholder': 'Email address',
            'class': 'form-control',
            'id': 'id_username'
        })
    )
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Password',
            'class': 'form-control',
            'id': 'id_password'
        })
    )
    remember_me = forms.BooleanField(
        required=False,
        label='Remember Me',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    class Meta:
        fields = ['username', 'password', 'remember_me']


class CustomPasswordResetForm(PasswordResetForm):
    """Custom password reset form with styled email field"""
    email = forms.EmailField(
        label="Email address",
        max_length=254,
        widget=forms.EmailInput(attrs={
            'placeholder': 'Email address',
            'class': 'form-control',
            'autocomplete': 'email',
            'id': 'id_email'
        })
    )


class CustomSetPasswordForm(SetPasswordForm):
    """Custom set password form with styled fields"""
    new_password1 = forms.CharField(
        label="New Password",
        widget=forms.PasswordInput(attrs={
            'placeholder': 'New password',
            'class': 'form-control',
            'autocomplete': 'new-password',
            'id': 'id_new_password1'
        }),
        strip=False,
    )
    new_password2 = forms.CharField(
        label="Confirm New Password",
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Confirm new password',
            'class': 'form-control',
            'autocomplete': 'new-password',
            'id': 'id_new_password2'
        }),
        strip=False,
    )