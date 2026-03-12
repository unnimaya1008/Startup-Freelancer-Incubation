from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.contrib import messages
from django.utils import timezone
from django.urls import reverse

from .forms import (
    StartupSignupForm,
    StartupProfileForm,
    ProjectForm,
    EmployeeForm,
    FundingForm,
    MentorshipSessionForm,
    FreelancerRatingForm,
    EmployeeRatingForm,
    MilestoneSetupForm
)
from accounts.supabase_helper import upload_to_supabase
from accounts.models import Notification
from projects.models import Project
from projects.models import Project, ProjectProposal, ProjectAssignment
from projects.proposal_ranker import trigger_proposal_rank_async
from funding.models import FundingRound
from .models import Employee, FreelancerReport, EmployeeRating
from mentors.models import MentorshipSession
from freelancer.models import FreelancerProfile, Milestone
from supabase import create_client
from .helpers import *
# -----------------------------
# Helper Functions
# -----------------------------
def get_supabase_client():
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

# -----------------------------
# 1️⃣ Startup Signup & Profile
# -----------------------------
def startup_signup(request):
    if request.method == 'POST':
        user_form = StartupSignupForm(request.POST)
        profile_form = StartupProfileForm(request.POST, request.FILES)
        if user_form.is_valid() and profile_form.is_valid():
            # Create user
            user = user_form.save(commit=False)
            user.role = 'STARTUP'
            user.save()
            # Create profile
            profile = profile_form.save(commit=False)
            profile.user = user
            logo_file = request.FILES.get('logo')
            if logo_file:
                try:
                    logo_url = upload_to_supabase(logo_file, folder='startups')
                    if logo_url:
                        profile.logo = logo_url
                except Exception as e:
                    print(f"⚠️ Error uploading logo to Supabase: {e}")
            profile.save()
            login(request, user)
            return redirect('startup:startup_dashboard')
        else:
            print("❌ Form errors:", user_form.errors, profile_form.errors)
    else:
        user_form = StartupSignupForm()
        profile_form = StartupProfileForm()
    return render(request, 'signup.html', {'user_form': user_form, 'profile_form': profile_form})

@login_required
def profile_detail(request):
    profile = request.user.startup_profile
    return render(request, 'sprofile_detail.html', {'profile': profile})

@login_required
def profile_edit(request):
    profile = request.user.startup_profile

    if request.method == 'POST':
        form = StartupProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            profile = form.save(commit=False)

            # Optional: upload logo to Supabase (same logic as signup)
            logo_file = request.FILES.get('logo')
            if logo_file:
                try:
                    logo_url = upload_to_supabase(logo_file, folder='startups')
                    if logo_url:
                        profile.logo = logo_url
                except Exception as e:
                    print("Logo upload failed:", e)

            profile.save()
            messages.success(request, "✅ Profile updated successfully")
            return redirect('startup:stprofile_detail')
    else:
        form = StartupProfileForm(instance=profile)

    return render(request, 'sprofile_edit.html', {
        'form': form,
        'profile': profile
    })


# -----------------------------
# 2️⃣ Dashboard
# -----------------------------
@login_required
def startup_dashboard(request):
    profile = request.user.startup_profile
    projects = Project.objects.filter(startup=profile)
    proposals = ProjectProposal.objects.filter(project__startup=profile)
    funding_qs = FundingRound.objects.filter(startup=profile)
    mentorship_qs = MentorshipSession.objects.filter(startup=profile)

    context = {
        'profile': profile,
        'projects_count': projects.count(),
        'projects_open': projects.filter(status='PLANNED').count(),
        'projects_in_progress': projects.filter(status='ONGOING').count(),
        'projects_completed': projects.filter(status='COMPLETED').count(),
        'employees_count': profile.employees.count(),
        'proposals_count': proposals.count(),
        'proposals_approved': proposals.filter(status='APPROVED').count(),
        'proposals_rejected': proposals.filter(status='REJECTED').count(),
        'funding_count': funding_qs.count(),
        'funding_approved': funding_qs.filter(status='APPROVED').count(),
        'funding_rejected': funding_qs.filter(status='REJECTED').count(),
        'mentorship_count': mentorship_qs.filter(status='SCHEDULED').count(),
        'mentorship_completed': mentorship_qs.filter(status='COMPLETED').count(),
        'notifications_count': request.user.notifications.filter(read=False).count(),
        'notifications': request.user.notifications.all().order_by('-created_at')[:5],
    }
    return render(request, 'dashboard.html', context)



