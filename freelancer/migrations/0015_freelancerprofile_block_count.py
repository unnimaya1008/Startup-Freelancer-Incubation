from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('freelancer', '0014_freelancerprofile_blocked'),
    ]

    operations = [
        migrations.AddField(
            model_name='freelancerprofile',
            name='block_count',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='freelancerprofile',
            name='permanently_removed',
            field=models.BooleanField(default=False),
        ),
    ]
