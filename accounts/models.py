from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models

class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('ADMIN', 'Admin'),
        ('STARTUP', 'Startup'),
        ('FREELANCER', 'Freelancer'),
        ('MENTOR', 'Mentor'),
        ('INVESTOR', 'Investor'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='STARTUP')
    created_at = models.DateTimeField(auto_now_add=True)

    # override to avoid clashes
    groups = models.ManyToManyField(
        Group,
        related_name='customuser_set',  # <--- change related_name
        blank=True,
        help_text='The groups this user belongs to.'
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='customuser_set',  # <--- change related_name
        blank=True,
        help_text='Specific permissions for this user.'
    )

    def save(self, *args, **kwargs):
        if self.is_superuser:
            self.role = 'ADMIN'
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.username} ({self.role})"

# -----------------------------
# Notifications and Messaging
# -----------------------------
class Notification(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="notifications")
    title = models.CharField(max_length=200)
    message = models.TextField()
    read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def mark_as_read(self):
        if not self.read:
            self.read = True
            self.save()

    def __str__(self):
        return f"{self.user.username} - {self.title}"

class Message(models.Model):
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="sent_messages")
    receiver = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="received_messages")
    subject = models.CharField(max_length=200)
    body = models.TextField()
    read = models.BooleanField(default=False)
    sent_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender.username} -> {self.receiver.username}: {self.subject}"

