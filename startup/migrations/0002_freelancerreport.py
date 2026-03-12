from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('startup', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='FreelancerReport',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reason', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('freelancer', models.ForeignKey(on_delete=models.deletion.CASCADE, related_name='reports', to='freelancer.freelancerprofile')),
                ('project', models.ForeignKey(on_delete=models.deletion.CASCADE, related_name='freelancer_reports', to='projects.project')),
                ('proposal', models.ForeignKey(on_delete=models.deletion.CASCADE, related_name='freelancer_reports', to='projects.projectproposal')),
                ('startup', models.ForeignKey(on_delete=models.deletion.CASCADE, related_name='freelancer_reports', to='startup.startupprofile')),
            ],
        ),
    ]
