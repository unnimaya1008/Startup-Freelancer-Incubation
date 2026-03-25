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
    github_url = models.URLField(blank=True, null=True)
    certificate = models.FileField(upload_to="mentors/certificates/", blank=True, null=True)

    VERIFICATION_CHOICES = [
        ('PENDING', 'Pending'),
        ('VERIFIED', 'Verified'),
        ('SUSPICIOUS', 'Suspicious'),
        ('UNVERIFIED', 'Unverified'),
    ]
    verification_status = models.CharField(max_length=20, choices=VERIFICATION_CHOICES, default='PENDING')
    fraud_score = models.IntegerField(default=0, help_text="0 = trustworthy, 100 = likely fraudulent")
    ai_verification_report = models.TextField(blank=True, null=True, help_text="AI-generated verification reasoning")

    @property
    def get_average_ratings(self):
        ratings = self.ratings.all()
        if not ratings.exists():
            return {
                'communication': 0,
                'knowledge_delivery': 0,
                'interaction': 0,
                'understanding_quality': 0,
                'overall': 0,
                'count': 0
            }

        avg_comm = sum(r.communication_rating for r in ratings) / ratings.count()
        avg_know = sum(r.knowledge_delivery_rating for r in ratings) / ratings.count()
        avg_inter = sum(r.interaction_rating for r in ratings) / ratings.count()
        avg_under = sum(r.understanding_quality_rating for r in ratings) / ratings.count()
        overall = (avg_comm + avg_know + avg_inter + avg_under) / 4

        return {
            'communication': round(avg_comm, 1),
            'knowledge_delivery': round(avg_know, 1),
            'interaction': round(avg_inter, 1),
            'understanding_quality': round(avg_under, 1),
            'overall': round(overall, 1),
            'count': ratings.count()
        }

    def __str__(self):
        return f"{self.user.username} - Mentor"


class MentorRating(models.Model):
    mentor = models.ForeignKey(MentorProfile, on_delete=models.CASCADE, related_name='ratings')
    startup = models.ForeignKey('startup.StartupProfile', on_delete=models.CASCADE, related_name='mentor_ratings')
    session = models.OneToOneField('mentors.MentorshipSession', on_delete=models.CASCADE, related_name='mentor_rating')

    communication_rating = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)], default=5)
    knowledge_delivery_rating = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)], default=5)
    interaction_rating = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)], default=5)
    understanding_quality_rating = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)], default=5)
    feedback = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def average_rating(self):
        return round(
            (self.communication_rating + self.knowledge_delivery_rating +
             self.interaction_rating + self.understanding_quality_rating) / 4, 1
        )

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.mentor.user.username} - Session {self.session.id} Rating"

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
            ('REQUESTED', 'Requested'),
            ('SCHEDULED', 'Scheduled'),
            ('COMPLETED', 'Completed'),
            ('CANCELLED', 'Cancelled'),
        ],
        default='REQUESTED'
    )
    meet_link = models.URLField(blank=True, null=True)
    calendar_event_id = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.startup.startup_name} → {self.mentor.user.username} ({self.topic})"

