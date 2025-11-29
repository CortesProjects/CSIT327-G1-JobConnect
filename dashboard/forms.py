from django import forms
from accounts.models import User, UserSocialLink
from applicant_profile.models import ApplicantProfile
from employer_profile.models import EmployerProfile
from django.contrib.auth.forms import PasswordChangeForm


class ApplicantSocialLinkForm(forms.ModelForm):
    """Form for adding/editing social links (now using UserSocialLink)"""
    
    class Meta:
        model = UserSocialLink
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
        fields = ['profile_image', 'title', 'first_name', 'middle_name', 'last_name', 'experience', 'education_level', 'resume']
        widgets = {
            'profile_image': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
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
            'education_level': forms.Select(attrs={
                'class': 'form-control'
            }),
            'resume': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.doc,.docx'
            }),
        }
        labels = {
            'profile_image': 'Profile Picture',
            'title': 'Title/Headline',
            'first_name': 'First Name',
            'middle_name': 'Middle Name (Optional)',
            'last_name': 'Last Name',
            'experience': 'Experience',
            'education_level': 'Education Level',
            'resume': 'Resume/CV',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['middle_name'].required = False
        self.fields['profile_image'].required = False
        self.fields['title'].required = False
        self.fields['resume'].required = False
        self.fields['experience'].required = False
        self.fields['education_level'].required = False
        
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
        self.fields['education_level'].widget.choices = [
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
    
    def clean_profile_image(self):
        profile_image = self.cleaned_data.get('profile_image')
        # If profile_image is False, it means no new file was uploaded (unchanged)
        if profile_image is False:
            return profile_image
        # If profile_image exists and is not False, validate it
        if profile_image:
            # Check file size (max 5MB)
            if hasattr(profile_image, 'size') and profile_image.size > 5 * 1024 * 1024:
                raise forms.ValidationError("Image file size must be less than 5MB.")
            # Check file type
            if hasattr(profile_image, 'content_type') and profile_image.content_type not in ['image/jpeg', 'image/jpg', 'image/png', 'image/gif']:
                raise forms.ValidationError("Only JPG, PNG, and GIF images are allowed.")
        return profile_image
    
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
        fields = ['nationality', 'date_of_birth', 'gender', 'marital_status', 'location_street','location_city','location_country', 'biography']
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
            'location_street': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Street address'
            }),
            'location_city': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'City'
            }),
            'location_country': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Country'
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
            'location_street': 'Street Address',
            'location_city': 'City',
            'location_country': 'Country',
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
        fields = ['company_profile_image', 'company_banner_image', 'company_name', 'about_us']
        widgets = {
            'company_profile_image': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'company_banner_image': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'company_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Company name'}),
            'about_us': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Write down about your company here. Let the candidate know who we are...',
                'rows': 6
            }),
        }
        labels = {
            'company_profile_image': 'Upload Logo',
            'company_banner_image': 'Upload Banner / Cover Image',
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
        fields = ['contact_phone_number', 'contact_email']
        widgets = {
            'contact_phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Phone number..'
            }),
            'contact_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Contact email address...'
            }),
        }
        labels = {
            'contact_phone_number': 'Phone',
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
        fields = ['company_business_permit']
        widgets = {
            'company_business_permit': forms.FileInput(attrs={'accept': '.pdf,.jpg,.jpeg,.png'}),
        }
        labels = {
            'company_business_permit': 'Upload Business Permit',
        }
    
    def clean_company_business_permit(self):
        permit = self.cleaned_data.get('company_business_permit')
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


# =====================================================
# JOB SEARCH FORMS
# =====================================================

class JobSearchForm(forms.Form):
    """Form for job search with filters and validation"""
    
    query = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'search-input',
            'placeholder': 'Job title, Keyword...',
            'id': 'id_query'
        }),
        label='Search'
    )
    
    category = forms.ChoiceField(
        required=False,
        widget=forms.Select(attrs={
            'class': 'filter-dropdown',
            'id': 'job_role'
        }),
        label='Category'
    )
    
    education = forms.ChoiceField(
        required=False,
        widget=forms.Select(attrs={
            'class': 'filter-dropdown',
            'id': 'education'
        }),
        label='Education'
    )
    
    experience = forms.ChoiceField(
        required=False,
        widget=forms.Select(attrs={
            'class': 'filter-dropdown',
            'id': 'experience'
        }),
        label='Experience'
    )
    
    job_level = forms.ChoiceField(
        required=False,
        widget=forms.Select(attrs={
            'class': 'filter-dropdown',
            'id': 'job_level'
        }),
        label='Level'
    )
    
    salary_min = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'salary-input',
            'placeholder': 'Min',
            'id': 'salary_min'
        }),
        label='Minimum Salary'
    )
    
    salary_max = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'salary-input',
            'placeholder': 'Max',
            'id': 'salary_max'
        }),
        label='Maximum Salary'
    )
    
    def __init__(self, *args, **kwargs):
        # Extract choices from kwargs
        category_choices = kwargs.pop('category_choices', [])
        education_choices = kwargs.pop('education_choices', [])
        experience_choices = kwargs.pop('experience_choices', [])
        job_level_choices = kwargs.pop('job_level_choices', [])
        
        super().__init__(*args, **kwargs)
        
        # Set dynamic choices for select fields
        self.fields['category'].choices = category_choices
        self.fields['education'].choices = education_choices
        self.fields['experience'].choices = experience_choices
        self.fields['job_level'].choices = job_level_choices
    
    def clean_query(self):
        """Validate and sanitize search query"""
        query = self.cleaned_data.get('query', '').strip()
        if query:
            # Limit query length
            if len(query) > 200:
                raise forms.ValidationError("Search query is too long. Maximum 200 characters.")
            # Basic sanitization - remove dangerous characters
            dangerous_chars = ['<', '>', '{', '}', '|', '\\', '^', '`']
            for char in dangerous_chars:
                if char in query:
                    raise forms.ValidationError("Search query contains invalid characters.")
        return query
    
    def clean(self):
        """Cross-field validation"""
        cleaned_data = super().clean()
        salary_min = cleaned_data.get('salary_min')
        salary_max = cleaned_data.get('salary_max')
        
        # Validate salary range
        if salary_min and salary_max:
            if salary_min > salary_max:
                raise forms.ValidationError({
                    'salary_max': 'Maximum salary must be greater than or equal to minimum salary.'
                })
            
            # Check reasonable salary range
            if salary_max - salary_min > 10000000:  # 10M difference limit
                raise forms.ValidationError({
                    'salary_max': 'Salary range is too wide. Please enter a more specific range.'
                })
        
        # Validate salary values are reasonable
        if salary_min and salary_min > 100000000:  # 100M limit
            raise forms.ValidationError({
                'salary_min': 'Minimum salary value is unrealistic. Please enter a valid amount.'
            })
        
        if salary_max and salary_max > 100000000:  # 100M limit
            raise forms.ValidationError({
                'salary_max': 'Maximum salary value is unrealistic. Please enter a valid amount.'
            })
        
        return cleaned_data


