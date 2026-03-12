from django.db import models
from accounts.models import CustomUser

class StartupProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name="startup_profile")
    startup_name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    founded_date = models.DateField(blank=True, null=True)
    industry = models.CharField(max_length=100, blank=True, null=True)
    logo = models.ImageField(upload_to='startup_logos/', blank=True, null=True)  # changed to ImageField

    def __str__(self):
        return self.startup_name


class Employee(models.Model):
    startup = models.ForeignKey(StartupProfile, on_delete=models.CASCADE, related_name='employees')
    name = models.CharField(max_length=255)
    role = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='employee_profiles/', blank=True, null=True)  # changed to ImageField
    linkedin_profile = models.URLField(blank=True, null=True)
    github_profile = models.URLField(blank=True, null=True)
    skills = models.TextField(blank=True, null=True)
    date_of_joining = models.DateField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    added_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.startup.startup_name})"


class FreelancerReport(models.Model):
    startup = models.ForeignKey(StartupProfile, on_delete=models.CASCADE, related_name="freelancer_reports")
    freelancer = models.ForeignKey('freelancer.FreelancerProfile', on_delete=models.CASCADE, related_name="reports")
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, related_name="freelancer_reports")
    proposal = models.ForeignKey('projects.ProjectProposal', on_delete=models.CASCADE, related_name="freelancer_reports")
    reason = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.startup.startup_name} reported {self.freelancer.full_name}"


class EmployeeRating(models.Model):
    startup = models.ForeignKey(StartupProfile, on_delete=models.CASCADE, related_name="employee_ratings")
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="ratings")
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, related_name="employee_ratings")

    timeliness_rating = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)], default=5)
    quality_rating = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)], default=5)
    communication_rating = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)], default=5)
    feedback = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def average_rating(self):
        return round((self.timeliness_rating + self.quality_rating + self.communication_rating) / 3, 1)

    class Meta:
        unique_together = ('employee', 'project')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.employee.name} - {self.project.name} Rating"
