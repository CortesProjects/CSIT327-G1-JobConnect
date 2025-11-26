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