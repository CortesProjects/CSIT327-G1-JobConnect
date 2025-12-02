from django import forms
from applicant_profile.models import ApplicantProfile 

# Form for Step 1: Personal Information
class PersonalInfoForm(forms.ModelForm):
    class Meta:
        model = ApplicantProfile
        fields = ['profile_image', 'title', 'first_name', 'middle_name', 'last_name', 'experience', 'education_level']
        widgets = {
            'profile_image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Software Developer, Marketing Specialist'
            }),
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
            'experience': forms.Select(attrs={
                'class': 'form-control',
            }),
            'education_level': forms.Select(attrs={
                'class': 'form-control',
                'required': 'required'
            }),
        }
        labels = {
            'profile_image': 'Profile Picture (Optional)',
            'title': 'Professional Title/Headline',
            'first_name': 'First Name *',
            'middle_name': 'Middle Name (Optional)',
            'last_name': 'Last Name *',
            'experience': 'Years of Experience *',
            'education_level': 'Education Level *',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['middle_name'].required = False
        self.fields['profile_image'].required = False
        self.fields['title'].required = False
        self.fields['experience'].required = True
        self.fields['education_level'].required = True
    
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
    

class ProfileDetailsForm(forms.ModelForm):
    class Meta:
        model = ApplicantProfile
        fields = [
            'nationality', 'date_of_birth', 'gender', 'marital_status', 'location_street','location_city','location_country', 'biography'
        ]
        widgets = {
            'nationality': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Filipino'
            }),
            'date_of_birth': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'required': 'required'
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
                'rows': 5,
                'placeholder': 'Tell employers about yourself, your experience, and career goals...'
            }),
        }
        labels = {
            'nationality': 'Nationality',
            'date_of_birth': 'Date of Birth *',
            'gender': 'Gender',
            'marital_status': 'Marital Status',
            'location_street': 'Street Address',
            'location_city': 'City',
            'location_country': 'Country',
            'biography': 'Biography'
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.fields['nationality'].required = False
        self.fields['date_of_birth'].required = True
        self.fields['gender'].required = False
        self.fields['marital_status'].required = False
        self.fields['biography'].required = False
    
    def clean_date_of_birth(self):
        from datetime import date
        dob = self.cleaned_data.get('date_of_birth')
        if not dob:
            raise forms.ValidationError("Date of birth is required.")
        
        today = date.today()
        age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        
        if age < 16:
            raise forms.ValidationError("You must be at least 16 years old to register.")
        if age > 100:
            raise forms.ValidationError("Please enter a valid date of birth.")
        
        # Ensure date is not in the future
        if dob > today:
            raise forms.ValidationError("Date of birth cannot be in the future.")
        
        return dob
    

# Form for Step 3: Contact Information and Resume
class ContactInfoForm(forms.ModelForm):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'readonly': 'readonly',
            'style': 'background-color: #f0f0f0; cursor: not-allowed;'
        }),
        label='Email *',
        required=True
    )
    
    class Meta:
        model = ApplicantProfile
        fields = ['contact_number']
        widgets = {
            'contact_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 09123456789',
                'required': 'required'
            }),
        }
        labels = {
            'contact_number': 'Phone *'
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Set email from user instance if available
        if self.instance and self.instance.user:
            self.fields['email'].initial = self.instance.user.email
        
        self.fields['contact_number'].required = True
       
    
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


# Form for Step 4: Resume Upload (using new Resume model)
class ResumeUploadSetupForm(forms.Form):
    """Form for uploading first resume during profile setup."""
    resume_name = forms.CharField(
        max_length=255,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., Software Engineer Resume',
        }),
        label='Resume Name *',
        help_text='Give your resume a descriptive name'
    )
    
    resume_file = forms.FileField(
        required=True,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.pdf,.doc,.docx'
        }),
        label='Resume File (PDF, DOC, DOCX) *',
        help_text='Upload your resume (max 5MB)'
    )
    
    set_as_default = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
            'checked': 'checked'
        }),
        label='Set as default resume',
        help_text='This resume will be pre-selected when applying to jobs'
    )
    
    def clean_resume_name(self):
        name = self.cleaned_data.get('resume_name', '').strip()
        if not name:
            raise forms.ValidationError('Resume name cannot be empty.')
        if len(name) < 3:
            raise forms.ValidationError('Resume name must be at least 3 characters long.')
        if len(name) > 100:
            raise forms.ValidationError('Resume name must not exceed 100 characters.')
        return name
    
    def clean_resume_file(self):
        file = self.cleaned_data.get('resume_file')
        if not file:
            raise forms.ValidationError('Please select a file to upload.')
        
        # Check file size (5MB limit)
        if file.size > 5 * 1024 * 1024:
            file_size_mb = round(file.size / (1024 * 1024), 2)
            raise forms.ValidationError(f'File size ({file_size_mb}MB) exceeds the 5MB limit.')
        
        # Check file extension
        allowed_extensions = ['.pdf', '.doc', '.docx']
        file_extension = f'.{file.name.lower().split(".")[-1]}'
        if file_extension not in allowed_extensions:
            raise forms.ValidationError(f'File type "{file_extension}" is not allowed. Only PDF, DOC, and DOCX files are accepted.')
        
        return file
    