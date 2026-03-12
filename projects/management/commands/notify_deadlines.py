from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from projects.models import ProjectAssignment
from accounts.models import Notification


class Command(BaseCommand):
    help = "Notify freelancers when project deadlines are near"

    def add_arguments(self, parser):
        parser.add_argument(
            "--days",
            type=int,
            default=3,
            help="Number of days before deadline to notify"
        )

    def handle(self, *args, **options):
        days = options["days"]
        today = timezone.localdate()
        cutoff = today + timedelta(days=days)

        assignments = ProjectAssignment.objects.select_related(
            "project", "freelancer", "freelancer__user"
        ).filter(
            is_active=True,
            project__status__in=["PLANNED", "ONGOING"],
            project__end_date__isnull=False,
            project__end_date__lte=cutoff,
            project__end_date__gte=today,
            freelancer__isnull=False,
        )

        sent = 0
        for assignment in assignments:
            project = assignment.project
            freelancer_user = assignment.freelancer.user

            title = "Project deadline approaching"
            message = (
                f"Your project '{project.name}' is due on {project.end_date}. "
                f"Please make sure your submission is on time."
            )

            already_sent = Notification.objects.filter(
                user=freelancer_user,
                title=title,
                message=message,
                created_at__date=today
            ).exists()

            if already_sent:
                continue

            Notification.objects.create(
                user=freelancer_user,
                title=title,
                message=message
            )
            sent += 1

        self.stdout.write(self.style.SUCCESS(f"Deadline notifications sent: {sent}"))
