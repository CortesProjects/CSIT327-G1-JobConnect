from django import forms
from django.core.exceptions import ValidationError
from datetime import date
from .models import Job


class JobPostForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = [
            'title', 'tags', 'category', 'min_salary', 'max_salary', 
            'salary_type', 'education', 'experience', 'job_type', 
            'vacancies', 'expiration_date', 'job_level', 'description', 
            'responsibilities', 'location'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Add job title, role, vacancies etc...',
                'id': 'job_title'
            }),
            'tags': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Job keyword, tags etc...',
                'id': 'tags'
            }),
            'category': forms.Select(attrs={
                'class': 'form-control',
                'id': 'category'
            }),
            'min_salary': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Minimum salary...',
                'id': 'min_salary',
                'min': '0'
            }),
            'max_salary': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Maximum salary...',
                'id': 'max_salary',
                'min': '0'
            }),
            'salary_type': forms.Select(attrs={
                'class': 'form-control',
                'id': 'salary_type'
            }),
            'education': forms.Select(attrs={
                'class': 'form-control',
                'id': 'education'
            }),
            'experience': forms.Select(attrs={
                'class': 'form-control',
                'id': 'experience'
            }),
            'job_type': forms.Select(attrs={
                'class': 'form-control',
                'id': 'job_type'
            }),
            'vacancies': forms.Select(attrs={
                'class': 'form-control',
                'id': 'vacancies'
            }),
            'expiration_date': forms.DateInput(attrs={
                'class': 'form-control',
                'placeholder': 'DD/MM/YYYY',
                'id': 'expiration_date',
                'type': 'date'
            }),
            'job_level': forms.Select(attrs={
                'class': 'form-control',
                'id': 'job_level'
            }),
            'description': forms.HiddenInput(attrs={
                'id': 'description_hidden'
            }),
            'responsibilities': forms.HiddenInput(attrs={
                'id': 'responsibilities_hidden'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter job location',
                'id': 'location'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ensure FK fields use active lookup table entries
        from .models import (
            JobCategory, EmploymentType, EducationLevel,
            ExperienceLevel, JobLevel, SalaryType
        )

        # If the model fields are present on the form, set their querysets
        if 'category' in self.fields:
            self.fields['category'].queryset = JobCategory.objects.filter(is_active=True)
        if 'job_type' in self.fields:
            # ModelChoiceField will be created for ForeignKey fields
            self.fields['job_type'].queryset = EmploymentType.objects.filter(is_active=True)
        if 'education' in self.fields:
            self.fields['education'].queryset = EducationLevel.objects.filter(is_active=True)
        if 'experience' in self.fields:
            self.fields['experience'].queryset = ExperienceLevel.objects.filter(is_active=True)
        if 'job_level' in self.fields:
            self.fields['job_level'].queryset = JobLevel.objects.filter(is_active=True)
        if 'salary_type' in self.fields:
            self.fields['salary_type'].queryset = SalaryType.objects.filter(is_active=True)

        # Vacancies should be a numeric input rather than a select
        self.fields['vacancies'].widget = forms.NumberInput(attrs={
            'class': 'form-control', 'id': 'vacancies', 'min': '1'
        })

    def clean_title(self):
        title = self.cleaned_data.get('title')
        if not title or not title.strip():
            raise ValidationError('Job title cannot be empty.')
        if len(title) > 100:
            raise ValidationError('Job title cannot exceed 100 characters.')
        return title.strip()

    def clean_description(self):
        description = self.cleaned_data.get('description')
        if not description or not description.strip():
            raise ValidationError('Job description cannot be empty.')
        
        # Remove HTML tags for length validation
        import re
        text_only = re.sub('<[^<]+?>', '', description)
        if len(text_only.strip()) < 50:
            raise ValidationError('Description must be at least 50 characters.')
        return description

    def clean_location(self):
        location = self.cleaned_data.get('location')
        if not location or not location.strip():
            raise ValidationError('Location cannot be empty.')
        return location.strip()

    def clean_expiration_date(self):
        expiration_date = self.cleaned_data.get('expiration_date')
        if expiration_date and expiration_date < date.today():
            raise ValidationError('Deadline must be a future date.')
        return expiration_date

    def clean(self):
        cleaned_data = super().clean()
        min_salary = cleaned_data.get('min_salary')
        max_salary = cleaned_data.get('max_salary')

        # Validate salary range
        if min_salary is not None and max_salary is not None:
            if min_salary < 0:
                self.add_error('min_salary', 'Minimum salary cannot be negative.')
            if max_salary < 0:
                self.add_error('max_salary', 'Maximum salary cannot be negative.')
            if min_salary > max_salary:
                self.add_error('min_salary', 'Minimum salary cannot be greater than maximum salary.')

        # Mirror model-level validation by populating instance and running its clean()
        try:
            # Assign cleaned values onto the instance for validation
            for field in self.Meta.fields:
                if field in cleaned_data:
                    setattr(self.instance, field, cleaned_data.get(field))

            # Call model.clean() to enforce model constraints
            self.instance.clean()
        except ValidationError as e:
            if hasattr(e, 'message_dict'):
                for f, msgs in e.message_dict.items():
                    for msg in msgs:
                        self.add_error(f, msg)
            else:
                raise

        return cleaned_data


class JobSearchForm(forms.Form):
    query = forms.CharField(
        required=False,
        min_length=1,
        max_length=100,
        widget=forms.TextInput(attrs={'placeholder': 'Search jobs...'})
    )

    location = forms.MultipleChoiceField(
        choices=[],  # populated dynamically
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-select'})
    )

    job_type = forms.ModelMultipleChoiceField(
        queryset=None,  # Will be set in __init__
        required=False,
        widget=forms.CheckboxSelectMultiple
    )

    category = forms.ModelMultipleChoiceField(
        queryset=None,  # Will be set in __init__
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-select'})
    )

    education = forms.ModelMultipleChoiceField(
        queryset=None,  # Will be set in __init__
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-select'})
    )

    experience = forms.ModelMultipleChoiceField(
        queryset=None,  # Will be set in __init__
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-select'})
    )

    job_level = forms.ModelMultipleChoiceField(
        queryset=None,  # Will be set in __init__
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-select'})
    )

    salary_min = forms.IntegerField(required=False)
    salary_max = forms.IntegerField(required=False)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Dynamically set querysets from lookup tables
        from .models import (
            JobCategory, EmploymentType, EducationLevel, 
            ExperienceLevel, JobLevel
        )
        self.fields['category'].queryset = JobCategory.objects.filter(is_active=True)
        self.fields['job_type'].queryset = EmploymentType.objects.filter(is_active=True)
        self.fields['education'].queryset = EducationLevel.objects.filter(is_active=True)
        self.fields['experience'].queryset = ExperienceLevel.objects.filter(is_active=True)
        self.fields['job_level'].queryset = JobLevel.objects.filter(is_active=True)


class JobApplicationForm(forms.Form):
    """Form for applying to a job with resume and cover letter."""
    
    job_id = forms.IntegerField(
        widget=forms.HiddenInput(),
        required=True
    )
    
    resume_id = forms.IntegerField(
        required=False,
        error_messages={
            'invalid': 'Please select a valid resume.'
        }
    )
    
    cover_letter = forms.CharField(
        required=False,
        max_length=5000,
        widget=forms.Textarea(attrs={
            'placeholder': 'Write your cover letter here...',
            'rows': 10
        }),
        error_messages={
            'max_length': 'Cover letter cannot exceed 5000 characters.'
        }
    )
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
    
    def clean_job_id(self):
        """Validate job exists and is active."""
        job_id = self.cleaned_data.get('job_id')
        
        try:
            job = Job.objects.get(id=job_id)
        except Job.DoesNotExist:
            raise ValidationError('Job not found.')
        
        if job.status != 'active':
            raise ValidationError('This job is no longer accepting applications.')
        
        # Check if job has expired
        if job.expiration_date and job.expiration_date < date.today():
            raise ValidationError('This job posting has expired.')
        
        self.cleaned_data['job'] = job
        return job_id
    
    def clean_resume_id(self):
        """Validate resume exists and belongs to the applicant."""
        resume_id = self.cleaned_data.get('resume_id')
        
        if not resume_id:
            # Check if applicant has a resume in their profile
            if self.user and hasattr(self.user, 'applicant_profile_rel'):
                profile = self.user.applicant_profile_rel
                if not profile.resume:
                    raise ValidationError('Please upload a resume to your profile before applying.')
                # Use profile resume
                self.cleaned_data['resume_file'] = profile.resume
                return None
            else:
                raise ValidationError('Resume is required to apply for this job.')
        
        # If resume_id provided, validate it exists and belongs to user
        # For now, we'll use the profile resume field
        # In future, if you have a separate Resume model, validate here
        
        return resume_id
    
    def clean(self):
        """Additional validation."""
        cleaned_data = super().clean()
        
        # Ensure user is authenticated and is an applicant
        if not self.user or not self.user.is_authenticated:
            raise ValidationError('You must be logged in to apply.')
        
        if not hasattr(self.user, 'user_type') or self.user.user_type != 'applicant':
            raise ValidationError('Only applicants can apply for jobs.')
        
        # Check for duplicate application
        from .models import JobApplication
        job = cleaned_data.get('job')
        if job:
            if JobApplication.objects.filter(applicant=self.user, job=job).exists():
                raise ValidationError('You have already applied for this job.')
        
        return cleaned_data