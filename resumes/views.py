from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import Resume
from .forms import ResumeUploadForm

@login_required
def upload_resume(request):
    """Upload a new resume."""
    if request.user.user_type != 'applicant':
        messages.error(request, 'Only applicants can upload resumes.')
        return redirect('dashboard:dashboard')
    
    if request.method == 'POST':
        form = ResumeUploadForm(request.POST, request.FILES)
        if form.is_valid():
            resume = form.save(commit=False)
            resume.user = request.user
            resume.save()
            messages.success(request, f'Resume "{resume.name}" uploaded successfully!')
            return redirect('dashboard:applicant_settings' + '#personal')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
            return redirect('dashboard:applicant_settings' + '#personal')
    else:
        form = ResumeUploadForm()
    
    return render(request, 'resumes/upload_resume.html', {'form': form})

@login_required
def delete_resume(request, resume_id):
    """Delete a resume."""
    if request.user.user_type != 'applicant':
        return JsonResponse({'success': False, 'error': 'Unauthorized'}, status=403)
    
    resume = get_object_or_404(Resume, id=resume_id, user=request.user)
    resume_name = resume.name
    resume.file.delete()  # Delete the file from storage
    resume.delete()
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'success': True, 'message': f'Resume "{resume_name}" deleted successfully.'})
    
    messages.success(request, f'Resume "{resume_name}" deleted successfully.')
    return redirect('dashboard:applicant_settings')

@login_required
def set_default_resume(request, resume_id):
    """Set a resume as default."""
    if request.user.user_type != 'applicant':
        return JsonResponse({'success': False, 'error': 'Unauthorized'}, status=403)
    
    resume = get_object_or_404(Resume, id=resume_id, user=request.user)
    
    # Remove default from all other resumes
    Resume.objects.filter(user=request.user, is_default=True).update(is_default=False)
    
    # Set this one as default
    resume.is_default = True
    resume.save()
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'success': True, 'message': f'Resume "{resume.name}" set as default.'})
    
    messages.success(request, f'Resume "{resume.name}" set as default.')
    return redirect('dashboard:applicant_settings')