@login_required
def dashboard_data(request):
    profile = request.user.startup_profile
    projects = Project.objects.filter(startup=profile)
    proposals = ProjectProposal.objects.filter(project__startup=profile)
    funding_qs = FundingRound.objects.filter(startup=profile)
    mentorship_qs = MentorshipSession.objects.filter(startup=profile)

    data = {
        'projects': {
            'planned': projects.filter(status='PLANNED').count(),
            'ongoing': projects.filter(status='ONGOING').count(),
            'completed': projects.filter(status='COMPLETED').count(),
        },
        'proposals': {
            'submitted': proposals.count(),
            'approved': proposals.filter(status='APPROVED').count(),
            'rejected': proposals.filter(status='REJECTED').count(),
        },
        'funding': {
            'requested': funding_qs.count(),
            'approved': funding_qs.filter(status='APPROVED').count(),
            'rejected': funding_qs.filter(status='REJECTED').count(),
        },
        'mentorship': {
            'scheduled': mentorship_qs.filter(status='SCHEDULED').count(),
            'completed': mentorship_qs.filter(status='COMPLETED').count(),
        }
    }

    return JsonResponse(data)

# -----------------------------
# 3️⃣ Project CRUD
# -----------------------------
@login_required
def startup_projects(request):
    profile = request.user.startup_profile
    projects = Project.objects.filter(startup=profile)
    context = {
        'profile': profile,
        'projects': projects,
        'projects_count': projects.count(),
        'projects_in_progress': projects.filter(status='IN_PROGRESS').count(),
        'projects_completed': projects.filter(status='COMPLETED').count(),
        'notifications_count': request.user.notifications.filter(read=False).count(),
        'notifications': request.user.notifications.all().order_by('-created_at')[:5],
    }
    return render(request, 'projects_list.html', context)

@login_required
def create_project(request):
    profile = request.user.startup_profile
    if request.method == 'POST':
        form = ProjectForm(request.POST, request.FILES, startup=profile)
        if form.is_valid():
            project = form.save(commit=False)
            project.startup = profile
            project.save()
            form.save_m2m()

            # Assign employees
            employee_ids = request.POST.getlist('employees_assigned')
            project.employees_assigned.set(employee_ids)
            # Assign primary employee if any
            if employee_ids:
                emp = Employee.objects.get(id=employee_ids[0])
                ProjectAssignment.objects.update_or_create(
                    project=project,
                    defaults={
                        'employee_name': emp.name,
                        'role': emp.role,
                        'freelancer': None
                    }
                )

            # Notify freelancers if project is open
            if project.assigned_to_freelancers:
                freelancers = FreelancerProfile.objects.filter(domain=project.domain)
                
                if project.required_experience and project.required_experience != 'ANY':
                    freelancers = freelancers.filter(experience_years=project.required_experience)

                for f in freelancers:
                    Notification.objects.create(
                        user=f.user,
                        title=f"New Project Opportunity: {project.name}",
                        message=f"A new project '{project.name}' is open for proposals in {project.domain}."
                    )

            messages.success(request, "✅ Project created successfully!")
            return redirect('startup:startup_projects')
        else:
            messages.error(request, "⚠️ Please correct the errors below.")
    else:
        form = ProjectForm(startup=profile)

    employees = profile.employees.all()
    return render(request, 'create_project.html', {'form': form, 'profile': profile, 'employees': employees})

@login_required
def update_project(request, project_id):
    project = get_object_or_404(Project, id=project_id, startup=request.user.startup_profile)
    if request.method == 'POST':
        form = ProjectForm(request.POST, request.FILES, instance=project, startup=request.user.startup_profile)
        if form.is_valid():
            project = form.save(commit=False)
            req_file = request.FILES.get('requirements_file_upload')
            if req_file:
                project.requirements_file = req_file
            project.save()
            form.save_m2m()
            messages.success(request, "✅ Project updated successfully.")
            return redirect('startup:project_detail', project_id=project.id)
    else:
        form = ProjectForm(instance=project, startup=request.user.startup_profile)
    return render(request, 'project_edit.html', {'form': form, 'project': project, 'update': True})

@login_required
def project_detail(request, project_id):
    project = get_object_or_404(Project, id=project_id, startup=request.user.startup_profile)
    proposals = project.proposals.all()
    assigned_employees = project.employees_assigned.all()
    return render(request, 'project_detail.html', {'project': project, 'proposals': proposals, 'assigned_employees': assigned_employees})

