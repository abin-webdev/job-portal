from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings

from accounts.forms import UserUpdateForm, ProfileUpdateForm

from .forms import RegisterForm,CompanyRegisterForm
from .models import Profile, Company
from jobs.models import Job, Application, JobCategory


# ================= LOGIN =================
def login_view(request):
    if request.user.is_authenticated:
        return redirect("role_redirect")

    if request.method == "POST":
        user = authenticate(
            request,
            username=request.POST.get("username"),
            password=request.POST.get("password"),
        )
        if user:
            login(request, user)
            return redirect("role_redirect")
        messages.error(request, "Invalid username or password")

    return render(request, "user/login.html")


# ================= REGISTER =================
def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)

        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data["password"])
            user.save()

            # profile MUST exist
            profile = user.profile
            profile.role = form.cleaned_data["role"]
            profile.save()

            # 🔥 IMPORTANT: company redirect
            if profile.role == "company":
                request.session["new_company_user"] = user.id
                return redirect("company_register")

            messages.success(request, "Registration successful. Please login.")
            return redirect("login")

    else:
        form = RegisterForm()

    return render(request, "user/register.html", {"form": form})




# ================= LOGOUT =================
@login_required
def logout_view(request):
    logout(request)
    return redirect("login")


# ================= ROLE REDIRECT =================
@login_required
def role_redirect(request):
    role = request.user.profile.role

    if role == "admin":
        return redirect("admin_dashboard")
    elif role == "company":
        return redirect("company_dashboard")
    return redirect("user_dashboard")




# ================= COMPANY REGISTER =================
def company_register(request):
    user_id = request.session.get("new_company_user")

    if not user_id:
        return redirect("register")

    user = get_object_or_404(User, id=user_id)

    form = CompanyRegisterForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        company = form.save(commit=False)
        company.user = user
        company.save()

        del request.session["new_company_user"]
        messages.success(request, "Company registered successfully.")
        return redirect("login")

    return render(
        request,
        "company/company_register.html",
        {"form": form}
    )



# ================= USER =================
@login_required
def user_dashboard(request):
    applications = Application.objects.filter(user=request.user)
    return render(request, "user/dashboard.html", {"applications": applications})


@login_required
def user_applications(request):
    applications = Application.objects.filter(user=request.user)
    return render(request, "user/application_status.html", {"applications": applications})


@login_required
def user_job_list(request):
    jobs = Job.objects.all().order_by("-created_at")
    return render(request, "user/job_list.html", {"jobs": jobs})


@login_required
def apply_job(request, job_id):
    job = get_object_or_404(Job, id=job_id)

    if Application.objects.filter(job=job, user=request.user).exists():
        messages.warning(request, "You already applied for this job.")
        return redirect("user_job_list")

    Application.objects.create(job=job, user=request.user, status="pending")
    messages.success(request, "Application submitted successfully.")
    return redirect("user_applications")


# ================= COMPANY =================
@login_required
def company_dashboard(request):
    if request.user.profile.role != "company":
        return redirect("role_redirect")

    company = get_object_or_404(Company, user=request.user)
    jobs = Job.objects.filter(company=company)

    context = {
        "company": company,
        "total_jobs": jobs.count(),
        "total_applications": Application.objects.filter(job__in=jobs).count(),
        "pending_apps": Application.objects.filter(job__in=jobs, status="pending").count(),
        "approved_apps": Application.objects.filter(job__in=jobs, status="approved").count(),
    }

    return render(request, "company/dashboard.html", context)


@login_required
def company_jobs(request):
    if request.user.profile.role != "company":
        return redirect("role_redirect")

    company = get_object_or_404(Company, user=request.user)
    jobs = Job.objects.filter(company=company)
    return render(request, "company/jobs.html", {"jobs": jobs})


@login_required
def company_post_job(request):
    if request.user.profile.role != "company":
        return redirect("role_redirect")

    categories = JobCategory.objects.all()
    company = get_object_or_404(Company, user=request.user)

    if request.method == "POST":
        Job.objects.create(
            company=company,
            title=request.POST.get("title"),
            description=request.POST.get("description"),
            location=request.POST.get("location"),
            salary=request.POST.get("salary"),
            category_id=request.POST.get("category"),
        )
        messages.success(request, "Job posted successfully.")
        return redirect("company_jobs")

    return render(request, "company/post_job.html", {"categories": categories})


@login_required
def company_applications(request, job_id):
    job = get_object_or_404(Job, id=job_id, company__user=request.user)
    applications = Application.objects.filter(job=job)
    return render(
        request,
        "company/applications.html",
        {"job": job, "applications": applications},
    )


# ================= APPROVE / REJECT (EMAIL) =================
@login_required
def company_approve(request, app_id):
    application = get_object_or_404(
        Application,
        id=app_id,
        job__company__user=request.user
    )

    # Update status
    application.status = "approved"
    application.save()

    # Email content
    subject = f"🎉 Application Approved – {application.job.title}"

    message = f"""
Dear {application.user.username},

Congratulations!

We are pleased to inform you that your application for the position of
"{application.job.title}" at "{application.job.company.company_name}"
has been successfully reviewed and approved.

Our hiring team was impressed with your profile and qualifications.
The next steps of the recruitment process will be shared with you shortly.

If you have any questions, feel free to reply to this email.

We wish you all the best and look forward to connecting with you.

Warm regards,
{application.job.company.company_name}
HR Team
"""

    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[application.user.email],
        fail_silently=False,
    )

    messages.success(request, "Application approved and email sent successfully.")
    return redirect("company_applications", job_id=application.job.id)



