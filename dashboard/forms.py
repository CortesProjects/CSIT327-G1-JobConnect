from django import forms
from accounts.models import ApplicantProfile, ApplicantSocialLink, EmployerProfile, User
from django.contrib.auth.forms import PasswordChangeForm


class ApplicantSocialLinkForm(forms.ModelForm):
    """Form for adding/editing social links"""
    
    class Meta:
        model = ApplicantSocialLink
        fields = ['platform', 'url']
        widgets = {
            'platform': forms.Select(attrs={'class': 'social-platform-select'}),
            'url': forms.URLInput(attrs={
                'class': 'social-link-input',
                'placeholder': 'Profile link/url...'
            }),
        }
        labels = {
            'platform': 'Social Platform',
            'url': 'Profile URL',
        }
    
    def clean_url(self):
        url = self.cleaned_data.get('url')
        if url and not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        return url


class ApplicantPersonalInfoForm(forms.ModelForm):
    """Form for Personal Information tab"""
    
    class Meta:
        model = ApplicantProfile
        fields = ['image', 'first_name', 'middle_name', 'last_name', 'school_name', 'degree']
        widgets = {
            'image': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First name'}),
            'middle_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Middle name (Optional)'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last name'}),
            'school_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'School/University'}),
            'degree': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Degree/Course'}),
        }
        labels = {
            'image': 'Profile Picture',
            'first_name': 'First Name',
            'middle_name': 'Middle Name (Optional)',
            'last_name': 'Last Name',
            'school_name': 'Education',
            'degree': 'Degree/Course',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['middle_name'].required = False
        self.fields['image'].required = False


class ApplicantProfileDetailsForm(forms.ModelForm):
    """Form for Profile tab - extended profile details"""
    
    class Meta:
        model = ApplicantProfile
        fields = ['location', 'year_level', 'skills_summary', 'biography']
        widgets = {
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City, Country'}),
            'year_level': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Year level/Experience'}),
            'skills_summary': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Python, JavaScript, SQL, Django, React, Problem Solving...',
                'rows': 3
            }),
            'biography': forms.Textarea(attrs={
                'class': 'form-control', 
                'placeholder': 'Write down your biography here. Let the employers know who you are...',
                'rows': 6
            }),
        }
        labels = {
            'location': 'Location',
            'year_level': 'Experience',
            'skills_summary': 'Skills',
            'biography': 'Biography',
        }


class ApplicantContactInfoForm(forms.ModelForm):
    """Form for Account Settings - Contact Info"""
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email address...'}),
        label='Email'
    )
    
    class Meta:
        model = ApplicantProfile
        fields = ['contact_number']
        widgets = {
            'contact_number': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Phone number...'
            }),
        }
        labels = {
            'contact_number': 'Phone',
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if self.user:
            self.fields['email'].initial = self.user.email
    
    def save(self, commit=True):
        profile = super().save(commit=False)
        if self.user:
            self.user.email = self.cleaned_data['email']
            if commit:
                self.user.save()
        if commit:
            profile.save()
        return profile


class ApplicantProfilePrivacyForm(forms.ModelForm):
    """Form for profile privacy settings"""
    
    class Meta:
        model = ApplicantProfile
        fields = ['is_public']
        widgets = {
            'is_public': forms.CheckboxInput(attrs={'class': 'privacy-toggle'}),
        }
        labels = {
            'is_public': 'Make Profile Public',
        }


class ApplicantResumeForm(forms.ModelForm):
    """Form for resume upload"""
    
    class Meta:
        model = ApplicantProfile
        fields = ['resume']
        widgets = {
            'resume': forms.FileInput(attrs={'accept': '.pdf,.doc,.docx'}),
        }
        labels = {
            'resume': 'Upload Resume',
        }
    
    def clean_resume(self):
        resume = self.cleaned_data.get('resume')
        if resume:
            # 5MB size limit
            if resume.size > 5 * 1024 * 1024:
                raise forms.ValidationError("Resume file cannot be larger than 5MB.")
            # Check file extension
            allowed_extensions = ['pdf', 'doc', 'docx']
            file_extension = resume.name.split('.')[-1].lower()
            if file_extension not in allowed_extensions:
                raise forms.ValidationError(f"Only {', '.join(allowed_extensions).upper()} files are allowed.")
        return resume


# =====================================================
# EMPLOYER FORMS
# =====================================================

class EmployerCompanyInfoForm(forms.ModelForm):
    """Form for Company Info tab"""
    
    class Meta:
        model = EmployerProfile
        fields = ['logo', 'banner', 'company_name', 'about_us']
        widgets = {
            'logo': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'banner': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'company_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Company name'}),
            'about_us': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Write down about your company here. Let the candidate know who we are...',
                'rows': 6
            }),
        }
        labels = {
            'logo': 'Upload Logo',
            'banner': 'Upload Banner / Cover Image',
            'company_name': 'Company Name',
            'about_us': 'About Us',
        }


