# Generated migration for AI fields

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('todo', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='todo',
            name='planned_start_at',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Thời gian bắt đầu dự kiến'),
        ),
        migrations.AddField(
            model_name='todo',
            name='estimated_duration_min',
            field=models.PositiveIntegerField(blank=True, null=True, verbose_name='Thời lượng ước tính (phút)'),
        ),
        migrations.AddField(
            model_name='todo',
            name='completed_at',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Thời gian hoàn thành'),
        ),
    ]