@login_required
def delete_project(request, project_id):
    project = get_object_or_404(Project, id=project_id, startup=request.user.startup_profile)
    if request.method == 'POST':
        project.delete()
        return redirect('startup:startup_projects')
    return render(request, 'delete_project_confirm.html', {'project': project})

# -----------------------------
# 4️⃣ Project Proposals Workflow
# -----------------------------
from django.db.models import Count, Q
@login_required
def project_proposals(request):
    startup = request.user.startup_profile

    # Filter only projects that have proposals
    projects_with_proposals = Project.objects.filter(
        startup=startup,
        proposals__isnull=False
    ).annotate(
        pending_count=Count('proposals', filter=Q(proposals__status='PENDING'))
    ).distinct()

    return render(request, 'project_proposals_list.html', {
        'profile': startup,
        'projects': projects_with_proposals
    })

@login_required
def project_proposals_detail(request, project_id):
    project = get_object_or_404(Project, id=project_id, startup=request.user.startup_profile)
    filter_key = request.GET.get('filter', 'best_match')

    proposals = list(
        project.proposals.select_related('freelancer', 'freelancer__user')
    )

    # Trigger AI ranking for proposals without a report or with prior missing-key errors
    for p in proposals:
        if (not p.ai_report and p.ai_score == 0 and p.rank_score == 0) or (
            p.ai_report and "GEMINI_API_KEY not configured" in p.ai_report
        ):
            trigger_proposal_rank_async(p.id)

    # Precompute rating and verification flags for sorting/filtering
    for p in proposals:
        rating_data = p.freelancer.get_average_ratings
        p._rating_overall = rating_data.get('overall', 0)
        p._verified = p.freelancer.verification_status == 'VERIFIED'

    # Apply filters
    exp_map = {
        'exp_0_1': '0-1',
        'exp_1_3': '1-3',
        'exp_3_5': '3-5',
        'exp_5_plus': '5+',
    }
    if filter_key in exp_map:
        desired = exp_map[filter_key]
        proposals = [p for p in proposals if p.freelancer.experience_years == desired]
    elif filter_key == 'verified':
        proposals = [p for p in proposals if p._verified]

    # Apply sorting
    if filter_key == 'rating':
        proposals.sort(key=lambda p: (p._rating_overall, p.rank_score, p.ai_score), reverse=True)
    else:
        proposals.sort(
            key=lambda p: (p._verified, p._rating_overall, p.rank_score, p.ai_score, p.submitted_at),
            reverse=True
        )

    # Determine best match
    best_match_id = None
    for p in proposals:
        if p._verified and p._rating_overall >= 4.0:
            best_match_id = p.id
            break
    if best_match_id is None and proposals:
        best_match_id = proposals[0].id

    return render(request, 'project_proposals_detail.html', {
        'project': project,
        'proposals': proposals,
        'filter_key': filter_key,
        'best_match_id': best_match_id
    })


@login_required
def startup_employees(request):
    profile = request.user.startup_profile
    employees = profile.employees.all()
    return render(request, 'employee_list.html', {'profile': profile, 'employees': employees})

from django.http import JsonResponse

@login_required
def approve_proposal(request, proposal_id):
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        if not hasattr(request.user, 'startup_profile'):
            return JsonResponse({'success': False, 'message': 'Access denied.'})

        proposal = get_object_or_404(ProjectProposal, id=proposal_id)
        project = proposal.project
        if project.startup_id != request.user.startup_profile.id:
            return JsonResponse({'success': False, 'message': 'Access denied.'})

        # Prevent multiple approvals
        if ProjectAssignment.objects.filter(project=project, freelancer__isnull=False).exists():
            return JsonResponse({
                'success': False,
                'message': 'A freelancer has already been assigned to this project.'
            })

        # Approve proposal
        proposal.status = 'APPROVED'
        proposal.save()

        # Reject other proposals automatically
        ProjectProposal.objects.filter(project=project).exclude(id=proposal.id).update(status='REJECTED')

        # Create or update assignment
        ProjectAssignment.objects.update_or_create(
            project=project,
            defaults={'freelancer': proposal.freelancer, 'employee_name': None, 'role': None}
        )

        # Update project status
        project.status = 'ONGOING'
        project.save()

        # Notify freelancer
        Notification.objects.create(
            user=proposal.freelancer.user,
            title="Project Proposal Approved",
            message=f"Your proposal for project '{project.name}' has been approved."
        )

        return JsonResponse({
            'success': True,
            'message': 'Proposal approved',
            'proposal_id': proposal.id,
            'redirect_url': reverse('startup:setup_milestones', args=[project.id])
        })

    return JsonResponse({'success': False, 'message': 'Invalid request'})



