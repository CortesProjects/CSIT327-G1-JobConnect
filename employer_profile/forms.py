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
        # Make all fields required
        self.fields['company_name'].required = True
        self.fields['logo'].required = False  # Validated in clean()
        self.fields['business_permit'].required = False  # Validated in clean()
        self.fields['about_us'].required = False
    
    def clean_company_name(self):
        company_name = self.cleaned_data.get('company_name')
        if not company_name or not company_name.strip():
            raise forms.ValidationError('Company name is required.')
        return company_name.strip()
    
    def clean_logo(self):
        logo = self.cleaned_data.get('logo')
        # If editing and logo already exists, it's optional
        if self.instance and self.instance.pk and self.instance.logo and not logo:
            return self.instance.logo
        # If new profile or no existing logo, require it
        if not logo and (not self.instance.pk or not self.instance.logo):
            raise forms.ValidationError('Company logo is required.')
        return logo
    
    def clean_business_permit(self):
        permit = self.cleaned_data.get('business_permit')
        # If editing and permit already exists, it's optional
        if self.instance and self.instance.pk and self.instance.business_permit and not permit:
            return self.instance.business_permit
        # If new profile or no existing permit, require it
        if not permit and (not self.instance.pk or not self.instance.business_permit):
            raise forms.ValidationError('Business permit is required.')
        return permit

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

    def __init__(self, *args, **kwargs):
        # Pre-fill contact_email from the related user if profile doesn't have one
        super().__init__(*args, **kwargs)
        
        # Check if profile already has a contact_email saved
        if self.instance and self.instance.contact_email:
            # If profile already has a contact_email, use it (instance will handle it)
            return

        # If no contact_email on profile, and the profile is linked to a user, use user's email
        if self.instance and hasattr(self.instance, 'user') and self.instance.user:
            user_email = getattr(self.instance.user, 'email', None)
            if user_email:
                # Set in form.initial dict, not field.initial, for ModelForm with instance
                self.initial['contact_email'] = user_email

    class Meta:
        model = EmployerProfile
        fields = ['phone_number', 'contact_email']
