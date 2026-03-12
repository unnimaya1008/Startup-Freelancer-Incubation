from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mentors', '0002_mentorprofile_profile_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='mentorshipsession',
            name='meet_link',
            field=models.URLField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='mentorshipsession',
            name='calendar_event_id',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
