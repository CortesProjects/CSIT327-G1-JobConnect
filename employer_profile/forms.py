from django import forms
from accounts.models import EmployerProfile 

# --- Step 1: Company Info Form (For Image/File Uploads) ---
class EmployerProfileCompanyInfoForm(forms.ModelForm):
    first_name = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'e.g., Juan', 'class': 'form-control'}),
        label='First Name'
    )
    middle_name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'e.g., Santos (Optional)', 'class': 'form-control'}),
        label='Middle Name (Optional)'
    )
    last_name = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'e.g., Dela Cruz', 'class': 'form-control'}),
        label='Last Name'
    )
    company_name = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Company name', 'class': 'form-control'})
    )
    # FIX: Change widget to HiddenInput
    about_us = forms.CharField(
        widget=forms.HiddenInput(),
        required=False # Can be optional since the editor handles display
    ) 
    # File fields are handled by default widgets

    class Meta:
        model = EmployerProfile
        fields = ['first_name', 'middle_name', 'last_name', 'company_name', 'about_us', 'logo', 'business_permit']

# --- Step 2: Founding Info Form ---
class EmployerProfileFoundingInfoForm(forms.ModelForm):
    organization_type = forms.ChoiceField(
        choices=EmployerProfile.ORGANIZATION_CHOICES, # Assuming you pulled choices from the model
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    industry_type = forms.ChoiceField(
        choices=EmployerProfile.INDUSTRY_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    team_size = forms.ChoiceField(
        choices=EmployerProfile.TEAM_SIZE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    # Use CharField with attrs to get the desired date picker appearance without complex widgets
    year_established = forms.DateField( 
        widget=forms.DateInput(attrs={
            'type': 'date', 
            'placeholder': 'YYYY-MM-DD',
            'class': 'form-control date-picker-input'
        })
    )
    company_website = forms.URLField(
        required=False,
        widget=forms.URLInput(attrs={'placeholder': 'Website url...', 'class': 'form-control'})
    )
    company_vision = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'placeholder': 'Tell us about your company vision...', 'rows': 4, 'class': 'form-control'})
    )

    class Meta:
        model = EmployerProfile
        fields = [
            'organization_type', 'industry_type', 'team_size', 
            'year_established', 'company_website', 'company_vision'
        ]

# --- Step 3: Contact Form ---
class EmployerProfileContactForm(forms.ModelForm):
    phone_number = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Phone number...', 'class': 'form-control'})
    )
    contact_email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={'placeholder': 'Email address', 'class': 'form-control'})
    )

    class Meta:
        model = EmployerProfile
        fields = ['phone_number', 'contact_email']
