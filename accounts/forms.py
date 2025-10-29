from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User, ApplicantProfile, EmployerProfile
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
        # Set the default choice for the Applicant form explicitly
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
        """Ensure username is unique."""
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('This username is already taken.')
        return username

    def save(self, commit=True):
        """Create either a Applicant or Employer user with their profile."""
        user = super().save(commit=False)
        
        # Set username from the form
        user.username = self.cleaned_data['username']
        user.email = self.cleaned_data['email']
        
        # Parse full name and set first_name and last_name
        user.set_name_from_full_name(self.cleaned_data['full_name'])
        
        # Use the value from the cleaned data, defaulting to 'applicant' if not provided
        user.user_type = self.cleaned_data.get('account_type', 'applicant') 

        if commit:
            user.save()

            # Create profile depending on user type
            if user.user_type == 'applicant':
                # Initialize ApplicantProfile with parsed names
                ApplicantProfile.objects.create(
                    user=user,
                    first_name=user.first_name,
                    last_name=user.last_name
                )
            elif user.user_type == 'employer':
                # Initialize EmployerProfile with parsed names
                EmployerProfile.objects.create(
                    user=user,
                    first_name=user.first_name,
                    last_name=user.last_name
                )

        return user

# --- NEW Employer Registration Form (Inherits from Applicant form) ---
class EmployerRegistrationForm(ApplicantRegistrationForm):
    """
    Inherits all fields and validation from ApplicantRegistrationForm, 
    but defaults the account_type field to 'employer'.
    """
    # Overrides the account_type field to change the initial/default value
    account_type = forms.ChoiceField(
        choices=[('applicant', 'Applicant'), ('employer', 'Employer')],
        widget=forms.Select(attrs={'class': 'form-select'}),
        initial='employer' # <<< This is the key difference
    )

    # Note: No need to redefine Meta or save(), as they are inherited and work correctly
    # based on the value passed for 'account_type'.

# --- User Login Form (Unchanged) ---
class UserLoginForm(AuthenticationForm):
    # Customize the username field to be labeled/placeholder as "Email address"
    username = forms.CharField(
        label="Email address",
        widget=forms.TextInput(attrs={
            'placeholder': 'Email address',
            'class': 'form-control',
            'id': 'id_username'
        })
    )
    # Customize the password field
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Password',
            'class': 'form-control',
            'id': 'id_password'
        })
    )
    
    # You can optionally add a 'Remember Me' field if you want to control session expiration
    remember_me = forms.BooleanField(
        required=False,
        label='Remember Me',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    class Meta:
        fields = ['username', 'password', 'remember_me']