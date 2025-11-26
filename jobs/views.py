from django.shortcuts import render
from django.http import JsonResponse
from .models import Job
from .forms import JobSearchForm
from django.db.models import Q

def job_search(request):

    # GET parameters
    query = request.GET.get("query", "")
    location = request.GET.get("location", "")
    job_types = request.GET.getlist("job_type")     # Multiple checkboxes
    categories = request.GET.getlist("category")    # Multi-select (job categories)
    educations = request.GET.getlist("education")  # Multi-select
    experiences = request.GET.getlist("experience")
    job_levels = request.GET.getlist("job_level")
    salary_min = request.GET.get("salary_min")
    salary_max = request.GET.get("salary_max")

    # Start with all jobs
    jobs = Job.objects.all()

    # 🔍 Keyword search
    if query:
        jobs = jobs.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query)
        )

    # 📍 Location filter
    if location:
        jobs = jobs.filter(location__icontains=location)

    # 🧩 Job type (checkbox)
    if job_types:
        jobs = jobs.filter(job_type__in=job_types)

    # 🧩 Job category (replaces job_role)
    if categories:
        jobs = jobs.filter(category__id__in=categories)

    # 🧩 Education level
    if educations:
        jobs = jobs.filter(education__in=educations)

    # 🧩 Experience
    if experiences:
        jobs = jobs.filter(experience__in=experiences)

    # 🧩 Job level
    if job_levels:
        jobs = jobs.filter(job_level__in=job_levels)

    # 💰 Salary filter
    if salary_min:
        jobs = jobs.filter(salary_min__gte=salary_min)

    if salary_max:
        jobs = jobs.filter(salary_max__lte=salary_max)

    # DYNAMIC FILTER VALUES (from lookup tables)
    from .lookup_models import JobCategory, EmploymentType, EducationLevel, ExperienceLevel, JobLevel
    
    all_job_types = Job.JOB_TYPES  # Keep for backward compatibility during migration
    all_categories = JobCategory.objects.filter(is_active=True).values_list('id', 'name')
    all_educations = Job.EDUCATION_LEVELS  # Keep for backward compatibility during migration
    all_experiences = Job.EXPERIENCE_LEVELS  # Keep for backward compatibility during migration
    all_job_levels = Job.JOB_LEVELS  # Keep for backward compatibility during migration
    all_locations = Job.objects.values_list("location", flat=True).distinct()

    context = {
        "jobs": jobs,
        "query": query,
        "location": location,
        "salary_min": salary_min,
        "salary_max": salary_max,

        # Dynamic filters
        "job_types": all_job_types,
        "categories": all_categories,  # Renamed from job_roles
        "educations": all_educations,
        "experiences": all_experiences,
        "job_levels": all_job_levels,
        "locations": all_locations,

        # Persist selected values
        "selected_job_types": job_types,
        "selected_categories": categories,  # Renamed from selected_job_roles
        "selected_educations": educations,
        "selected_experiences": experiences,
        "selected_job_levels": job_levels,
    }

    return render(request, "jobs/job_search.html", context)

def job_suggestions(request):
    term = request.GET.get("term", "")
    if len(term) < 3:
        return JsonResponse([], safe=False)

    qs = Job.objects.filter(title__icontains=term)
    suggestions = list(qs.values_list("title", flat=True)[:8])
    return JsonResponse(suggestions, safe=False)