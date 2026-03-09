from django.urls import path
from . import views
app_name = 'mentors'

urlpatterns = [
    path('signup/', views.MentorSignupView.as_view(), name='mentor_signup'),
    path('dashboard/', views.MentorDashboardView.as_view(), name='dashboard'),
    path('mentorship-sessions/', views.MentorshipSessionListView.as_view(), name='mentorship_sessions'),
    path('mentorship-sessions/<int:session_id>/approve/', views.MentorshipSessionApproveView.as_view(), name='approve_session'),
    path('mentorship-sessions/<int:session_id>/reject/', views.MentorshipSessionRejectView.as_view(), name='reject_session'),
    path('mentorship-sessions/<int:session_id>/update-status/<str:new_status>/', views.MentorshipSessionStatusUpdateView.as_view(), name='update_session_status'),
    path('profile/', views.MentorProfileView.as_view(), name='mentor_profile'),
    path('profile/edit/', views.MentorProfileEditView.as_view(), name='mentor_profile_edit'),
    
]
