from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.mail import send_mail
from django.db.models import Count

from jobs.models import Job, JobCategory, Application
from accounts.models import Profile, Company


# ===================== ROLE REDIRECT =====================

@login_required
def role_redirect(request):
    role = request.user.profile.role

    if role == 'admin':
        return redirect('admin_dashboard')
    elif role == 'company':
        return redirect('company_dashboard')
    else:
        return redirect('user_dashboard')


# ===================== USER VIEWS =====================

@login_required
def user_dashboard(request):
    apps = Application.objects.filter(user=request.user)
    return render(request, 'user/dashboard.html', {'applications': apps})


@login_required
def user_job_list(request):
    jobs = Job.objects.all().order_by('-id')
    return render(request, 'user/job_list.html', {'jobs': jobs})


@login_required
def user_job_detail(request, pk):
    job = get_object_or_404(Job, pk=pk)
    return render(request, 'user/job_detail.html', {'job': job})


@login_required
def user_apply_job(request, pk):
    job = get_object_or_404(Job, pk=pk)

    if request.method == 'POST':
        resume = request.FILES.get('resume')
        cover_letter = request.POST.get('cover_letter', '')

        Application.objects.create(
            job=job,
            user=request.user,
            resume=resume,
            cover_letter=cover_letter
        )

        messages.success(request, 'Application submitted successfully.')
        return redirect('user_dashboard')

    return render(request, 'user/apply_job.html', {'job': job})


@login_required
def user_applications(request):
    apps = Application.objects.filter(user=request.user)
    return render(request, 'user/application_status.html', {'applications': apps})


# ===================== ADMIN SECURITY DECORATOR =====================

def admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.profile.role != "admin":
            return redirect("login")
        return view_func(request, *args, **kwargs)
    return wrapper


# ===================== ADMIN VIEWS =====================

@admin_required
def admin_dashboard(request):
    return render(request, 'admin/dashboard.html', {
        'total_users': User.objects.count(),
        'total_companies': Company.objects.count(),
        'total_jobs': Job.objects.count(),
        'total_apps': Application.objects.count(),
    })


@admin_required
def admin_users(request):
    users = Profile.objects.filter(role="user")
    return render(request, 'admin/users.html', {'users': users})


@admin_required
def admin_companies(request):
    companies = Company.objects.all()
    return render(request, 'admin/companies.html', {'companies': companies})


@admin_required
def admin_job_list(request):
    jobs = Job.objects.all()
    return render(request, 'admin/job_list.html', {'jobs': jobs})


@admin_required
def admin_delete_job(request, pk):
    job = get_object_or_404(Job, pk=pk)
    job.delete()
    messages.success(request, 'Job deleted successfully.')
    return redirect('admin_job_list')


@admin_required
def admin_applications(request):
    apps = Application.objects.select_related('job', 'user')
    return render(request, 'admin/applications.html', {'applications': apps})


# ===================== COMPANY VIEWS =====================

@login_required
def company_dashboard(request):
    if request.user.profile.role != "company":
        return redirect("role_redirect")

    company = Company.objects.get(user=request.user)
    jobs = Job.objects.filter(company=company)

    total_apps = Application.objects.filter(job__in=jobs).count()
    pending = Application.objects.filter(job__in=jobs, status="pending").count()
    approved = Application.objects.filter(job__in=jobs, status="approved").count()

    return render(request, "company/dashboard.html", {
        "company": company,
        "jobs": jobs,
        "total_apps": total_apps,
        "pending": pending,
        "approved": approved,
    })


@login_required
def company_post_job(request):
    if request.user.profile.role != "company":
        return redirect("role_redirect")

    categories = JobCategory.objects.all()
    company = Company.objects.get(user=request.user)

    if request.method == "POST":
        Job.objects.create(
            company=company,
            title=request.POST["title"],
            description=request.POST["description"],
            location=request.POST["location"],
            salary=request.POST["salary"],
            category_id=request.POST.get("category")
        )

        messages.success(request, "Job posted successfully.")
        return redirect("company_jobs")

    return render(request, "company/post_job.html", {"categories": categories})


@login_required
def company_jobs(request):
    company = Company.objects.get(user=request.user)
    jobs = Job.objects.filter(company=company)
    return render(request, "company/jobs.html", {"jobs": jobs})


@login_required
def company_applications(request, job_id):
    job = get_object_or_404(Job, id=job_id)

    if job.company.user != request.user:
        return redirect("role_redirect")

    apps = Application.objects.filter(job=job)
    return render(request, "company/applications.html", {"job": job, "applications": apps})


@login_required
def company_approve(request, app_id):
    app = get_object_or_404(Application, id=app_id)

    if app.job.company.user != request.user:
        return redirect("role_redirect")

    app.status = "approved"
    app.save()
    messages.success(request, "Application approved.")
    return redirect("company_applications", job_id=app.job.id)


@login_required
def company_reject(request, app_id):
    app = get_object_or_404(Application, id=app_id)

    if app.job.company.user != request.user:
        return redirect("role_redirect")

    app.status = "rejected"
    app.save()
    messages.success(request, "Application rejected.")
    return redirect("company_applications", job_id=app.job.id)

from django.db.models import Q
from .models import Job

@login_required
def user_job_list(request):
    query = request.GET.get("q", "")

    jobs = Job.objects.all()

    if query:
        jobs = jobs.filter(
            Q(title__icontains=query) |
            Q(company__company_name__icontains=query) |
            Q(location__icontains=query) |
            Q(category__name__icontains=query)
        )

    return render(request, "user/job_list.html", {
        "jobs": jobs,
        "query": query,
    })

@login_required
def user_job_detail(request, job_id):
    job = get_object_or_404(Job, id=job_id)

    # Check if already applied
    already_applied = Application.objects.filter(job=job, user=request.user).exists()

    return render(request, "user/job_detail.html", {
        "job": job,
        "already_applied": already_applied
    })

@login_required
def apply_job(request, job_id):
    job = get_object_or_404(Job, id=job_id)

    # Prevent duplicate apply
    if Application.objects.filter(job=job, user=request.user).exists():
        messages.warning(request, "You have already applied for this job.")
        return redirect("user_job_detail", job_id=job.id)

    if request.method == "POST":
        Application.objects.create(
            job=job,
            user=request.user,
            resume=request.FILES.get("resume"),
            cover_letter=request.POST.get("cover_letter")
        )

        messages.success(request, "Application submitted successfully!")
        return redirect("user_applications")

    return redirect("user_job_detail", job_id=job.id)

