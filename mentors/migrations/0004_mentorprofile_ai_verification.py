from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mentors', '0003_mentorshipsession_meet_link'),
    ]

    operations = [
        migrations.AddField(
            model_name='mentorprofile',
            name='github_url',
            field=models.URLField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='mentorprofile',
            name='certificate',
            field=models.FileField(blank=True, null=True, upload_to='mentors/certificates/'),
        ),
        migrations.AddField(
            model_name='mentorprofile',
            name='verification_status',
            field=models.CharField(choices=[('PENDING', 'Pending'), ('VERIFIED', 'Verified'), ('SUSPICIOUS', 'Suspicious'), ('UNVERIFIED', 'Unverified')], default='PENDING', max_length=20),
        ),
        migrations.AddField(
            model_name='mentorprofile',
            name='fraud_score',
            field=models.IntegerField(default=0, help_text='0 = trustworthy, 100 = likely fraudulent'),
        ),
        migrations.AddField(
            model_name='mentorprofile',
            name='ai_verification_report',
            field=models.TextField(blank=True, help_text='AI-generated verification reasoning', null=True),
        ),
    ]
