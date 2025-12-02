from django import forms
from .models import Resume

class ResumeUploadForm(forms.ModelForm):
    class Meta:
        model = Resume
        fields = ['name', 'file', 'is_default']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Software Engineer Resume',
                'required': True
            }),
            'file': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.doc,.docx',
                'required': True
            }),
            'is_default': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
        labels = {
            'name': 'Resume Name',
            'file': 'Resume File (PDF, DOC, DOCX)',
            'is_default': 'Set as default resume'
        }
        help_texts = {
            'name': 'Give your resume a descriptive name',
            'file': 'Upload your resume (max 5MB)',
            'is_default': 'This resume will be pre-selected when applying to jobs'
        }
    
    def clean_name(self):
        name = self.cleaned_data.get('name')
        if name:
            name = name.strip()
            if not name:
                raise forms.ValidationError('Resume name cannot be empty.')
            if len(name) < 3:
                raise forms.ValidationError('Resume name must be at least 3 characters long.')
            if len(name) > 100:
                raise forms.ValidationError('Resume name must not exceed 100 characters.')
        return name
    
    def clean_file(self):
        file = self.cleaned_data.get('file')
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
