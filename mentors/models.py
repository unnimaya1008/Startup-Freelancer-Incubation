from django.db import models
from accounts.models import CustomUser
from startup.models import StartupProfile

class MentorProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name="mentor_profile")
    expertise_area = models.CharField(max_length=200)
    profile_image = models.ImageField(
        upload_to="mentors/profile_images/",
        blank=True,
        null=True
    )
    experience_years = models.PositiveIntegerField(default=0)
    linkedin_profile = models.URLField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} - Mentor"

class MentorshipSession(models.Model):
    mentor = models.ForeignKey(MentorProfile, on_delete=models.CASCADE, related_name="sessions")
    startup = models.ForeignKey(StartupProfile, on_delete=models.CASCADE, related_name="sessions")

    topic = models.CharField(max_length=100)
    session_date = models.DateTimeField()
    notes = models.TextField(blank=True, null=True)

    approval_status = models.CharField(
        max_length=20,
        choices=[
            ('PENDING', 'Pending Approval'),
            ('APPROVED', 'Approved'),
            ('REJECTED', 'Rejected'),
        ],
        default='PENDING'
    )

    status = models.CharField(
    max_length=20,
    choices=[
        ('REQUESTED', 'Requested'),   # <-- new option
        ('SCHEDULED', 'Scheduled'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ],
    default='REQUESTED'
)

    def __str__(self):
        return f"{self.startup.startup_name} → {self.mentor.user.username} ({self.topic})"

