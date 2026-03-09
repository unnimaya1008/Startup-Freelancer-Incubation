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
