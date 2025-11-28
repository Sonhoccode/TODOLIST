"""
Management command để tạo test tasks cho performance testing
Usage: python manage.py create_test_tasks --count 100
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from todo.models import Todo, Category
from django.utils import timezone
from datetime import timedelta
import random

User = get_user_model()

class Command(BaseCommand):
    help = 'Tạo test tasks để test performance'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=100,
            help='Số lượng tasks cần tạo (default: 100)'
        )
        parser.add_argument(
            '--username',
            type=str,
            default=None,
            help='Username của user (nếu không có sẽ dùng user đầu tiên)'
        )

    def handle(self, *args, **options):
        count = options['count']
        username = options['username']

        # Lấy user
        if username:
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'User "{username}" không tồn tại'))
                return
        else:
            user = User.objects.first()
            if not user:
                self.stdout.write(self.style.ERROR('Không có user nào trong database'))
                return

        self.stdout.write(f'Tạo {count} tasks cho user: {user.username}')

        # Tạo categories nếu chưa có
        categories = list(Category.objects.filter(owner=user))
        if not categories:
            cat_names = ['Công việc', 'Cá nhân', 'Học tập', 'Dự án']
            for name in cat_names:
                cat, _ = Category.objects.get_or_create(owner=user, name=name)
                categories.append(cat)
            self.stdout.write(f'Đã tạo {len(categories)} categories')

        priorities = ['Low', 'Medium', 'High', 'Urgent']
        tags_pool = ['urgent', 'backend', 'frontend', 'bug', 'feature', 'api', 'ui', 'test']

        created = 0
        for i in range(count):
            # Random data
            priority = random.choice(priorities)
            completed = random.choice([True, False, False, False])  # 25% completed
            category = random.choice(categories) if random.random() > 0.3 else None
            
            # Random due date (trong vòng 30 ngày)
            days_offset = random.randint(-15, 15)
            due_at = timezone.now() + timedelta(days=days_offset)
            
            # Random tags
            num_tags = random.randint(0, 3)
            tags = random.sample(tags_pool, num_tags) if num_tags > 0 else []

            Todo.objects.create(
                owner=user,
                title=f'Test Task #{i+1} - {priority}',
                description=f'Đây là task test số {i+1} để kiểm tra performance',
                priority=priority,
                completed=completed,
                category=category,
                due_at=due_at,
                tags=tags,
            )
            created += 1

            if (i + 1) % 50 == 0:
                self.stdout.write(f'Đã tạo {i+1}/{count} tasks...')

        self.stdout.write(self.style.SUCCESS(f'✅ Hoàn tất! Đã tạo {created} tasks'))
        self.stdout.write(f'User: {user.username} ({user.email})')
        self.stdout.write(f'Total tasks: {Todo.objects.filter(owner=user).count()}')
