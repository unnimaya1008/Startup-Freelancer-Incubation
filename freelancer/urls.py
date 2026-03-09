from django.urls import path
from . import views
app_name = 'freelancer'
urlpatterns = [
    # -----------------------------
    # Auth / Dashboard
    # -----------------------------
    path("dashboard/", views.freelancer_dashboard, name="freelancer_dashboard"),
    path("signup/", views.freelancer_signup, name="freelancer_signup"),
    path("notification/read/<int:pk>/", views.mark_notification_read, name="mark_notification_read"),
    

    # -----------------------------
    # 1️⃣ Profile
    # -----------------------------
    path('profile/', views.freelancer_profile_detail, name='freelancer_profile_detail'),
    path('profile/edit/', views.freelancer_profile_edit, name='freelancer_profile_edit'),

    # -----------------------------
    # 2️⃣ Skills
    # -----------------------------
    # path('skills/', views.manage_skills, name='manage_skills'),
    # path('skills/edit/<int:skill_id>/', views.edit_skill, name='edit_skill'),
    # path('skills/delete/<int:skill_id>/', views.delete_skill, name='delete_skill'),

    # -----------------------------
    # 3️⃣ Certifications
    # -----------------------------
    # path('certifications/', views.manage_certifications, name='manage_certifications'),
    # path('certifications/delete/<int:cert_id>/', views.delete_certification, name='delete_certification'),

    # -----------------------------
    # 4️⃣ Portfolio
    # -----------------------------
    # path('portfolio/', views.portfolio_list, name='freelancer_portfolio'),
    # path('portfolio/add/', views.add_portfolio_item, name='freelancer_add_portfolio'),
    # path('portfolio/edit/<int:pk>/', views.edit_portfolio_item, name='freelancer_edit_portfolio'),
    # path('portfolio/delete/<int:pk>/', views.delete_portfolio_item, name='freelancer_delete_portfolio'),

    # -----------------------------
    # 5️⃣ Projects & Proposals
    # ----------------------------- 
    path("projects/available/", views.available_projects, name="available_projects"),
    path("projects/assigned/", views.assigned_projects, name="freelancer_assigned_projects"),
    path("projects/<int:project_id>/", views.project_detail, name="freelancer_project_detail"),

    # --- Proposals ---
    path("proposals/", views.freelancer_proposals, name="freelancer_proposals"),
    path("projects/<int:project_id>/submit-proposal/", views.submit_proposal, name="freelancer_submit_proposal"),

    # -----------------------------
    # 6️⃣ Milestones
    # -----------------------------
    path("projects/<int:project_id>/milestones/", views.milestone_list, name="freelancer_milestones"),
    path("milestones/<int:milestone_id>/update/", views.update_milestone, name="freelancer_update_milestone"),
    path("milestones/<int:milestone_id>/delete/", views.delete_milestone, name="freelancer_delete_milestone"),
    path("projects/<int:project_id>/milestones/create/", views.create_milestone, name="freelancer_create_milestone"),

    # -----------------------------
    # 7️⃣ Notifications
    # -----------------------------
    path("notifications/", views.freelancer_notifications, name="freelancer_notifications"),

    # -----------------------------
    # 8️⃣ Feedback / Earnings
    # -----------------------------
    # path("feedback/", views.feedback_list, name="freelancer_feedback"),
    # path("earnings/", views.freelancer_earnings, name="freelancer_earnings"),
    
    path('project/<int:project_id>/complete/', views.complete_project, name='complete_project'),

]
