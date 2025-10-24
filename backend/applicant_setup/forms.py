from django import forms
from accounts.models import ApplicantProfile 

class PersonalInfoForm(forms.ModelForm):
    class Meta:
        model = ApplicantProfile
        fields = ['contact_number', 'location']
        widgets = {
            'contact_number': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'e.g., 09123456789'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'e.g., Cebu City, PH'
            }),
        }

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
            
            'resume': forms.FileInput(),
        }
        
    def clean_resume(self):
        """Custom validator to check the resume file size."""
        resume = self.cleaned_data.get('resume', False)
        if resume:
            if resume.size > 5 * 1024 * 1024:
                raise forms.ValidationError("Resume file cannot be larger than 5MB.")
        elif not self.instance.resume: 
             raise forms.ValidationError("Uploading a resume is required.")
        return resume