@login_required
def reject_proposal(request, proposal_id):
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        if not hasattr(request.user, 'startup_profile'):
            return JsonResponse({'success': False, 'message': 'Access denied.'})

        proposal = get_object_or_404(ProjectProposal, id=proposal_id)
        if proposal.project.startup_id != request.user.startup_profile.id:
            return JsonResponse({'success': False, 'message': 'Access denied.'})

        if proposal.status != 'APPROVED':
            rejection_note = request.POST.get('rejection_note', '').strip()
            proposal.status = 'REJECTED'
            proposal.rejection_note = rejection_note
            proposal.save()

            Notification.objects.create(
                user=proposal.freelancer.user,
                title="Project Proposal Rejected",
                message=f"Your proposal for project '{proposal.project.name}' was rejected. Reason: {rejection_note}"
            )

            return JsonResponse({'success': True, 'message': 'Proposal rejected', 'proposal_id': proposal.id})

        return JsonResponse({'success': False, 'message': 'Cannot reject an approved proposal.'})

    return JsonResponse({'success': False, 'message': 'Invalid request'})


@login_required
def report_freelancer(request, proposal_id):
    if not hasattr(request.user, 'startup_profile'):
        messages.error(request, "Access denied.")
        return redirect('login')

    proposal = get_object_or_404(ProjectProposal, id=proposal_id)
    project = proposal.project
    if project.startup_id != request.user.startup_profile.id:
        messages.error(request, "Access denied.")
        return redirect('startup:project_proposals_detail', project_id=project.id)

    if request.method == 'POST':
        reason = request.POST.get('reason', '').strip()
        if not reason:
            messages.error(request, "Please provide a reason for the report.")
            return redirect('startup:project_proposals_detail', project_id=project.id)

        freelancer = proposal.freelancer
        FreelancerReport.objects.create(
            startup=request.user.startup_profile,
            freelancer=freelancer,
            project=project,
            proposal=proposal,
            reason=reason
        )

        freelancer.is_blocked = True
        freelancer.blocked_reason = reason
        freelancer.blocked_at = timezone.now()
        freelancer.block_count = (freelancer.block_count or 0) + 1
        # Permanent removal after 3 blocks
        if freelancer.block_count >= 3:
            freelancer.permanently_removed = True
            freelancer.user.is_active = False
            freelancer.user.save(update_fields=['is_active'])
        freelancer.save(update_fields=[
            'is_blocked',
            'blocked_reason',
            'blocked_at',
            'block_count',
            'permanently_removed',
        ])

        Notification.objects.create(
            user=freelancer.user,
            title="Account blocked",
            message=(
                "Your account has been blocked due to a report from a startup. "
                "Please contact support."
                if not freelancer.permanently_removed else
                "Your account has been permanently removed due to repeated reports."
            )
        )

        if freelancer.permanently_removed:
            messages.success(request, "Freelancer reported and permanently removed.")
        else:
            messages.success(request, "Freelancer reported and blocked from submitting new proposals.")
    return redirect('startup:project_proposals_detail', project_id=project.id)


# -----------------------------
# Milestone Setup (Startup)
# -----------------------------
@login_required
def setup_milestones(request, project_id):
    if not hasattr(request.user, 'startup_profile'):
        messages.error(request, "Access denied.")
        return redirect('login')

    project = get_object_or_404(Project, id=project_id, startup=request.user.startup_profile)
    assignment = getattr(project, 'assignment', None)
    if not assignment or not assignment.freelancer:
        messages.error(request, "No freelancer assigned to this project yet.")
        return redirect('startup:project_detail', project_id=project.id)

    existing = Milestone.objects.filter(project=project, freelancer=assignment.freelancer).order_by('id')

    if request.method == 'POST':
        form = MilestoneSetupForm(request.POST)
        if form.is_valid():
            raw = form.cleaned_data['milestones']
            lines = [line.strip() for line in raw.splitlines() if line.strip()]
            if not lines:
                messages.error(request, "Please add at least one milestone.")
            else:
                new_items = [
                    Milestone(
                        project=project,
                        freelancer=assignment.freelancer,
                        title=line,
                        status='PENDING',
                        progress=0
                    )
                    for line in lines
                ]
                Milestone.objects.bulk_create(new_items)
                Notification.objects.create(
                    user=assignment.freelancer.user,
                    title=f"Milestones added for {project.name}",
                    message="Your startup has added a milestone checklist. You can now mark them as you complete each item."
                )
                messages.success(request, "Milestones created successfully.")
                return redirect('startup:project_detail', project_id=project.id)
    else:
        form = MilestoneSetupForm()

    return render(request, 'setup_milestones.html', {
        'form': form,
        'project': project,
        'existing_milestones': existing,
        'profile': request.user.startup_profile
    })




