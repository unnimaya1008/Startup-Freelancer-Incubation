from django.shortcuts import render ,redirect
from .forms import FreelancerProfileForm , FreelancerSignupForm
from django.contrib.auth import login
# Create your views here.

from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone

from .forms import (
    FreelancerProfileForm,
    ProposalForm,
    MilestoneForm
)
from accounts.models import Notification
from projects.models import Project, ProjectProposal
from .models import FreelancerProfile
from accounts.supabase_helper import upload_to_supabase


# ----------------------------------------
# Helper
# ----------------------------------------
def role_required(role):
    """Custom role check for freelancers."""
    def decorator(func):
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated or request.user.role != role:
                messages.error(request, "Access denied.")
                return redirect('login')
            return func(request, *args, **kwargs)
        return wrapper
    return decorator



def freelancer_signup(request):
    if request.method == 'POST':
        user_form = FreelancerSignupForm(request.POST)
        profile_form = FreelancerProfileForm(request.POST, request.FILES)

        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save(commit=False)
            user.role = 'FREELANCER'
            user.save()

            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()

            login(request, user)
            return redirect('freelancer:freelancer_dashboard')

        else:
            print("❌ USER ERRORS:", user_form.errors)
            print("❌ PROFILE ERRORS:", profile_form.errors)

    else:
        user_form = FreelancerSignupForm()
        profile_form = FreelancerProfileForm()

    return render(request, 'freelancersignup.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })




# ----------------------------------------
# 1️⃣ Dashboard
# ----------------------------------------
@login_required
@role_required('FREELANCER')
def freelancer_dashboard(request):
    profile = request.user.freelancer_profile
    user = request.user
    proposals = ProjectProposal.objects.filter(freelancer=profile)
    
    # Get assigned projects through ProjectAssignment
    assigned_projects = Project.objects.filter(assignment__freelancer=profile)
    completed_projects = assigned_projects.filter(status='COMPLETED')

    # Remove earnings calculation (feature temporarily removed)
    # earnings = sum(profile.earnings.values_list('amount', flat=True))

    # Prepare stats as a list of dictionaries (without earnings)
    stats = [
        {'title': 'Total Proposals', 'value': proposals.count()},
        {'title': 'Pending Proposals', 'value': proposals.filter(status='PENDING').count()},
        {'title': 'Assigned Projects', 'value': assigned_projects.count()},
        {'title': 'Completed Projects', 'value': completed_projects.count()},
        {'title': 'New Notifications', 'value': request.user.notifications.filter(read=False).count()},
    ]

    context = {
        'user': user,
        'profile': profile,
        'stats': stats,
        'notifications': request.user.notifications.filter(read=False).order_by('-created_at')[:5],
    }
    return render(request, 'Fdashboard.html', context)


from django.http import JsonResponse
@login_required
def mark_notification_read(request, pk):
    if request.method != "POST":
        return HttpResponseForbidden("Invalid request method")

    note = get_object_or_404(Notification, pk=pk, user=request.user)

    # mark read and set read_at if the field exists
    if not note.read:
        note.read = True
        # prepare fields list defensively
        update_fields = ['read']
        if hasattr(note, 'read_at'):
            try:
                note.read_at = timezone.now()
                update_fields.append('read_at')
            except Exception:
                # fallback: don't include read_at if any unexpected error
                pass
        note.save(update_fields=update_fields)
    else:
        # already read — nothing to change
        pass

    # respond
    is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'
    if is_ajax:
        return JsonResponse({'success': True, 'id': note.id})

    next_url = request.POST.get('next') or request.GET.get('next') or request.META.get('HTTP_REFERER')
    if next_url:
        return redirect(next_url)
    return redirect(reverse('freelancer:freelancer_notifications'))

# ----------------------------------------
# 2️⃣ Profile Management
# ----------------------------------------
@login_required
@role_required('FREELANCER')
def freelancer_profile_detail(request):
    """Display freelancer profile in read-only form style."""
    profile = request.user.freelancer_profile
    return render(request, 'profile_detail.html', {'profile': profile})


@login_required
@role_required('FREELANCER')
def freelancer_profile_edit(request):
    user = request.user
    profile = user.freelancer_profile

    if request.method == 'POST':
        form = FreelancerProfileForm(
            request.POST,
            request.FILES,
            instance=profile
        )

        # User fields (handled separately)
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()

        if form.is_valid():
            # Save profile
            profile = form.save(commit=False)

            # Sync full_name safely
            full_name = f"{first_name} {last_name}".strip()
            if full_name:
                profile.full_name = full_name

            profile.save()

            # Save user fields
            user.first_name = first_name
            user.last_name = last_name
            user.save(update_fields=['first_name', 'last_name'])

            messages.success(request, "Profile updated successfully.")
            return redirect('freelancer:freelancer_profile_detail')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = FreelancerProfileForm(instance=profile)

    return render(
        request,
        'profile_edit.html',
        {
            'form': form,
            'profile': profile
        }
    )


# ----------------------------------------
# 3️⃣ Browse Projects & Proposals
# ----------------------------------------
@login_required
@role_required('FREELANCER')
def available_projects(request):
    profile = request.user.freelancer_profile

    # ✅ Projects that are not assigned and still in PLANNED status
    projects = Project.objects.filter(
    assigned_to_freelancers=True,
    status='PLANNED').exclude(proposals__freelancer=profile)


    return render(request, 'available_projects.html', {
        'projects': projects,
        'profile': profile
    })



# ----------------------------------------
# 2️⃣ Project Detail + Existing Proposal
# ----------------------------------------
@login_required
@role_required('FREELANCER')
def project_detail(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    freelancer = request.user.freelancer_profile

    # Check if the freelancer already applied
    existing_proposal = ProjectProposal.objects.filter(
        project=project,
        freelancer=freelancer
    ).first()

    return render(request, 'freelancerproject_detail.html', {
        'project': project,
        'proposal': existing_proposal
    })



# ----------------------------------------
# 3️⃣ Submit a Proposal
# ----------------------------------------
@login_required
@role_required('FREELANCER')
def submit_proposal(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    freelancer = request.user.freelancer_profile

    previous_proposal = ProjectProposal.objects.filter(project=project, freelancer=freelancer).first()

    # Allow resubmission only if project not assigned
    if previous_proposal and previous_proposal.status == 'APPROVED':
        messages.info(request, "Your proposal was already approved. Cannot resubmit.")
        return redirect('freelancer:freelancer_proposals')

    if request.method == 'POST':
        form = ProposalForm(request.POST, request.FILES, instance=previous_proposal if previous_proposal else None)
        if form.is_valid():
            proposal = form.save(commit=False)
            proposal.project = project
            proposal.freelancer = freelancer
            proposal.status = 'PENDING'
            proposal.rejection_note = None  # Clear old rejection note
            proposal.save()

            messages.success(request, "Proposal submitted successfully.")
            return redirect('freelancer:freelancer_proposals')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = ProposalForm(instance=previous_proposal)

    return render(request, 'submit_proposal.html', {
        'form': form,
        'project': project,
        'previous_proposal': previous_proposal
    })




# ----------------------------------------
# 4️⃣ View All My Proposals
# ----------------------------------------
@login_required
@role_required('FREELANCER')
def freelancer_proposals(request):
    proposals = ProjectProposal.objects.filter(
        freelancer=request.user.freelancer_profile
    ).select_related('project')
    
    return render(request, 'proposals_list.html', {
        'proposals': proposals
    })



# ----------------------------------------
# 5️⃣ Assigned Projects
# ----------------------------------------
@login_required
@role_required('FREELANCER')
def assigned_projects(request):
    freelancer = request.user.freelancer_profile

    projects = Project.objects.filter(
    assignment__freelancer=freelancer,
    assignment__is_active=True
)


    return render(request, 'assigned_projects.html', {
        'projects': projects
    })

@login_required
@role_required('FREELANCER')
def project_milestones(request, project_id):
    project = get_object_or_404(Project, id=project_id, assigned_freelancer=request.user.freelancer_profile)
    milestones = ProjectMilestone.objects.filter(project=project)
    return render(request, 'freelancer/project_milestones.html', {'project': project, 'milestones': milestones})


@login_required
@role_required('FREELANCER')
def update_milestone(request, milestone_id):
    milestone = get_object_or_404(ProjectMilestone, id=milestone_id, project__assigned_freelancer=request.user.freelancer_profile)
    if request.method == 'POST':
        form = MilestoneUpdateForm(request.POST, request.FILES, instance=milestone)
        if form.is_valid():
            form.save()
            messages.success(request, "Milestone updated successfully.")
            return redirect('project_milestones', project_id=milestone.project.id)
    else:
        form = MilestoneUpdateForm(instance=milestone)
    return render(request, 'freelancer/update_milestone.html', {'form': form, 'milestone': milestone})


# ----------------------------------------
# 5️⃣ Skills & Certifications
# ----------------------------------------
# @login_required
# @role_required('FREELANCER')
# def manage_skills(request):
#     profile = request.user.freelancer_profile
#     skills = Skill.objects.filter(freelancer=profile)

#     if request.method == 'POST':
#         form = SkillForm(request.POST, request.FILES)  # ✅ add request.FILES
#         if form.is_valid():
#             skill = form.save(commit=False)
#             skill.freelancer = profile
#             skill.save()
#             messages.success(request, "Skill added successfully.")
#             return redirect('freelancer:manage_skills')
#     else:
#         form = SkillForm()

#     return render(request, 'manage_skills.html', {'skills': skills, 'form': form})


# @login_required
# @role_required('FREELANCER')
# def edit_skill(request, skill_id):
#     profile = request.user.freelancer_profile
#     skill = get_object_or_404(Skill, id=skill_id, freelancer=profile)

#     if request.method == 'POST':
#         form = SkillForm(request.POST, request.FILES, instance=skill)  # handle uploaded file
#         if form.is_valid():
#             form.save()
#             messages.success(request, "Skill updated successfully.")
#             return redirect('freelancer:manage_skills')
#     else:
#         form = SkillForm(instance=skill)

#     return render(request, 'edit_skill.html', {'form': form, 'skill': skill})



# @login_required
# @role_required('FREELANCER')
# def delete_skill(request, skill_id):
#     profile = request.user.freelancer_profile
#     skill = get_object_or_404(Skill, id=skill_id, freelancer=profile)

#     if request.method == 'POST':
#         skill.delete()
#         messages.success(request, "Skill deleted successfully.")
#         return redirect('freelancer:manage_skills')



# @login_required
# @role_required('FREELANCER')
# def manage_certifications(request):
#     profile = request.user.freelancer_profile
#     certifications = Certification.objects.filter(freelancer=profile)
#     edit_id = request.GET.get('edit')
#     edit_cert = None

#     if edit_id:
#         edit_cert = get_object_or_404(Certification, id=edit_id, freelancer=profile)

#     if request.method == 'POST':
#         if edit_cert:
#             form = CertificationForm(request.POST, request.FILES, instance=edit_cert)
#             msg = "Certification updated successfully."
#         else:
#             form = CertificationForm(request.POST, request.FILES)
#             msg = "Certification added successfully."

#         if form.is_valid():
#             cert = form.save(commit=False)
#             cert.freelancer = profile
#             cert.save()
#             messages.success(request, msg)
#             return redirect('freelancer:manage_certifications')
#     else:
#         form = CertificationForm(instance=edit_cert)

#     return render(request, 'manage_certifications.html', {
#         'form': form,
#         'certifications': certifications,
#         'edit_cert': edit_cert,
#     })


# @login_required
# @role_required('FREELANCER')
# def delete_certification(request, cert_id):
#     profile = request.user.freelancer_profile
#     cert = get_object_or_404(Certification, id=cert_id, freelancer=profile)
#     cert.delete()
#     messages.success(request, "Certification deleted successfully.")
#     return redirect('freelancer:manage_certifications')




# # ----------------------------------------
# # 6️⃣ Portfolio Management
# # ----------------------------------------
# @login_required
# @role_required('FREELANCER')
# def portfolio_list(request):
#     profile = request.user.freelancer_profile
#     portfolio_items = PortfolioItem.objects.filter(freelancer=profile)
#     return render(request, 'portfolio_list.html', {'portfolio_items': portfolio_items})

# # Add a new portfolio item
# @login_required
# @role_required('FREELANCER')
# def add_portfolio_item(request):
#     profile = request.user.freelancer_profile
#     if request.method == 'POST':
#         form = PortfolioForm(request.POST, request.FILES)
#         if form.is_valid():
#             item = form.save(commit=False)
#             item.freelancer = profile
#             item.save()
#             messages.success(request, "Portfolio item added successfully.")
#             return redirect('freelancer:freelancer_portfolio')
#     else:
#         form = PortfolioForm()
#     return render(request, 'add_portfolio.html', {'form': form})

# # Edit an existing portfolio item
# @login_required
# @role_required('FREELANCER')
# def edit_portfolio_item(request, pk):
#     profile = request.user.freelancer_profile
#     item = get_object_or_404(PortfolioItem, pk=pk, freelancer=profile)
    
#     if request.method == 'POST':
#         form = PortfolioForm(request.POST, request.FILES, instance=item)
#         if form.is_valid():
#             form.save()
#             messages.success(request, "Portfolio item updated successfully.")
#             return redirect('freelancer:freelancer_portfolio')
#     else:
#         form = PortfolioForm(instance=item)
    
#     return render(request, 'edit_portfolio.html', {'form': form, 'item': item})


# # Delete a portfolio item
# @login_required
# @role_required('FREELANCER')
# def delete_portfolio_item(request, pk):
#     profile = request.user.freelancer_profile
#     item = get_object_or_404(PortfolioItem, pk=pk, freelancer=profile)
    
#     if request.method == 'POST':
#         item.delete()
#         messages.success(request, f'Portfolio item "{item.title}" deleted successfully.')
#         return redirect('freelancer:freelancer_portfolio')
    
#     # Optional: show confirmation page before deletion
#     return render(request, 'confirm_delete_portfolio.html', {'item': item})


# ----------------------------------------
# 7️⃣ Notifications & Feedback
# ----------------------------------------
@login_required
@role_required('FREELANCER')
def freelancer_notifications(request):
    notifications = Notification.objects.filter(
        user=request.user
    ).order_by('-created_at')

    return render(
        request,
        'notifications.html',
        {'notifications': notifications}
    )







# ----------------------------------------
# Milestone Views (Corrected)
# ----------------------------------------

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from .models import Milestone, FreelancerProfile
from .forms import MilestoneForm
from projects.models import Project
from accounts.models import Notification


# ----------------------------------------
# LIST MILESTONES FOR A PROJECT
# ----------------------------------------
@login_required
@role_required('FREELANCER')
def milestone_list(request, project_id):
    freelancer = request.user.freelancer_profile

    project = get_object_or_404(
        Project,
        id=project_id,
        assignment__freelancer=freelancer,
        assignment__is_active=True
    )

    milestones = Milestone.objects.filter(
        project=project,
        freelancer=freelancer
    )

    return render(
        request,
        'milestone_list.html',
        {
            'project': project,
            'milestones': milestones
        }
    )


# ----------------------------------------
# CREATE NEW MILESTONE
# ----------------------------------------
@login_required
@role_required('FREELANCER')
def create_milestone(request, project_id):
    freelancer = request.user.freelancer_profile

    project = get_object_or_404(
        Project,
        id=project_id,
        assignment__freelancer=freelancer,
        assignment__is_active=True
    )

    if project.status == 'COMPLETED':
        messages.error(request, "Cannot add milestones to a completed project.")
        return redirect('freelancer:freelancer_milestones', project_id=project.id)

    if request.method == 'POST':
        form = MilestoneForm(request.POST)
        if form.is_valid():
            milestone = form.save(commit=False)
            milestone.project = project
            milestone.freelancer = freelancer
            milestone.save()

            Notification.objects.create(
                user=project.startup.user,
                title="New Milestone Added",
                message=f"{freelancer.full_name} added milestone '{milestone.title}' for project '{project.name}'."
            )

            messages.success(request, "Milestone created successfully.")
            return redirect('freelancer:freelancer_milestones', project_id=project.id)
    else:
        form = MilestoneForm()

    return render(
        request,
        'milestone_form.html',
        {
            'form': form,
            'project': project,
            'create': True
        }
    )


# ----------------------------------------
# UPDATE MILESTONE
# ----------------------------------------
@login_required
@role_required('FREELANCER')
def update_milestone(request, milestone_id):
    freelancer = request.user.freelancer_profile

    milestone = get_object_or_404(
        Milestone,
        id=milestone_id,
        freelancer=freelancer,
        project__assignment__freelancer=freelancer
    )

    project = milestone.project

    if project.status == 'COMPLETED':
        messages.error(request, "Cannot update milestones of a completed project.")
        return redirect('freelancer:freelancer_milestones', project_id=project.id)

    if request.method == 'POST':
        form = MilestoneForm(request.POST, instance=milestone)
        if form.is_valid():
            updated = form.save(commit=False)

            # Auto status sync
            if updated.progress >= 100:
                updated.progress = 100
                updated.status = 'COMPLETED'

                Notification.objects.create(
                    user=project.startup.user,
                    title="Milestone Completed",
                    message=f"{freelancer.full_name} completed milestone '{updated.title}'."
                )
            elif updated.progress > 0:
                updated.status = 'IN_PROGRESS'
            else:
                updated.status = 'PENDING'

            updated.save()
            messages.success(request, "Milestone updated successfully.")
            return redirect('freelancer:freelancer_milestones', project_id=project.id)
    else:
        form = MilestoneForm(instance=milestone)

    return render(
        request,
        'milestone_form.html',
        {
            'form': form,
            'project': project,
            'milestone': milestone,
            'update': True
        }
    )


# ----------------------------------------
# DELETE MILESTONE
# ----------------------------------------
@login_required
@role_required('FREELANCER')
def delete_milestone(request, milestone_id):
    freelancer = request.user.freelancer_profile

    milestone = get_object_or_404(
        Milestone,
        id=milestone_id,
        freelancer=freelancer,
        project__assignment__freelancer=freelancer
    )

    project_id = milestone.project.id

    if milestone.project.status == 'COMPLETED':
        messages.error(request, "Cannot delete milestones from a completed project.")
        return redirect('freelancer:freelancer_milestones', project_id=project_id)

    milestone.delete()
    messages.success(request, "Milestone deleted successfully.")

    return redirect('freelancer:freelancer_milestones', project_id=project_id)



@login_required
@role_required('FREELANCER')
def complete_project(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    freelancer = request.user.freelancer_profile

    # Get the assignment
    assignment = getattr(project, 'assignment', None)
    if not assignment or assignment.freelancer != freelancer:
        messages.error(request, "You are not assigned to this project.")
        return redirect('freelancer:freelancer_assigned_projects')

    if project.status != 'COMPLETED':
        project.status = 'COMPLETED'
        project.save()
        messages.success(request, f"Project '{project.name}' marked as completed!")
    else:
        messages.info(request, f"Project '{project.name}' is already completed.")

    return redirect('freelancer:freelancer_assigned_projects')



