from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mentors', '0004_mentorprofile_ai_verification'),
    ]

    operations = [
        migrations.CreateModel(
            name='MentorRating',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('communication_rating', models.IntegerField(choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')], default=5)),
                ('knowledge_delivery_rating', models.IntegerField(choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')], default=5)),
                ('interaction_rating', models.IntegerField(choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')], default=5)),
                ('understanding_quality_rating', models.IntegerField(choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')], default=5)),
                ('feedback', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('mentor', models.ForeignKey(on_delete=models.deletion.CASCADE, related_name='ratings', to='mentors.mentorprofile')),
                ('session', models.OneToOneField(on_delete=models.deletion.CASCADE, related_name='mentor_rating', to='mentors.mentorshipsession')),
                ('startup', models.ForeignKey(on_delete=models.deletion.CASCADE, related_name='mentor_ratings', to='startup.startupprofile')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]
