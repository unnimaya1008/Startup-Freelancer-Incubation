# startup/helpers.py (or inside views.py if you prefer)
from funding.models import InvestorProfile,FundingRound
from accounts.models import Notification

def notify_investors(funding: FundingRound):
    """
    Send notifications to either a single investor (if selected) 
    or all investors (if investor field is empty).
    """
    if funding.investor:
        # Notify the selected investor only
        Notification.objects.create(
            user=funding.investor.user,
            title="Funding Round Created",
            message=f"{funding.startup.startup_name} created a funding round: {funding.round_name} for ${funding.amount}"
        )
    else:
        # Notify all investors
        all_investors = InvestorProfile.objects.all()
        notifications = [
            Notification(
                user=investor.user,
                title="Funding Round Created",
                message=f"{funding.startup.startup_name} created a funding round: {funding.round_name} for ${funding.amount}"
            )
            for investor in all_investors
        ]
        Notification.objects.bulk_create(notifications)