@login_required
def company_reject(request, app_id):
    application = get_object_or_404(
        Application,
        id=app_id,
        job__company__user=request.user
    )

    # Update status
    application.status = "rejected"
    application.save()

    # Email content
    subject = f"Application Update – {application.job.title}"

    message = f"""
Dear {application.user.username},

Thank you for taking the time to apply for the position of
"{application.job.title}" at "{application.job.company.company_name}".

After careful review of your application, we regret to inform you that
we will not be moving forward with your candidature at this time.

Please note that this decision does not reflect your abilities or potential.
We received many applications and had to make a difficult choice.

We truly appreciate your interest in our company and encourage you to
apply for future opportunities that match your skills and experience.

We wish you every success in your job search.

Kind regards,
{application.job.company.company_name}
HR Team
"""

    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[application.user.email],
        fail_silently=False,
    )

    messages.success(request, "Application rejected and email sent successfully.")
    return redirect("company_applications", job_id=application.job.id)



# ================= ADMIN =================
@login_required
def admin_dashboard(request):
    if request.user.profile.role != "admin":
        return redirect("role_redirect")

    context = {
        "total_users": Profile.objects.filter(role="user").count(),
        "total_companies": Profile.objects.filter(role="company").count(),
        "total_jobs": Job.objects.count(),
        "total_applications": Application.objects.count(),
    }

    return render(request, "admin/dashboard.html", context)


@login_required
def admin_users(request):
    if request.user.profile.role != "admin":
        return redirect("role_redirect")

    users = User.objects.filter(profile__role="user")
    return render(request, "admin/users.html", {"users": users})


@login_required
def admin_delete_user(request, user_id):
    if request.user.profile.role != "admin":
        return redirect("role_redirect")

    user = get_object_or_404(User, id=user_id)
    user.delete()
    messages.success(request, "User deleted.")
    return redirect("admin_users")


@login_required
def admin_companies(request):
    if request.user.profile.role != "admin":
        return redirect("role_redirect")

    companies = Company.objects.all()
    return render(request, "admin/companies.html", {"companies": companies})


@login_required
def admin_delete_company(request, company_id):
    if request.user.profile.role != "admin":
        return redirect("role_redirect")

    company = get_object_or_404(Company, id=company_id)
    user = company.user
    company.delete()
    user.delete()

    messages.success(request, "Company deleted.")
    return redirect("admin_companies")


@login_required
def admin_job_list(request):
    if request.user.profile.role != "admin":
        return redirect("role_redirect")

    jobs = Job.objects.select_related("company").all()
    return render(request, "admin/job_list.html", {"jobs": jobs})

@login_required
def company_application_detail(request, app_id):
    app = get_object_or_404(Application, id=app_id)

    return render(
        request,
        "company/application_detail.html",
        {
            "app": app,          # ✅ MUST exist
            "job": app.job       # ✅ optional but helpful
        }
    )

    return render(
        request,
        "company/application_detail.html",
        {"application": application}
    )

@login_required
def admin_delete_job(request, pk):
    if request.user.profile.role != "admin":
        return redirect("role_redirect")

    job = get_object_or_404(Job, id=pk)
    job.delete()

    messages.success(request, "Job deleted successfully.")
    return redirect("admin_job_list")

@login_required
def admin_applications(request):
    if request.user.profile.role != "admin":
        return redirect("role_redirect")

    applications = Application.objects.select_related(
        "job", "user", "job__company"
    ).order_by("-applied_at")

    return render(
        request,
        "admin/applications.html",
        {"applications": applications}
    )


@login_required
def company_dashboard(request):
    if request.user.profile.role != "company":
        return redirect("role_redirect")

    company, created = Company.objects.get_or_create(
        user=request.user,
        defaults={
            "company_name": "Your Company",
            "phone": "",
            "location": "",
            "description": ""
        }
    )

    jobs = Job.objects.filter(company=company)

    context = {
        "company": company,
        "total_jobs": jobs.count(),
        "total_applications": Application.objects.filter(job__in=jobs).count(),
        "pending_apps": Application.objects.filter(job__in=jobs, status="pending").count(),
        "approved_apps": Application.objects.filter(job__in=jobs, status="approved").count(),
    }

    return render(request, "company/dashboard.html", context)


@login_required
def admin_delete_company(request, company_id):
    if request.user.profile.role != "admin":
        return redirect("role_redirect")

    company = get_object_or_404(Company, id=company_id)

    if request.method == "POST":
        user = company.user
        company.delete()
        user.delete()
        messages.success(request, "Company deleted successfully.")

    return redirect("admin_companies")



# ================= PROFILE UPDATE =================

@login_required
def edit_profile(request):

    if request.method == "POST":
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(
            request.POST,
            request.FILES,
            instance=request.user.profile
        )

        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            return redirect('user_profile')

    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    return render(request, 'user/edit_profile.html', {
        'u_form': u_form,
        'p_form': p_form
    })