from django.db import models
from accounts.models import CustomUser
import datetime
from django.utils import timezone


# ------------------------------------------------
# 1️⃣ FREELANCER PROFILE
# ------------------------------------------------
class FreelancerProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='freelancer_profile')
    full_name = models.CharField(max_length=100)
    contact_number = models.CharField(max_length=20, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    hourly_rate = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)

    domain = models.CharField(max_length=50)   # ← ADD THIS LINE

    availability = models.CharField(
        max_length=50,
        choices=[('AVAILABLE', 'Available'), ('BUSY', 'Busy'), ('OFFLINE', 'Offline')],
        default='AVAILABLE'
    )

    experience_years = models.CharField(
        max_length=20,
        choices=[
            ('0-1', '0-1 Years'),
            ('1-3', '1-3 Years'),
            ('3-5', '3-5 Years'),
            ('5+', '5+ Years'),
        ],
        default='0-1'
    )

    profile_picture = models.ImageField(upload_to="freelancer/", blank=True, null=True)
    resume = models.FileField(blank=True, null=True)
    total_earnings = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

# # ------------------------------------------------
# # 2️⃣ SKILLS
# # ------------------------------------------------
# class Skill(models.Model):
#     freelancer = models.ForeignKey(FreelancerProfile, on_delete=models.CASCADE, related_name='skills')
#     name = models.CharField(max_length=100)
#     proficiency = models.CharField(
#         max_length=20,
#         choices=[('BEGINNER', 'Beginner'), ('INTERMEDIATE', 'Intermediate'), ('EXPERT', 'Expert')],
#         default='INTERMEDIATE'
#     )
#     image = models.ImageField(upload_to='skill_icons/', null=True, blank=True)  # ✅ New image field

#     def __str__(self):
#         return f"{self.name} ({self.proficiency})"

#     class Meta:
#         unique_together = ('freelancer', 'name')
#         ordering = ['name']


# # ------------------------------------------------
# # 3️⃣ CERTIFICATIONS
# # ------------------------------------------------
# class Certification(models.Model):
#     freelancer = models.ForeignKey(FreelancerProfile, on_delete=models.CASCADE, related_name='certifications')
#     title = models.CharField(max_length=150)
#     issuer = models.CharField(max_length=150, blank=True, null=True)
#     issue_date = models.DateField(blank=True, null=True)
#     certificate_url = models.URLField(blank=True, null=True)
#     certificate_file = models.FileField(upload_to='certificates/files/', blank=True, null=True)
#     certificate_image = models.ImageField(upload_to='certificates/images/', blank=True, null=True)  # 🖼️ Added field


#     def __str__(self):
#         return f"{self.title} - {self.issuer or 'N/A'}"

#     class Meta:
#         ordering = ['-issue_date']


# # ------------------------------------------------
# # 4️⃣ PORTFOLIO ITEMS
# # ------------------------------------------------
# class PortfolioItem(models.Model):
#     freelancer = models.ForeignKey(FreelancerProfile, on_delete=models.CASCADE, related_name='portfolio_items')
#     title = models.CharField(max_length=200)
#     description = models.TextField(blank=True, null=True)
#     file = models.FileField(upload_to='portfolio_files/', blank=True, null=True)
#     preview_image = models.ImageField(upload_to='portfolio_images/', blank=True, null=True)
#     date_uploaded = models.DateTimeField(auto_now_add=True , null=True)
#     live_link = models.URLField(blank=True, null=True)

#     def __str__(self):
#         return self.title

#     class Meta:
#         ordering = ['-date_uploaded']


# # ------------------------------------------------
# # 5️⃣ FREELANCER RATINGS (optional)
# # ------------------------------------------------
# class FreelancerRating(models.Model):
#     freelancer = models.ForeignKey(FreelancerProfile, on_delete=models.CASCADE, related_name='ratings')
#     startup = models.ForeignKey('startup.StartupProfile', on_delete=models.CASCADE, related_name='freelancer_ratings')
#     project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, related_name='freelancer_ratings')
#     rating = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)])
#     feedback = models.TextField(blank=True, null=True)
#     created_at = models.DateTimeField(auto_now_add=True , null=True)

#     def __str__(self):
#         return f"{self.freelancer.full_name} - {self.rating}/5"

#     class Meta:
#         unique_together = ('freelancer', 'project')
#         ordering = ['-created_at']


# # ------------------------------------------------
# # 6️⃣ EARNINGS & PAYMENTS (optional extension)
# # ------------------------------------------------
# class FreelancerEarning(models.Model):
#     freelancer = models.ForeignKey(FreelancerProfile, on_delete=models.CASCADE, related_name='earnings')
#     project = models.ForeignKey('projects.Project', on_delete=models.SET_NULL, null=True, blank=True)
#     amount = models.DecimalField(max_digits=10, decimal_places=2)
#     payment_status = models.CharField(
#         max_length=20,
#         choices=[('PENDING', 'Pending'), ('PAID', 'Paid')],
#         default='PENDING'
#     )
#     date = models.DateField(auto_now_add=True , null=True)

#     def __str__(self):
#         return f"{self.freelancer.full_name} - ₹{self.amount} ({self.payment_status})"

#     class Meta:
#         ordering = ['-date']



# ------------------------------------------------
# 7️⃣ MILESTONES
# ------------------------------------------------
class Milestone(models.Model):
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, related_name='milestones')
    freelancer = models.ForeignKey(FreelancerProfile, on_delete=models.CASCADE, related_name='milestones')
    title = models.CharField(max_length=150)
    description = models.TextField(blank=True, null=True)
    
    # Make nullable so migration works
    due_date = models.DateField(null=True, blank=True)
    
    progress = models.IntegerField(default=0)
    status = models.CharField(
        max_length=20,
        choices=[('PENDING', 'Pending'), ('IN_PROGRESS', 'In Progress'), ('COMPLETED', 'Completed')],
        default='PENDING'
    )
    remarks = models.TextField(blank=True, null=True)
    
    # auto_now is enough
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} - {self.project.title}"

    class Meta:
        ordering = ['-due_date']
