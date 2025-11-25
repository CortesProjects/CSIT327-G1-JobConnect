from django import forms
from accounts.models import User
from applicant_profile.models import ApplicantProfile, ApplicantSocialLink
from employer_profile.models import EmployerProfile
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
        fields = ['image', 'title', 'first_name', 'middle_name', 'last_name', 'experience', 'education', 'website', 'resume']
        widgets = {
            'image': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'title': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'e.g., Software Developer, Marketing Specialist'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'First name'
            }),
            'middle_name': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Middle name (Optional)'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Last name'
            }),
            'experience': forms.Select(attrs={
                'class': 'form-control'
            }),
            'education': forms.Select(attrs={
                'class': 'form-control'
            }),
            'website': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://yourwebsite.com'
            }),
            'resume': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.doc,.docx'
            }),
        }
        labels = {
            'image': 'Profile Picture',
            'title': 'Title/Headline',
            'first_name': 'First Name',
            'middle_name': 'Middle Name (Optional)',
            'last_name': 'Last Name',
            'experience': 'Experience',
            'education': 'Educations',
            'website': 'Personal Website URL',
            'resume': 'Resume/CV',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['middle_name'].required = False
        self.fields['image'].required = False
        self.fields['title'].required = False
        self.fields['website'].required = False
        self.fields['resume'].required = False
        self.fields['experience'].required = False
        self.fields['education'].required = False
        
        # Set choices for experience field
        self.fields['experience'].widget.choices = [
            ('', 'Select experience level'),
            ('0-1', '0-1 years (Entry Level)'),
            ('1-3', '1-3 years'),
            ('3-5', '3-5 years'),
            ('5-10', '5-10 years'),
            ('10+', '10+ years (Senior)'),
        ]
        
        # Set choices for education field
        self.fields['education'].widget.choices = [
            ('', 'Select highest education level'),
            ('high_school', 'High School'),
            ('associate', 'Associate Degree'),
            ('bachelor', "Bachelor's Degree"),
            ('master', "Master's Degree"),
            ('doctorate', 'Doctorate/PhD'),
            ('vocational', 'Vocational/Technical'),
        ]
    
    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name', '').strip()
        if first_name and len(first_name) < 2:
            raise forms.ValidationError("First name must be at least 2 characters long.")
        if first_name and not all(c.isalpha() or c.isspace() or c == '-' for c in first_name):
            raise forms.ValidationError("First name can only contain letters, spaces, and hyphens.")
        return first_name
    
    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name', '').strip()
        if last_name and len(last_name) < 2:
            raise forms.ValidationError("Last name must be at least 2 characters long.")
        if last_name and not all(c.isalpha() or c.isspace() or c == '-' for c in last_name):
            raise forms.ValidationError("Last name can only contain letters, spaces, and hyphens.")
        return last_name
    
    def clean_image(self):
        image = self.cleaned_data.get('image')
        # If image is False, it means no new file was uploaded (unchanged)
        if image is False:
            return image
        # If image exists and is not False, validate it
        if image:
            # Check file size (max 5MB)
            if hasattr(image, 'size') and image.size > 5 * 1024 * 1024:
                raise forms.ValidationError("Image file size must be less than 5MB.")
            # Check file type
            if hasattr(image, 'content_type') and image.content_type not in ['image/jpeg', 'image/jpg', 'image/png', 'image/gif']:
                raise forms.ValidationError("Only JPG, PNG, and GIF images are allowed.")
        return image
    
    def clean_resume(self):
        resume = self.cleaned_data.get('resume')
        # If resume is False, it means no new file was uploaded (unchanged)
        if resume is False:
            return resume
        # If resume exists and is not False, validate it
        if resume:
            # Check file size (max 5MB)
            if hasattr(resume, 'size') and resume.size > 5 * 1024 * 1024:
                raise forms.ValidationError("Resume file size must be less than 5MB.")
            # Check file type
            allowed_types = [
                'application/pdf',
                'application/msword',
                'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            ]
            if hasattr(resume, 'content_type') and resume.content_type not in allowed_types:
                raise forms.ValidationError("Only PDF, DOC, and DOCX files are allowed.")
        return resume


class ApplicantProfileDetailsForm(forms.ModelForm):
    """Form for Profile tab - extended profile details"""
    
    class Meta:
        model = ApplicantProfile
        fields = ['nationality', 'date_of_birth', 'gender', 'marital_status', 'biography']
        widgets = {
            'nationality': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Filipino'
            }),
            'date_of_birth': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'gender': forms.Select(attrs={
                'class': 'form-control'
            }),
            'marital_status': forms.Select(attrs={
                'class': 'form-control'
            }),
            'biography': forms.Textarea(attrs={
                'class': 'form-control', 
                'placeholder': 'Write down your biography here. Let the employers know who you are...',
                'rows': 6
            }),
        }
        labels = {
            'nationality': 'Nationality',
            'date_of_birth': 'Date of Birth',
            'gender': 'Gender',
            'marital_status': 'Marital Status',
            'biography': 'Biography',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['nationality'].required = False
        self.fields['date_of_birth'].required = False
        self.fields['gender'].required = False
        self.fields['marital_status'].required = False
        self.fields['biography'].required = False
    
    def clean_date_of_birth(self):
        from datetime import date
        dob = self.cleaned_data.get('date_of_birth')
        if dob:
            today = date.today()
            age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
            if age < 16:
                raise forms.ValidationError("You must be at least 16 years old.")
            if age > 100:
                raise forms.ValidationError("Please enter a valid date of birth.")
        return dob


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
    
    def clean_contact_number(self):
        contact_number = self.cleaned_data.get('contact_number', '').strip()
        if contact_number:
            # Remove any non-digit characters for validation
            digits_only = ''.join(c for c in contact_number if c.isdigit())
            if len(digits_only) < 10:
                raise forms.ValidationError("Contact number must be at least 10 digits.")
            if len(digits_only) > 15:
                raise forms.ValidationError("Contact number cannot exceed 15 digits.")
        return contact_number
    
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

