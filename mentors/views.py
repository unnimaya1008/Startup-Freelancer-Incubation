from django.shortcuts import render, redirect, get_object_or_404
from .models import MentorProfile, MentorshipSession
from .forms import MentorSignupForm, MentorProfileForm
from django.views import View
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseForbidden

class MentorSignupView(View):
    def get(self, request):
        form = MentorSignupForm()
        profile_form = MentorProfileForm()
        return render(request, 'mentorsignup.html', {'user_form': form, 'profile_form': profile_form})

    def post(self, request):
        user_form = MentorSignupForm(request.POST)
        profile_form = MentorProfileForm(request.POST, request.FILES)
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()
            login(request, user)
            return redirect("mentors:dashboard")
        return render(request, 'mentorsignup.html', {'user_form': user_form, 'profile_form': profile_form})

class MentorDashboardView(LoginRequiredMixin, View):
    def get(self, request):
        mentor_profile = get_object_or_404(
            MentorProfile,
            user=request.user
        )

        sessions = MentorshipSession.objects.filter(
            mentor=mentor_profile
        )

        # ✅ Active Requests = sessions not yet acted upon
        active_requests = sessions.filter(
            approval_status='PENDING'
        ).count()

        context = {
            'mentor_profile': mentor_profile,
            'sessions': sessions,
            'active_requests': active_requests,
        }

        return render(
            request,
            'mentor_dashboard.html',
            context
        )

class MentorshipSessionListView(LoginRequiredMixin, View):
    def get(self, request):
        mentor_profile = get_object_or_404(MentorProfile, user=request.user)
        sessions = MentorshipSession.objects.filter(mentor=mentor_profile)
        return render(request, 'mentorship_sessions.html', {'sessions': sessions , 'mentor_profile': mentor_profile,})

class MentorshipSessionApproveView(LoginRequiredMixin, View):
    def post(self, request, session_id):
        session = get_object_or_404(MentorshipSession, id=session_id)
        if session.mentor.user != request.user:
            return HttpResponseForbidden("Not allowed")
        session.approval_status = 'APPROVED'
        session.status = 'SCHEDULED'
        session.save()
        return redirect('mentors:mentorship_sessions')

class MentorshipSessionRejectView(LoginRequiredMixin, View):
    def post(self, request, session_id):
        session = get_object_or_404(MentorshipSession, id=session_id)
        if session.mentor.user != request.user:
            return HttpResponseForbidden("Not allowed")
        session.approval_status = 'REJECTED'
        session.status = 'CANCELLED'
        session.save()
        return redirect('mentors:mentorship_sessions')

class MentorshipSessionStatusUpdateView(LoginRequiredMixin, View):
    def post(self, request, session_id, new_status):
        session = get_object_or_404(MentorshipSession, id=session_id)
        if session.mentor.user != request.user:
            return HttpResponseForbidden("Not allowed")
        if new_status in dict(MentorshipSession._meta.get_field('status').choices).keys():
            session.status = new_status
            session.save()
        return redirect('mentors:mentorship_sessions')

class MentorProfileView(LoginRequiredMixin, View):
    def get(self, request):
        mentor_profile = get_object_or_404(MentorProfile, user=request.user)
        return render(request, 'mentor_profile.html', {'mentor_profile': mentor_profile})

class MentorProfileEditView(LoginRequiredMixin, View):
    def get(self, request):
        mentor_profile = get_object_or_404(MentorProfile, user=request.user)
        form = MentorProfileForm(instance=mentor_profile)
        return render(request, 'mentor_profile_edit.html', {
            'form': form,
            'mentor_profile': mentor_profile
        })

    def post(self, request):
        mentor_profile = get_object_or_404(MentorProfile, user=request.user)
        form = MentorProfileForm(request.POST, request.FILES, instance=mentor_profile)

        if form.is_valid():
            form.save()
            return redirect('mentors:mentor_profile')

        return render(request, 'mentor_profile_edit.html', {
            'form': form,
            'mentor_profile': mentor_profile
        })

