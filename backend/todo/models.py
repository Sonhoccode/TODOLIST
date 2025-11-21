from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

class Category(models.Model):
    name = models.CharField("Tên danh mục", max_length=100)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='categories')

    class Meta:
        verbose_name = "Danh mục"
        verbose_name_plural = "Các danh mục"
        constraints = [
            models.UniqueConstraint(
            fields=['owner', 'name'],
            name='unique_category_per_user'
            )
        ]

    def __str__(self):
        return self.name


class Todo(models.Model):
    PRIORITY_CHOICES = [
        ('Low', 'Thấp'),
        ('Medium', 'Trung bình'),
        ('High', 'Cao'),
        ('Urgent', 'Khẩn cấp'),
    ]

    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='todos')
    title = models.CharField("Tiêu đề", max_length=200)
    description = models.TextField("Mô tả", blank=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        related_name='todos',
        null=True,
        blank=True,
        verbose_name="Danh mục"
    )
    priority = models.CharField("Mức ưu tiên", max_length=10, choices=PRIORITY_CHOICES, default='Medium')
    created_at = models.DateTimeField("Ngày tạo", auto_now_add=True)
    due_at = models.DateTimeField("Thời hạn", null=True, blank=True)
    remind_at = models.DateTimeField("Thời gian nhắc nhở", null=True, blank=True)
    completed = models.BooleanField(default=False)
    tags = models.CharField(max_length=255, blank=True)
    daily_reminder_time = models.TimeField("Giờ nhắc hằng ngày", null=True, blank=True)
    
    # AI fields
    planned_start_at = models.DateTimeField("Thời gian bắt đầu dự kiến", null=True, blank=True)
    estimated_duration_min = models.PositiveIntegerField("Thời lượng ước tính (phút)", null=True, blank=True)
    completed_at = models.DateTimeField("Thời gian hoàn thành", null=True, blank=True)

    class Meta:
        verbose_name = "Công việc"
        verbose_name_plural = "Các công việc"

    def __str__(self):
        return self.title

    def is_overdue(self):
        return self.due_at and self.due_at < timezone.now()

    @property
    def priority_numeric(self):
        mapping = {"Low": 1, "low": 1, "Medium": 2, "medium": 2, "High": 3, "high": 3, "Urgent": 3, "urgent": 3}
        return mapping.get(self.priority, 2)

    @property
    def start_dt(self):
        return self.planned_start_at or self.created_at

    @property
    def start_hour(self):
        return (self.start_dt or timezone.now()).hour

    @property
    def day_of_week(self):
        return (self.start_dt or timezone.now()).weekday() + 1

    @property
    def effective_duration_min(self):
        if self.estimated_duration_min:
            return int(self.estimated_duration_min)
        if self.due_at and self.start_dt:
            return int(max(1, (self.due_at - self.start_dt).total_seconds() // 60))
        return 60

    def save(self, *args, **kwargs):
        if self.completed and self.completed_at is None:
            self.completed_at = timezone.now()
        elif not self.completed:
            self.completed_at = None
        super().save(*args, **kwargs)