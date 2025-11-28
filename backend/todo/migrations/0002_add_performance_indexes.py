# Generated migration for performance optimization

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('todo', '0001_initial'),  # Adjust this to your last migration
    ]

    operations = [
        migrations.AddIndex(
            model_name='todo',
            index=models.Index(fields=['owner', '-created_at'], name='todo_owner_created_idx'),
        ),
        migrations.AddIndex(
            model_name='todo',
            index=models.Index(fields=['owner', 'completed'], name='todo_owner_completed_idx'),
        ),
        migrations.AddIndex(
            model_name='todo',
            index=models.Index(fields=['owner', 'priority'], name='todo_owner_priority_idx'),
        ),
        migrations.AddIndex(
            model_name='todo',
            index=models.Index(fields=['owner', 'category'], name='todo_owner_category_idx'),
        ),
        migrations.AddIndex(
            model_name='todo',
            index=models.Index(fields=['due_at'], name='todo_due_at_idx'),
        ),
    ]
