from django import forms
from accounts.models import ApplicantProfile # Correctly import from your accounts app

# Form for Step 1: Personal Information
class PersonalInfoForm(forms.ModelForm):
    class Meta:
        model = ApplicantProfile
        fields = ['first_name', 'middle_name', 'last_name', 'contact_number', 'location']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'e.g., Juan'
            }),
            'middle_name': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'e.g., Santos (Optional)'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'e.g., Dela Cruz'
            }),
            'contact_number': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'e.g., 09123456789'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'e.g., Cebu City, PH'
            }),
        }
        labels = {
            'first_name': 'First Name',
            'middle_name': 'Middle Name (Optional)',
            'last_name': 'Last Name',
            'contact_number': 'Contact Number (10+ digits)',
            'location': 'Current Location (City, Country)'
        }

# Form for Step 2: Education Details
class EducationForm(forms.ModelForm):
    class Meta:
        model = ApplicantProfile
        fields = ['school_name', 'degree', 'year_level']
        widgets = {
            'school_name': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'e.g., University of San Carlos'
            }),
            'degree': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'e.g., BS in Computer Science'
            }),
            'year_level': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'e.g., 4th Year'
            }),
        }

# Form for Step 3: Skills and Resume
class SkillsResumeForm(forms.ModelForm):
    class Meta:
        model = ApplicantProfile
        fields = ['skills_summary', 'resume']
        widgets = {
            'skills_summary': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Enter your skills separated by commas...'
            }),
            # The actual file input is styled via the label in your HTML
            'resume': forms.FileInput(),
        }
        
    def clean_resume(self):
        """Custom validator to check the resume file size."""
        resume = self.cleaned_data.get('resume', False)
        if resume:
            # 5MB size limit
            if resume.size > 5 * 1024 * 1024:
                raise forms.ValidationError("Resume file cannot be larger than 5MB.")
        elif not self.instance.resume: # Check if a resume is already uploaded
             raise forms.ValidationError("Uploading a resume is required.")
        return resume