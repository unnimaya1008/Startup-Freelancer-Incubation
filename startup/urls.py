from django.urls import path
from . import views
app_name = 'startup'

urlpatterns = [
    # -----------------------------
    # Auth / Signup / Dashboard / Profile
    # -----------------------------
    path('signup/', views.startup_signup, name='startup_signup'),
    path('dashboard/', views.startup_dashboard, name='startup_dashboard'),
    path('dashboard/data/', views.dashboard_data, name='dashboard_data'),
    path('profile/', views.profile_detail, name='stprofile_detail'),
    path('profile/edit/', views.profile_edit, name='sprofile_edit'),

    

    # -----------------------------
    # Projects CRUD
    # -----------------------------
    path('projects/', views.startup_projects, name='startup_projects'),
    path('projects/create/', views.create_project, name='create_project'),
    path('projects/<int:project_id>/', views.project_detail, name='project_detail'),
    path('projects/<int:project_id>/update/', views.update_project, name='update_project'),
    path('projects/<int:project_id>/delete/', views.delete_project, name='delete_project'),

    # -----------------------------
    # Project Proposals
    # -----------------------------
    path('proposals/', views.project_proposals, name='project_proposals'),
    path('proposals/<int:project_id>/', views.project_proposals_detail, name='project_proposals_detail'),
    path('proposals/<int:proposal_id>/approve/', views.approve_proposal, name='approve_proposal'),
    path('proposals/<int:proposal_id>/reject/', views.reject_proposal, name='reject_proposal'),

    # -----------------------------
    # Employee Assignment to Projects
    # -----------------------------
    path('projects/<int:project_id>/assign-employees/', views.assign_employee_to_project, name='assign_employee_to_project'),

    # -----------------------------
    # Employees Management
    # -----------------------------
    path('employees/', views.startup_employees, name='startup_employees'),
    path('employees/add/', views.add_employee, name='add_employee'),
    path('employees/<int:employee_id>/', views.employee_detail, name='employee_detail'),
    path('employees/<int:employee_id>/update/', views.update_employee, name='update_employee'),
    path('employees/<int:employee_id>/delete/', views.delete_employee, name='delete_employee'),

    # -----------------------------
    # Notifications
    # -----------------------------
    path('notifications/', views.notifications_list, name='notifications_list'),
    path('notifications/<int:notification_id>/', views.notification_detail, name='notification_detail'),
    path('notifications/<int:notification_id>/read/', views.mark_notification_read, name='mark_notification_read'),

    # -----------------------------
    # Funding Rounds
    # -----------------------------
    # path('funding/', views.funding_list, name='funding_list'),
    # path('funding/create/', views.create_funding, name='create_funding'),
    # path('funding/<int:funding_id>/', views.funding_detail, name='funding_detail'),
    # path('funding/<int:funding_id>/update/', views.update_funding, name='update_funding'),
    # path('funding/<int:funding_id>/delete/', views.delete_funding, name='delete_funding'),

    # -----------------------------
    # Mentorship Sessions
    # -----------------------------
    path('sessions/', views.startup_sessions, name='startup_sessions'),
    path('sessions/create/', views.create_session, name='create_session'),
    path('sessions/<int:session_id>/', views.session_detail, name='session_detail'),
    path('sessions/<int:session_id>/update/', views.update_session, name='update_session'),
    path('sessions/<int:session_id>/cancel/', views.cancel_session, name='cancel_session'),

    # -----------------------------
    # Freelancer Projects / Proposals (for future use)
    # -----------------------------
    path('freelancer/available-projects/', views.project_to_frelancer_list, name='available_projects_for_freelancer'),
]