class EmployerFoundingInfoForm(forms.ModelForm):
    """Form for Founding Info tab"""
    
    class Meta:
        model = EmployerProfile
        fields = ['organization_type', 'industry_type', 'team_size', 'year_established', 'company_website', 'company_vision']
        widgets = {
            'organization_type': forms.Select(attrs={'class': 'form-control'}),
            'industry_type': forms.Select(attrs={'class': 'form-control'}),
            'team_size': forms.Select(attrs={'class': 'form-control'}),
            'year_established': forms.DateInput(attrs={
                'class': 'form-control',
                'placeholder': 'dd/mm/yyyy',
                'type': 'date'
            }),
            'company_website': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'Website url...'
            }),
            'company_vision': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Tell us what Vision of your company...',
                'rows': 6
            }),
        }
        labels = {
            'organization_type': 'Organization Type',
            'industry_type': 'Industry Types',
            'team_size': 'Team Size',
            'year_established': 'Year of Establishment',
            'company_website': 'Company Website',
            'company_vision': 'Company Vision',
        }
    
    def clean_company_website(self):
        url = self.cleaned_data.get('company_website')
        if url and not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        return url


class EmployerContactInfoForm(forms.ModelForm):
    """Form for Account Settings - Contact Info"""
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email address...'}),
        label='Contact Email'
    )
    
    class Meta:
        model = EmployerProfile
        fields = ['phone_number', 'contact_email']
        widgets = {
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Phone number..'
            }),
            'contact_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Contact email address...'
            }),
        }
        labels = {
            'phone_number': 'Phone',
            'contact_email': 'Contact Email',
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if self.user:
            self.fields['email'].initial = self.user.email
    
    def save(self, commit=True):
        profile = super().save(commit=False)
        if self.user:
            self.user.email = self.cleaned_data['email']
            if commit:
                self.user.save()
        if commit:
            profile.save()
        return profile


class EmployerBusinessPermitForm(forms.ModelForm):
    """Form for business permit upload"""
    
    class Meta:
        model = EmployerProfile
        fields = ['business_permit']
        widgets = {
            'business_permit': forms.FileInput(attrs={'accept': '.pdf,.jpg,.jpeg,.png'}),
        }
        labels = {
            'business_permit': 'Upload Business Permit',
        }
    
    def clean_business_permit(self):
        permit = self.cleaned_data.get('business_permit')
        if permit:
            # 10MB size limit
            if permit.size > 10 * 1024 * 1024:
                raise forms.ValidationError("Business permit file cannot be larger than 10MB.")
            # Check file extension
            allowed_extensions = ['pdf', 'jpg', 'jpeg', 'png']
            file_extension = permit.name.split('.')[-1].lower()
            if file_extension not in allowed_extensions:
                raise forms.ValidationError(f"Only {', '.join(allowed_extensions).upper()} files are allowed.")
        return permit

