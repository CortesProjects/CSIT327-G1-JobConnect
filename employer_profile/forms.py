from django import forms
from accounts.models import EmployerProfile 

# --- Step 1: Company Info Form (For Image/File Uploads) ---
class EmployerProfileCompanyInfoForm(forms.ModelForm):
    company_name = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Enter your company name', 'class': 'form-control', 'required': 'required'}),
        label='Company Name *'
    )
    # FIX: Change widget to HiddenInput
    about_us = forms.CharField(
        widget=forms.HiddenInput(),
        required=False # Can be optional since the editor handles display
    ) 
    # File fields are handled by default widgets

    class Meta:
        model = EmployerProfile
        fields = ['company_name', 'about_us', 'logo', 'business_permit']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make company_name required, files handled by JavaScript
        self.fields['company_name'].required = True
        self.fields['logo'].required = False
        self.fields['business_permit'].required = False
        self.fields['about_us'].required = False

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
