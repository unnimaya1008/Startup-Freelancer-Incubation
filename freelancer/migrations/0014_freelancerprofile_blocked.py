from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('freelancer', '0013_freelancerprofile_ai_verification_report_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='freelancerprofile',
            name='is_blocked',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='freelancerprofile',
            name='blocked_reason',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='freelancerprofile',
            name='blocked_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
