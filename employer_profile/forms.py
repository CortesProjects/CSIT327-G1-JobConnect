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
        # Make company_name, logo, and business_permit required
        self.fields['company_name'].required = True
        self.fields['logo'].required = True
        self.fields['business_permit'].required = True
        self.fields['about_us'].required = False

# --- Step 2: Founding Info Form ---
class EmployerProfileFoundingInfoForm(forms.ModelForm):
    organization_type = forms.ChoiceField(
        required=True,
        choices=EmployerProfile.ORGANIZATION_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select', 'required': 'required'}),
        label='Organization Type *'
    )
    industry_type = forms.ChoiceField(
        required=True,
        choices=EmployerProfile.INDUSTRY_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select', 'required': 'required'}),
        label='Industry Type *'
    )
    team_size = forms.ChoiceField(
        required=True,
        choices=EmployerProfile.TEAM_SIZE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select', 'required': 'required'}),
        label='Team Size *'
    )
    # Use CharField with attrs to get the desired date picker appearance without complex widgets
    year_established = forms.DateField(
        required=True,
        widget=forms.DateInput(attrs={
            'type': 'date', 
            'placeholder': 'YYYY-MM-DD',
            'class': 'form-control date-picker-input',
            'required': 'required'
        }),
        label='Year Established *'
    )
    company_website = forms.URLField(
        required=False,
        widget=forms.URLInput(attrs={'placeholder': 'Website url...', 'class': 'form-control'}),
        label='Company Website (Optional)'
    )
    company_vision = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'placeholder': 'Tell us about your company vision...', 'rows': 4, 'class': 'form-control'}),
        label='Company Vision (Optional)'
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
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Phone number...', 'class': 'form-control', 'required': 'required'}),
        label='Phone Number *'
    )
    contact_email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'placeholder': 'Email address', 'class': 'form-control', 'required': 'required'}),
        label='Contact Email *'
    )

    class Meta:
        model = EmployerProfile
        fields = ['phone_number', 'contact_email']
