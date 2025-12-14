from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0003_alter_project_owner'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='status',
            field=models.CharField(
                choices=[('active', 'Active'), ('in_progress', 'In Progress'), ('completed', 'Completed')],
                default='active',
                max_length=20
            ),
        ),
    ]