# -----------------------------
# 5️⃣ Employee Management
# -----------------------------
@login_required
def startup_employees(request):
    profile = request.user.startup_profile
    employees = profile.employees.all()
    return render(request, 'employee_list.html', {'profile': profile, 'employees': employees})

@login_required
def add_employee(request):
    if request.method == 'POST':
        form = EmployeeForm(request.POST, request.FILES)
        if form.is_valid():
            employee = form.save(commit=False)
            employee.startup = request.user.startup_profile
            employee.save()
            return redirect('startup:startup_employees')
    else:
        form = EmployeeForm()
    return render(request, 'add_employee.html', {'form': form, 'profile': request.user.startup_profile})

@login_required
def update_employee(request, employee_id):
    employee = get_object_or_404(Employee, id=employee_id, startup=request.user.startup_profile)
    if request.method == 'POST':
        form = EmployeeForm(request.POST, request.FILES, instance=employee)
        if form.is_valid():
            form.save()
            messages.success(request, "Employee updated successfully!")
            return redirect('employee_detail', employee_id=employee.id)
        else:
            messages.error(request, "Please fix the errors below.")
    else:
        form = EmployeeForm(instance=employee)
    return render(request, 'employee_edit.html', {'form': form, 'employee': employee , 'profile': request.user.startup_profile})

@login_required
def employee_detail(request, employee_id):
    employee = get_object_or_404(Employee, id=employee_id, startup=request.user.startup_profile)
    completed_projects = Project.objects.filter(
        employees_assigned=employee,
        status='COMPLETED'
    )
    ratings = EmployeeRating.objects.filter(employee=employee)
    avg_rating = 0
    if ratings.exists():
        avg_rating = round(sum(r.average_rating for r in ratings) / ratings.count(), 1)

    return render(request, 'employee_detail.html', {
        'employee': employee,
        'profile': request.user.startup_profile,
        'completed_projects': completed_projects,
        'ratings': ratings,
        'avg_rating': avg_rating,
    })

@login_required
def delete_employee(request, employee_id):
    employee = get_object_or_404(Employee, id=employee_id, startup=request.user.startup_profile)
    if request.method == 'POST':
        employee.delete()
        return redirect('startup:startup_employees')
    return render(request, 'delete_employee_confirm.html', {'employee': employee , 'profile': request.user.startup_profile})

# -----------------------------
# 6️⃣ Notifications
# -----------------------------
@login_required
def notifications_list(request):
    notifications = request.user.notifications.all().order_by('-created_at')
    return render(request, 'notifications.html', {'notifications': notifications})

