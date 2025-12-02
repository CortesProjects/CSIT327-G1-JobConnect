from django import forms
from django.core.exceptions import ValidationError
from datetime import date
from .models import Job, JobAlert


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
            # User-friendly empty label for selects
            self.fields['category'].empty_label = 'Select'
        if 'job_type' in self.fields:
            # ModelChoiceField will be created for ForeignKey fields
            self.fields['job_type'].queryset = EmploymentType.objects.filter(is_active=True)
            self.fields['job_type'].empty_label = 'Select'
        if 'education' in self.fields:
            self.fields['education'].queryset = EducationLevel.objects.filter(is_active=True)
            self.fields['education'].empty_label = 'Select'
        if 'experience' in self.fields:
            self.fields['experience'].queryset = ExperienceLevel.objects.filter(is_active=True)
            self.fields['experience'].empty_label = 'Select'
        if 'job_level' in self.fields:
            self.fields['job_level'].queryset = JobLevel.objects.filter(is_active=True)
            self.fields['job_level'].empty_label = 'Select'
        if 'salary_type' in self.fields:
            self.fields['salary_type'].queryset = SalaryType.objects.filter(is_active=True)
            self.fields['salary_type'].empty_label = 'Select'

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
            raise ValidationError('Job description is required. Please provide details about the position.')
        
        # Remove HTML tags for length validation
        import re
        text_only = re.sub('<[^<]+?>', '', description)
        if len(text_only.strip()) < 50:
            raise ValidationError('Job description must be at least 50 characters. Please provide more details about the role.')
        if len(text_only.strip()) > 10000:
            raise ValidationError('Job description is too long. Maximum 10,000 characters.')
        return description

    def clean_responsibilities(self):
        responsibilities = self.cleaned_data.get('responsibilities')
        if responsibilities:
            import re
            text_only = re.sub('<[^<]+?>', '', responsibilities)
            if len(text_only.strip()) > 5000:
                raise ValidationError('Responsibilities section is too long. Maximum 5,000 characters.')
        return responsibilities
    
    def clean_location(self):
        location = self.cleaned_data.get('location')
        if not location or not location.strip():
            raise ValidationError('Job location is required. Please specify where this position is based.')
        if len(location.strip()) > 200:
            raise ValidationError('Location is too long. Maximum 200 characters.')
        return location.strip()

    def clean_vacancies(self):
        vacancies = self.cleaned_data.get('vacancies')
        if vacancies is not None:
            if vacancies < 1:
                raise ValidationError('Number of vacancies must be at least 1.')
            if vacancies > 1000:
                raise ValidationError('Number of vacancies cannot exceed 1,000. Please contact support for bulk hiring.')
        return vacancies
    
    def clean_expiration_date(self):
        expiration_date = self.cleaned_data.get('expiration_date')
        if not expiration_date:
            raise ValidationError('Application deadline is required.')
        if expiration_date < date.today():
            raise ValidationError('Application deadline must be a future date.')
        # Check if deadline is too far in future (e.g., more than 1 year)
        from datetime import timedelta
        max_date = date.today() + timedelta(days=365)
        if expiration_date > max_date:
            raise ValidationError('Application deadline cannot be more than 1 year in the future.')
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


class JobAlertForm(forms.ModelForm):
    """Form for creating and editing job alerts."""
    
    class Meta:
        model = JobAlert
        fields = [
            'alert_name', 'job_title', 'location', 'job_type', 
            'job_category', 'min_salary', 'max_salary', 'keywords', 'is_active'
        ]
        widgets = {
            'alert_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Frontend Developer Jobs',
                'id': 'alert_name',
                'required': True
            }),
            'job_title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Software Engineer, Developer',
                'id': 'job_title'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., New York, Remote',
                'id': 'location'
            }),
            'job_type': forms.Select(attrs={
                'class': 'form-control',
                'id': 'job_type'
            }),
            'job_category': forms.Select(attrs={
                'class': 'form-control',
                'id': 'job_category'
            }),
            'min_salary': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Minimum salary',
                'id': 'min_salary',
                'min': '0'
            }),
            'max_salary': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Maximum salary',
                'id': 'max_salary',
                'min': '0'
            }),
            'keywords': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Python, React, AWS (comma-separated)',
                'id': 'keywords'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
                'id': 'is_active'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set querysets for FK fields to only show active options
        from .models import JobCategory, EmploymentType
        
        self.fields['job_type'].queryset = EmploymentType.objects.filter(is_active=True)
        self.fields['job_type'].empty_label = "Any Employment Type"
        
        self.fields['job_category'].queryset = JobCategory.objects.filter(is_active=True)
        self.fields['job_category'].empty_label = "Any Category"
    
    def clean_alert_name(self):
        """Validate alert name."""
        alert_name = self.cleaned_data.get('alert_name')
        if not alert_name or not alert_name.strip():
            raise ValidationError('Alert name is required.')
        if len(alert_name) > 100:
            raise ValidationError('Alert name cannot exceed 100 characters.')
        return alert_name.strip()
    
    def clean_job_title(self):
        """Validate and clean job title."""
        job_title = self.cleaned_data.get('job_title')
        if job_title:
            job_title = job_title.strip()
            if len(job_title) > 200:
                raise ValidationError('Job title cannot exceed 200 characters.')
        return job_title or ''
    
    def clean_location(self):
        """Validate and clean location."""
        location = self.cleaned_data.get('location')
        if location:
            location = location.strip()
            if len(location) > 200:
                raise ValidationError('Location cannot exceed 200 characters.')
        return location or ''
    
    def clean_keywords(self):
        """Validate and clean keywords."""
        keywords = self.cleaned_data.get('keywords')
        if keywords:
            keywords = keywords.strip()
            if len(keywords) > 500:
                raise ValidationError('Keywords cannot exceed 500 characters.')
        return keywords or ''
    
    def clean(self):
        """Additional validation for salary range."""
        cleaned_data = super().clean()
        min_salary = cleaned_data.get('min_salary')
        max_salary = cleaned_data.get('max_salary')
        
        # Validate salary range
        if min_salary is not None and min_salary < 0:
            self.add_error('min_salary', 'Minimum salary cannot be negative.')
        
        if max_salary is not None and max_salary < 0:
            self.add_error('max_salary', 'Maximum salary cannot be negative.')
        
        if min_salary and max_salary and min_salary > max_salary:
            self.add_error('min_salary', 'Minimum salary cannot be greater than maximum salary.')
        
        # Ensure at least one filter criterion is provided
        if not any([
            cleaned_data.get('job_title'),
            cleaned_data.get('location'),
            cleaned_data.get('job_type'),
            cleaned_data.get('job_category'),
            cleaned_data.get('min_salary'),
            cleaned_data.get('max_salary'),
            cleaned_data.get('keywords')
        ]):
            raise ValidationError('Please specify at least one filter criterion for this alert.')
        
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
        from resumes.models import Resume
        
        resume_id = self.cleaned_data.get('resume_id')
        
        if not resume_id:
            raise ValidationError('Please select a resume to submit with your application.')
        
        try:
            resume = Resume.objects.get(id=resume_id, user=self.user)
            self.cleaned_data['resume'] = resume
        except Resume.DoesNotExist:
            raise ValidationError('Selected resume not found or does not belong to you.')
        
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