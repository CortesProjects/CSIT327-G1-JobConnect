from django import forms
from .models import Job

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

    job_type = forms.MultipleChoiceField(
        choices=Job.JOB_TYPES,
        required=False,
        widget=forms.CheckboxSelectMultiple
    )

    industry = forms.MultipleChoiceField(
        choices=[],  # populated dynamically
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-select'})
    )

    salary_min = forms.IntegerField(required=False)
    salary_max = forms.IntegerField(required=False)