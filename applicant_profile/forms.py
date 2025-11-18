from django import forms
from accounts.models import ApplicantProfile 

# Form for Step 1: Personal Information
class PersonalInfoForm(forms.ModelForm):
    class Meta:
        model = ApplicantProfile
        fields = ['first_name', 'middle_name', 'last_name', 'contact_number', 'location']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'e.g., Juan',
                'required': 'required'
            }),
            'middle_name': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'e.g., Santos (Optional)'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'e.g., Dela Cruz',
                'required': 'required'
            }),
            'contact_number': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'e.g., 09123456789',
                'required': 'required'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'e.g., Cebu City, PH',
                'required': 'required'
            }),
        }
        labels = {
            'first_name': 'First Name *',
            'middle_name': 'Middle Name (Optional)',
            'last_name': 'Last Name *',
            'contact_number': 'Contact Number (10+ digits) *',
            'location': 'Current Location (City, Country) *'
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['contact_number'].required = True
        self.fields['location'].required = True
        self.fields['middle_name'].required = False
    
    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name', '').strip()
        if not first_name:
            raise forms.ValidationError("First name is required.")
        if len(first_name) < 2:
            raise forms.ValidationError("First name must be at least 2 characters long.")
        if not all(c.isalpha() or c.isspace() or c == '-' for c in first_name):
            raise forms.ValidationError("First name can only contain letters, spaces, and hyphens.")
        return first_name
    
    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name', '').strip()
        if not last_name:
            raise forms.ValidationError("Last name is required.")
        if len(last_name) < 2:
            raise forms.ValidationError("Last name must be at least 2 characters long.")
        if not all(c.isalpha() or c.isspace() or c == '-' for c in last_name):
            raise forms.ValidationError("Last name can only contain letters, spaces, and hyphens.")
        return last_name
    
    def clean_contact_number(self):
        contact_number = self.cleaned_data.get('contact_number', '').strip()
        if not contact_number:
            raise forms.ValidationError("Contact number is required.")
        
        digits_only = ''.join(c for c in contact_number if c.isdigit())
        if len(digits_only) < 10:
            raise forms.ValidationError("Contact number must be at least 10 digits.")
        if len(digits_only) > 15:
            raise forms.ValidationError("Contact number cannot exceed 15 digits.")
        return contact_number
    
    def clean_location(self):
        location = self.cleaned_data.get('location', '').strip()
        if not location:
            raise forms.ValidationError("Location is required.")
        if len(location) < 3:
            raise forms.ValidationError("Please provide a valid location (e.g., Cebu City, PH).")
        return location

class EducationForm(forms.ModelForm):
    class Meta:
        model = ApplicantProfile
        fields = ['school_name', 'degree', 'year_level']
        widgets = {
            'school_name': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'e.g., University of San Carlos',
                'required': 'required'
            }),
            'degree': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'e.g., BS in Computer Science',
                'required': 'required'
            }),
            'year_level': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'e.g., 4th Year',
                'required': 'required'
            }),
        }
        labels = {
            'school_name': 'School Name *',
            'degree': 'Degree/Course *',
            'year_level': 'Year Level *'
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.fields['school_name'].required = True
        self.fields['degree'].required = True
        self.fields['year_level'].required = True
    
    def clean_school_name(self):
        school_name = self.cleaned_data.get('school_name', '').strip()
        if not school_name:
            raise forms.ValidationError("School/University name is required.")
        if len(school_name) < 3:
            raise forms.ValidationError("School name must be at least 3 characters long.")
        return school_name
    
    def clean_degree(self):
        degree = self.cleaned_data.get('degree', '').strip()
        if not degree:
            raise forms.ValidationError("Degree/Course is required.")
        if len(degree) < 2:
            raise forms.ValidationError("Degree/Course must be at least 2 characters long.")
        return degree
    
    def clean_year_level(self):
        year_level = self.cleaned_data.get('year_level', '').strip()
        if not year_level:
            raise forms.ValidationError("Year level is required.")
        return year_level

# Form for Step 3: Skills and Resume
class SkillsResumeForm(forms.ModelForm):
    class Meta:
        model = ApplicantProfile
        fields = ['skills_summary', 'resume']
        widgets = {
            'skills_summary': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Enter your skills separated by commas...',
                'required': 'required'
            }),
            
            'resume': forms.FileInput(attrs={'required': 'required'}),
        }
        labels = {
            'skills_summary': 'Skills Summary *',
            'resume': 'Upload Resume (PDF, DOC, DOCX - Max 5MB) *'
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)        # Make fields required for new profiles
        self.fields['skills_summary'].required = True
        
        if self.instance and self.instance.pk and self.instance.resume:
            self.fields['resume'].required = False
        else:
            self.fields['resume'].required = True
    
    def clean_skills_summary(self):
        skills_summary = self.cleaned_data.get('skills_summary', '').strip()
        if not skills_summary:
            raise forms.ValidationError("Skills summary is required.")
        if len(skills_summary) < 10:
            raise forms.ValidationError("Please provide a more detailed skills summary (at least 10 characters).")
        
        skills_list = [s.strip() for s in skills_summary.split(',') if s.strip()]
        if len(skills_list) < 1:
            raise forms.ValidationError("Please provide at least one skill.")
        return skills_summary
        
    def clean_resume(self):
        
        resume = self.cleaned_data.get('resume', False)
        
        if resume:
            if resume.size > 5 * 1024 * 1024:
                raise forms.ValidationError("Resume file cannot be larger than 5MB.")
            
            allowed_extensions = ['pdf', 'doc', 'docx']
            file_extension = resume.name.split('.')[-1].lower()
            if file_extension not in allowed_extensions:
                raise forms.ValidationError(f"Only {', '.join(allowed_extensions).upper()} files are allowed.")
        elif not self.instance.resume:
            raise forms.ValidationError("Uploading a resume is required.")
        
        return resume