class EmployerApplicationFilterForm(forms.Form):
    """Filter form for employer job applications (education, experience, and sort)."""

    education = forms.ChoiceField(required=False, widget=forms.Select(attrs={'class': 'filter-dropdown'}), label='Education')
    experience = forms.ChoiceField(required=False, widget=forms.Select(attrs={'class': 'filter-dropdown'}), label='Experience')
    sort = forms.ChoiceField(
        required=False,
        choices=[
            ('', 'Default (Newest)'),
            ('newest', 'Newest First'),
            ('oldest', 'Oldest First'),
            ('name', 'Name (A-Z)'),
        ],
        widget=forms.RadioSelect(attrs={'class': 'sort-radio'}),
        label='Sort By'
    )

    def __init__(self, *args, **kwargs):
        education_choices = kwargs.pop('education_choices', [])
        experience_choices = kwargs.pop('experience_choices', [])
        super().__init__(*args, **kwargs)
        # Provide defaults
        self.fields['education'].choices = [('', 'All Education Levels')] + list(education_choices)
        self.fields['experience'].choices = [('', 'All Experience Levels')] + list(experience_choices)


class FavoriteJobForm(forms.Form):
    """Form for favoriting/unfavoriting a job with validation"""
    
    job_id = forms.IntegerField(
        required=True,
        min_value=1,
        error_messages={
            'required': 'Job ID is required.',
            'invalid': 'Invalid job ID.',
            'min_value': 'Invalid job ID.'
        }
    )
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
    
    def clean_job_id(self):
        """Validate that the job exists and is active"""
        from jobs.models import Job
        job_id = self.cleaned_data.get('job_id')
        
        try:
            job = Job.objects.get(id=job_id)
        except Job.DoesNotExist:
            raise forms.ValidationError('Job not found.')
        
        # Check if job is active
        if job.status != 'active':
            raise forms.ValidationError('This job is no longer available.')
        
        # Store job instance for later use
        self.cleaned_data['job'] = job
        return job_id
    
    def clean(self):
        """Additional validation"""
        cleaned_data = super().clean()
        
        # Validate user is an applicant
        if self.user:
            if not hasattr(self.user, 'user_type') or self.user.user_type != 'applicant':
                raise forms.ValidationError('Only applicants can favorite jobs.')
            
            if not self.user.is_authenticated:
                raise forms.ValidationError('You must be logged in to favorite jobs.')
        
        return cleaned_data

