from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('startup', '0002_freelancerreport'),
    ]

    operations = [
        migrations.CreateModel(
            name='EmployeeRating',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timeliness_rating', models.IntegerField(choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')], default=5)),
                ('quality_rating', models.IntegerField(choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')], default=5)),
                ('communication_rating', models.IntegerField(choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')], default=5)),
                ('feedback', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('employee', models.ForeignKey(on_delete=models.deletion.CASCADE, related_name='ratings', to='startup.employee')),
                ('project', models.ForeignKey(on_delete=models.deletion.CASCADE, related_name='employee_ratings', to='projects.project')),
                ('startup', models.ForeignKey(on_delete=models.deletion.CASCADE, related_name='employee_ratings', to='startup.startupprofile')),
            ],
            options={
                'ordering': ['-created_at'],
                'unique_together': {('employee', 'project')},
            },
        ),
    ]
