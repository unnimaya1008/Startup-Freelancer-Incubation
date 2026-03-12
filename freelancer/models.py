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

    # ── AI Verification Fields ──
    github_url = models.URLField(blank=True, null=True, help_text="Link to your GitHub profile")
    certificate = models.FileField(upload_to="freelancer/certificates/", blank=True, null=True, help_text="Upload your certificate (image or PDF)")

    VERIFICATION_CHOICES = [
        ('PENDING', 'Pending'),
        ('VERIFIED', 'Verified'),
        ('SUSPICIOUS', 'Suspicious'),
        ('UNVERIFIED', 'Unverified'),
    ]
    verification_status = models.CharField(max_length=20, choices=VERIFICATION_CHOICES, default='PENDING')
    fraud_score = models.IntegerField(default=0, help_text="0 = trustworthy, 100 = likely fraudulent")
    ai_verification_report = models.TextField(blank=True, null=True, help_text="AI-generated verification reasoning")
    is_blocked = models.BooleanField(default=False)
    blocked_reason = models.TextField(blank=True, null=True)
    blocked_at = models.DateTimeField(blank=True, null=True)
    block_count = models.IntegerField(default=0)
    permanently_removed = models.BooleanField(default=False)

    @property
    def get_average_ratings(self):
        """Calculates and returns average ratings for the freelancer."""
        ratings = self.ratings.all()
        if not ratings.exists():
            return {
                'timeliness': 0,
                'quality': 0,
                'communication': 0,
                'overall': 0,
                'count': 0
            }
        
        avg_timeliness = sum(r.timeliness_rating for r in ratings) / ratings.count()
        avg_quality = sum(r.quality_rating for r in ratings) / ratings.count()
        avg_communication = sum(r.communication_rating for r in ratings) / ratings.count()
        overall = (avg_timeliness + avg_quality + avg_communication) / 3
        
        return {
            'timeliness': round(avg_timeliness, 1),
            'quality': round(avg_quality, 1),
            'communication': round(avg_communication, 1),
            'overall': round(overall, 1),
            'count': ratings.count()
        }

# # ------------------------------------------------
# # 2️⃣ SKILLS
# # ------------------------------------------------
# 5️⃣ FREELANCER RATINGS
# ------------------------------------------------
class FreelancerRating(models.Model):
    freelancer = models.ForeignKey(FreelancerProfile, on_delete=models.CASCADE, related_name='ratings')
    startup = models.ForeignKey('startup.StartupProfile', on_delete=models.CASCADE, related_name='freelancer_ratings')
    project = models.OneToOneField('projects.Project', on_delete=models.CASCADE, related_name='rating')
    
    timeliness_rating = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)], default=5)
    quality_rating = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)], default=5)
    communication_rating = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)], default=5)
    
    feedback = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def average_rating(self):
        return round((self.timeliness_rating + self.quality_rating + self.communication_rating) / 3, 1)

    def __str__(self):
        return f"{self.freelancer.full_name} - {self.project.name} Rating"

    class Meta:
        ordering = ['-created_at']


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
    completed_date = models.DateField(null=True, blank=True)
    
    # auto_now is enough
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} - {self.project.title}"

    class Meta:
        ordering = ['-due_date']
