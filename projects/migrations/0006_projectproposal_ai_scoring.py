from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0005_project_required_experience'),
    ]

    operations = [
        migrations.AddField(
            model_name='projectproposal',
            name='ai_score',
            field=models.IntegerField(default=0, help_text='AI score for proposal quality (0-100)'),
        ),
        migrations.AddField(
            model_name='projectproposal',
            name='ai_report',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='projectproposal',
            name='rank_score',
            field=models.IntegerField(default=0, help_text='Combined ranking score for sorting proposals'),
        ),
    ]