@login_required
def mark_notification_read(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.read = True
    notification.save()
    return redirect('startup:notifications_list')

@login_required
def notification_detail(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    if not notification.read:
        notification.read = True
        notification.save()
    return render(request, 'startup/notification_detail.html', {'notification': notification})

# # -----------------------------
# # 7️⃣ Funding
# # -----------------------------
# @login_required
# def funding_list(request):
#     rounds = FundingRound.objects.filter(startup=request.user.startup_profile)
#     return render(request, 'funding_list.html', {'funding_rounds': rounds , 'profile': request.user.startup_profile})

# from django.core.exceptions import ValidationError
# @login_required
# def create_funding(request):
#     if request.method == 'POST':
#         form = FundingForm(request.POST)
#         if form.is_valid():
#             funding = form.save(commit=False)
#             funding.startup = request.user.startup_profile
#             funding.status="REQUESTED"

#             try:
#                 # Model-level validation
#                 funding.full_clean()
#                 funding.save()
#                 print(f"Funding round saved: ID={funding.id}, Round={funding.round_name}")

#                 # ----- SEND NOTIFICATIONS -----
#                 if funding.all_investors:
#                     investors = InvestorProfile.objects.all()
#                     print(f"Sending notifications to all investors ({investors.count()})")
#                     for investor in investors:
#                         try:
#                             Notification.objects.create(
#                                 user=investor.user,
#                                 title="New Funding Round Available",
#                                 message=f"{funding.startup.startup_name} created a funding round: "
#                                         f"{funding.round_name} for ${funding.amount}"
#                             )
#                             print(f"Notification sent to {investor.user.username}")
#                         except Exception as e:
#                             print(f"Failed to send notification to {investor.user.username}: {e}")

#                 elif funding.investor:
#                     try:
#                         Notification.objects.create(
#                             user=funding.investor.user,
#                             title="Funding Round Created",
#                             message=f"{funding.startup.startup_name} created a funding round: "
#                                     f"{funding.round_name} for ${funding.amount}"
#                         )
#                         print(f"Notification sent to {funding.investor.user.username}")
#                     except Exception as e:
#                         print(f"Failed to send notification to {funding.investor.user.username}: {e}")
#                 else:
#                     print("No investor selected and all_investors=False — no notifications sent")
#                     messages.warning(request, 
#                         "Funding saved, but no notifications were sent because no investor was selected."
#                     )

#                 messages.success(request, "Funding round created successfully!")
#                 return redirect('startup:funding_list')

#             except ValidationError as e:
#                 form.add_error(None, e.message)
#                 messages.error(request, "Validation error — please check your inputs.")
#                 print("Validation error:", e)

#             except Exception as e:
#                 messages.error(request, "An unexpected error occurred.")
#                 print("Unexpected error:", e)

#         else:
#             messages.error(request, "Please correct the errors below.")
#             print("Form errors:", form.errors)

#     else:
#         form = FundingForm()

#     return render(request, 'create_funding.html', {'form': form , 'profile': request.user.startup_profile})
# @login_required
# def update_funding(request, funding_id):
#     funding = get_object_or_404(FundingRound, id=funding_id, startup=request.user.startup_profile)

#     # Restrict updates if already approved
#     if funding.status == 'APPROVED':
#         messages.error(request, "You cannot update an approved funding request.")
#         return redirect('startup:funding_list')

#     old_status = funding.status

#     if request.method == 'POST':
#         form = FundingForm(request.POST, instance=funding)
#         if form.is_valid():
#             updated_funding = form.save(commit=False)
#             updated_funding.startup = request.user.startup_profile

#             if old_status == 'REJECTED':
#                 updated_funding.status = 'PENDING'
#                 updated_funding.save()

#                 # ✅ Log status change
#                 funding.log_status_change(old_status, 'PENDING')

#                 # Notify investor
#                 Notification.objects.create(
#                     user=updated_funding.investor.user,
#                     title="Funding Request Resubmitted",
#                     message=f"{updated_funding.startup.startup_name} has updated and resubmitted the funding request '{updated_funding.round_name}' for your review."
#                 )

#                 # Notify startup
#                 Notification.objects.create(
#                     user=request.user,
#                     title="Funding Request Resent",
#                     message=f"Your funding request '{updated_funding.round_name}' has been resent to {updated_funding.investor.user.username}."
#                 )

#             else:
#                 updated_funding.save()
#                 funding.log_status_change(old_status, updated_funding.status)

#             messages.success(request, "Funding request updated successfully.")
#             return redirect('startup:funding_list')
#     else:
#         form = FundingForm(instance=funding)

#     return render(request, 'update_funding.html', {
#         'form': form,
#         'update': True,
#         'funding': funding,
#         'profile': request.user.startup_profile
#     })


# @login_required
# def funding_detail(request, funding_id):
#     funding = get_object_or_404(FundingRound, id=funding_id, startup=request.user.startup_profile)
#     return render(request, 'funding_detail.html', {'funding': funding , 'profile': request.user.startup_profile})

# @login_required
# def delete_funding(request, funding_id):
#     funding = get_object_or_404(FundingRound, id=funding_id, startup=request.user.startup_profile)
#     if request.method == 'POST':
#         funding.delete()
#         return redirect('startup:funding_list')
#     return render(request, 'delete_funding_confirm.html', {'funding': funding , 'profile': request.user.startup_profile})

# -----------------------------
# 8️⃣ Mentorship
# -----------------------------
# -----------------------------
# List all sessions for startup
# -----------------------------
@login_required
def startup_sessions(request):
    startup = request.user.startup_profile
    sessions = MentorshipSession.objects.filter(startup=startup).order_by('-session_date')
    
    return render(request, 'startup_sessions_list.html', {
        'sessions': sessions,
        'profile': request.user.startup_profile
    })



# -----------------------------
# Create a new session request
# -----------------------------
@login_required
def create_session(request):
    if request.method == 'POST':
        form = MentorshipSessionForm(request.POST)
        if form.is_valid():
            session = form.save(commit=False)
            session.startup = request.user.startup_profile
            session.approval_status = 'PENDING'  # awaiting mentor approval
            session.status = 'REQUESTED'
            session.save()

            # Notify mentor
            Notification.objects.create(
                user=session.mentor.user,
                title="New Mentorship Session Request",
                message=f"{session.startup.startup_name} requested a session on '{session.topic}' for {session.session_date.strftime('%d %b %Y, %I:%M %p')}."
            )

            Notification.objects.create(
                user=request.user,
                title="Session Request Sent",
                message=f"Your request to {session.mentor.user.username} is awaiting approval."
            )

            messages.success(request, "Session request sent and pending mentor approval.")
            return redirect('startup:startup_sessions')
    else:
        form = MentorshipSessionForm()
    return render(request, 'create_session.html', {'form': form , 'profile': request.user.startup_profile })


# -----------------------------
# View session details
# -----------------------------
@login_required
def session_detail(request, session_id):
    session = get_object_or_404(MentorshipSession, id=session_id, startup=request.user.startup_profile)
    return render(request, 'session_detail.html', {'session': session , 'profile': request.user.startup_profile})


# -----------------------------
# Update session (notes or status)
# -----------------------------
@login_required
def update_session(request, session_id):
    session = get_object_or_404(MentorshipSession, id=session_id, startup=request.user.startup_profile)

    # Determine if the form should be disabled (session is cancelled)
    disable_form = session.status == 'CANCELLED'

    if request.method == 'POST' and not disable_form:
        form = MentorshipSessionForm(request.POST, instance=session)
        if form.is_valid():
            original_status = session.approval_status
            updated_session = form.save(commit=False)

            # If session was approved, mark as pending for re-approval
            if original_status == 'APPROVED':
                updated_session.approval_status = 'PENDING'

                # Notify mentor for re-approval
                Notification.objects.create(
                    user=updated_session.mentor.user,
                    title="Session Updated – Approval Required",
                    message=f"{updated_session.startup.startup_name} updated session '{updated_session.topic}'. Please review and approve again."
                )

                Notification.objects.create(
                    user=request.user,
                    title="Session Update Sent",
                    message=f"Your updated session request for '{updated_session.topic}' is awaiting mentor approval again."
                )
            else:
                # Normal update for pending/rejected
                Notification.objects.create(
                    user=updated_session.mentor.user,
                    title="Session Request Updated",
                    message=f"{updated_session.startup.startup_name} modified the mentorship session request for '{updated_session.topic}'."
                )

            updated_session.save()
            messages.success(request, "Session updated successfully.")
            return redirect('startup:startup_sessions')
        else:
            messages.error(request, "Please correct the errors below.")

    else:
        # Initialize form, disabling fields if the session is cancelled
        form = MentorshipSessionForm(instance=session, disable_all=disable_form)

        if disable_form:
            messages.warning(request, "This session is cancelled and cannot be updated.")

    return render(request, 'update_session.html', {
        'form': form,
        'session': session,
        'profile': request.user.startup_profile
    })


# -----------------------------
# Cancel a session
# -----------------------------
@login_required
def cancel_session(request, session_id):
    session = get_object_or_404(MentorshipSession, id=session_id, startup=request.user.startup_profile)

    if request.method == 'POST':
        session.status = 'CANCELLED'
        session.save()

        Notification.objects.create(
            user=session.mentor.user,
            title="Session Cancelled",
            message=f"{session.startup.startup_name} cancelled the mentorship session '{session.topic}'."
        )

        messages.success(request, "Session cancelled successfully.")
        return redirect('startup:startup_sessions')

    return render(request, 'cancel_session_confirm.html', {'session': session , 'profile': request.user.startup_profile})



# 7️⃣ Notifications for startup
@login_required
def startup_notifications(request):
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'notifications.html', {'notifications': notifications})
# -----------------------------
# 9️⃣ Assign Employees to Projects
# -----------------------------
@login_required
def assign_employee_to_project(request, project_id):
    project = get_object_or_404(Project, id=project_id, startup=request.user.startup_profile)
    if request.method == 'POST':
        employee_ids = request.POST.getlist('employees')
        project.employees_assigned.set(employee_ids)
        project.save()
        # Notify freelancers
        freelancers = project.employees_assigned.filter(role='FREELANCER')
        for freelancer in freelancers:
            Notification.objects.create(
                user=freelancer.user,
                title="Project Assigned",
                message=f"You have been assigned to project: {project.name}"
            )
        return redirect('startup:startup_projects')
    employees = request.user.startup_profile.employees.all()
    return render(request, 'assign_employee.html', {'project': project, 'employees': employees})

@login_required
def project_to_frelancer_list(request):
    projects = ProjectAssignment.objects.filter(startup=request.user.startup_profile)
    return render(request, 'freelancerpro_list.html', {'project': projects , 'profile': request.user.startup_profile})



@login_required
def rate_freelancer(request, project_id):
    project = get_object_or_404(Project, id=project_id, startup=request.user.startup_profile)
    
    if project.status != 'COMPLETED':
        messages.error(request, "You can only rate freelancers for completed projects.")
        return redirect('startup:project_detail', project_id=project.id)
    
    if hasattr(project, 'rating'):
        messages.warning(request, "You have already rated the freelancer for this project.")
        return redirect('startup:project_detail', project_id=project.id)
    
    assignment = getattr(project, 'assignment', None)
    if not assignment or not assignment.freelancer:
        messages.error(request, "No freelancer was assigned to this project.")
        return redirect('startup:project_detail', project_id=project.id)
    
    freelancer = assignment.freelancer
    
    if request.method == 'POST':
        form = FreelancerRatingForm(request.POST)
        if form.is_valid():
            rating = form.save(commit=False)
            rating.freelancer = freelancer
            rating.startup = request.user.startup_profile
            rating.project = project
            rating.save()
            messages.success(request, f"Successfully rated {freelancer.full_name}!")
            return redirect('startup:project_detail', project_id=project.id)
    else:
        form = FreelancerRatingForm()
    
    return render(request, 'rate_freelancer.html', {
        'form': form,
        'project': project,
        'freelancer': freelancer,
        'profile': request.user.startup_profile
    })


@login_required
def rate_employee(request, employee_id, project_id):
    employee = get_object_or_404(Employee, id=employee_id, startup=request.user.startup_profile)
    project = get_object_or_404(Project, id=project_id, startup=request.user.startup_profile)

    if project.status != 'COMPLETED':
        messages.error(request, "You can only rate an employee after project completion.")
        return redirect('startup:employee_detail', employee_id=employee.id)

    if not project.employees_assigned.filter(id=employee.id).exists():
        messages.error(request, "This employee is not assigned to the selected project.")
        return redirect('startup:employee_detail', employee_id=employee.id)

    existing = EmployeeRating.objects.filter(employee=employee, project=project).first()
    if request.method == 'POST':
        form = EmployeeRatingForm(request.POST, instance=existing)
        if form.is_valid():
            rating = form.save(commit=False)
            rating.startup = request.user.startup_profile
            rating.employee = employee
            rating.project = project
            rating.save()
            messages.success(request, "Employee rating saved.")
            return redirect('startup:employee_detail', employee_id=employee.id)
    else:
        form = EmployeeRatingForm(instance=existing)

    return render(request, 'rate_employee.html', {
        'form': form,
        'employee': employee,
        'project': project,
        'profile': request.user.startup_profile
    })


# -----------------------------
# Notification helpers (side panel)
# -----------------------------
from django.views.decorators.http import require_POST

@login_required
@require_POST
def mark_all_notifications_read(request):
    """Called via AJAX when the notification panel is opened. Marks all unread as read."""
    request.user.notifications.filter(read=False).update(read=True)
    from django.http import JsonResponse
    return JsonResponse({'status': 'ok'})


@login_required
def notifications_list(request):
    profile = request.user.startup_profile
    notifications = request.user.notifications.all().order_by('-created_at')
    request.user.notifications.filter(read=False).update(read=True)
    return render(request, 'notifications_list.html', {
        'profile': profile,
        'notifications': notifications,
        'notifications_count': 0,
        'notifications_all': notifications,
    })


@login_required
def notification_detail(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.read = True
    notification.save()
    return render(request, 'notification_detail.html', {
        'notification': notification,
        'profile': request.user.startup_profile,
        'notifications_count': request.user.notifications.filter(read=False).count(),
        'notifications': request.user.notifications.filter(read=False).order_by('-created_at')[:10],
    })


@login_required
def mark_notification_read(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.read = True
    notification.save()
    return redirect(request.META.get('HTTP_REFERER', 'startup:startup_dashboard'))
