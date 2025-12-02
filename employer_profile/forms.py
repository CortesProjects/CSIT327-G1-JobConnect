from django import forms
from employer_profile.models import EmployerProfile 

class EmployerProfileCompanyInfoForm(forms.ModelForm):
    company_name = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Enter your company name', 'class': 'form-control', 'required': 'required'}),
        label='Company Name *'
    )
    about_us = forms.CharField(
        widget=forms.HiddenInput(),
        required=False
    ) 
    class Meta:
        model = EmployerProfile
        fields = ['company_name', 'about_us', 'company_profile_image', 'company_business_permit']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['company_name'].required = True
        self.fields['company_profile_image'].required = False  
        self.fields['company_business_permit'].required = False  
        self.fields['about_us'].required = False
    
    def clean_company_name(self):
        company_name = self.cleaned_data.get('company_name')
        if not company_name or not company_name.strip():
            raise forms.ValidationError('Company name is required.')
        return company_name.strip()
    
    def clean_company_profile_image(self):
        company_profile_image = self.cleaned_data.get('company_profile_image')
        if self.instance and self.instance.pk and self.instance.company_profile_image and not company_profile_image:
            return self.instance.company_profile_image
        if not company_profile_image and (not self.instance.pk or not self.instance.company_profile_image):
            raise forms.ValidationError('Company logo is required.')
        if not hasattr(company_profile_image, 'content_type'):
            return company_profile_image

        valid_types = ['image/jpeg', 'image/jpg', 'image/png']
        if company_profile_image.content_type not in valid_types:
            raise forms.ValidationError('Please upload a valid image file (JPG, or PNG).')
        
        max_size = 5 * 1024 * 1024
        if company_profile_image.size > max_size:
            raise forms.ValidationError('Image size must be less than 5MB.')

        return company_profile_image
    
    def clean_company_business_permit(self):
        company_business_permit = self.cleaned_data.get('company_business_permit')
        if self.instance and self.instance.pk and self.instance.company_business_permit and not company_business_permit:
            return self.instance.company_business_permit
        if not company_business_permit and (not self.instance.pk or not self.instance.company_business_permit):
            raise forms.ValidationError('Business permit is required.')
        if not hasattr(company_business_permit, 'content_type'):
            return company_business_permit

        valid_types = [
            'image/jpeg', 'image/jpg', 'image/png',
            'application/pdf',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'application/msword'
        ]
        if company_business_permit.content_type not in valid_types:
            raise forms.ValidationError('Please upload a valid file (PNG, JPG, PDF, or DOCX).')

        max_size = 5 * 1024 * 1024
        if company_business_permit.size > max_size:
            raise forms.ValidationError('File size must be less than 5MB.')

        return company_business_permit
    
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
    
    def clean_year_established(self):
        from datetime import date
        year_established = self.cleaned_data.get('year_established')
        if year_established:
            if year_established > date.today():
                raise forms.ValidationError('Year established cannot be in the future.')

            if year_established.year < 1800:
                raise forms.ValidationError('Please enter a valid year of establishment.')
        return year_established
    
    def clean_company_website(self):
        url = self.cleaned_data.get('company_website', '').strip()
        if url:
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            if len(url) > 500:
                raise forms.ValidationError('Website URL is too long. Maximum 500 characters.')
        return url

class EmployerProfileContactForm(forms.ModelForm):
    contact_phone_number = forms.CharField(
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
        super().__init__(*args, **kwargs)
        
        if self.instance and self.instance.contact_email:
            pass

        if self.instance and hasattr(self.instance, 'user') and self.instance.user:
            user_email = getattr(self.instance.user, 'email', None)
            if user_email:
                self.initial['contact_email'] = user_email

    class Meta:
        model = EmployerProfile
        fields = ['contact_phone_number', 'contact_email']
    
    def clean_contact_phone_number(self):
        phone = self.cleaned_data.get('contact_phone_number', '').strip()
        if not phone:
            raise forms.ValidationError('Contact phone number is required.')
        digits_only = ''.join(c for c in phone if c.isdigit())
        if len(digits_only) < 10:
            raise forms.ValidationError('Phone number must be at least 10 digits.')
        if len(digits_only) > 15:
            raise forms.ValidationError('Phone number cannot exceed 15 digits.')
        return phone
    
    def clean_contact_email(self):
        email = self.cleaned_data.get('contact_email', '').strip()
        if not email:
            raise forms.ValidationError('Contact email is required.')
        return email
