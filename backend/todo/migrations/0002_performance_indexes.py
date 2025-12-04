# Generated migration for performance optimization

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('todo', '0001_initial'),
    ]

    operations = [
        # Add indexes to Todo model
        migrations.AlterField(
            model_name='todo',
            name='title',
            field=models.CharField(db_index=True, max_length=200, verbose_name='Tiêu đề'),
        ),
        migrations.AlterField(
            model_name='todo',
            name='priority',
            field=models.CharField(
                choices=[('Low', 'Thấp'), ('Medium', 'Trung bình'), ('High', 'Cao'), ('Urgent', 'Khẩn cấp')],
                db_index=True,
                default='Medium',
                max_length=10,
                verbose_name='Mức ưu tiên'
            ),
        ),
        migrations.AlterField(
            model_name='todo',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Ngày tạo'),
        ),
        migrations.AlterField(
            model_name='todo',
            name='due_at',
            field=models.DateTimeField(blank=True, db_index=True, null=True, verbose_name='Thời hạn'),
        ),
        migrations.AlterField(
            model_name='todo',
            name='completed',
            field=models.BooleanField(db_index=True, default=False),
        ),
        
        # Add composite indexes
        migrations.AddIndex(
            model_name='todo',
            index=models.Index(fields=['owner', 'completed'], name='todo_owner_completed_idx'),
        ),
        migrations.AddIndex(
            model_name='todo',
            index=models.Index(fields=['owner', 'due_at'], name='todo_owner_due_at_idx'),
        ),
        migrations.AddIndex(
            model_name='todo',
            index=models.Index(fields=['owner', 'priority'], name='todo_owner_priority_idx'),
        ),
        
        # Update TaskShare model
        migrations.AlterField(
            model_name='taskshare',
            name='share_link',
            field=models.CharField(db_index=True, max_length=32, unique=True),
        ),
        migrations.AlterField(
            model_name='taskshare',
            name='accepted',
            field=models.BooleanField(db_index=True, default=False),
        ),
    ]
