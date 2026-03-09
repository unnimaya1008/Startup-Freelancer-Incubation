from django.db import models
from accounts.models import CustomUser
from startup.models import StartupProfile

class InvestorProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name="investor_profile")
    company = models.CharField(max_length=200, blank=True, null=True)
    investment_focus = models.CharField(max_length=200, blank=True, null=True)
    total_invested = models.DecimalField(max_digits=15, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.user.username} - Investor"

class FundingRound(models.Model):
    startup = models.ForeignKey(StartupProfile, on_delete=models.CASCADE, related_name="funding_rounds")
    investor = models.ForeignKey(
        InvestorProfile,
        on_delete=models.CASCADE,
        related_name="fundings",
        null=True,           # ✅ allows blank in DB
        blank=True            # ✅ allows blank in forms
    )
    round_name = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    date = models.DateField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ('REQUESTED', 'Requested'),
            ('APPROVED', 'Approved'),
            ('REJECTED', 'Rejected')
        ],
        default='REQUESTED'
    )
    all_investors = models.BooleanField(default=False)
    
    status_history = models.TextField(default='', blank=True)

    def log_status_change(self, old_status, new_status):
        """Append a timestamped status change entry."""
        from django.utils import timezone
        entry = f"{timezone.now().strftime('%Y-%m-%d %H:%M:%S')} | {old_status} → {new_status}\n"
        self.status_history += entry
        self.save(update_fields=['status_history'])

    def __str__(self):
        return f"{self.startup.startup_name} - {self.round_name}"

    def clean(self):
        # Optional safeguard: enforce mutual exclusivity even outside form
        from django.core.exceptions import ValidationError
        if not self.all_investors and not self.investor:
            raise ValidationError("Either select an investor or choose 'all investors'.")
        if self.all_investors and self.investor:
            raise ValidationError("Cannot select both an investor and 'all investors'.")
