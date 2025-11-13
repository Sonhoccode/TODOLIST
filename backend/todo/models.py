from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User # <-- Đã bật

class Category(models.Model):
    name = models.CharField("Tên danh mục", max_length=100)
    # Thêm 'owner' (liên kết với User)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='categories')

    class Meta:
        verbose_name = "Danh mục"
        verbose_name_plural = "Các danh mục"

    def __str__(self):
        return self.name


class Todo(models.Model):
    # Cập nhật choices để khớp React (viết hoa)
    PRIORITY_CHOICES = [
        ('Low', 'Thấp'),
        ('Medium', 'Trung bình'),
        ('High', 'Cao'),
        ('Urgent', 'Khẩn cấp'),
    ]

    # (Đã XÓA 'STATUS_CHOICES')

    # Thêm 'owner'
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='todos')
    
    title = models.CharField("Tiêu đề", max_length=200)
    description = models.TextField("Mô tả", blank=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL, # <-- Đổi thành SET_NULL (Tốt hơn)
        related_name='todos',
        null=True,
        blank=True,
        verbose_name="Danh mục"
    )
    priority = models.CharField("Mức ưu tiên", max_length=10, choices=PRIORITY_CHOICES, default='Medium')
    
    # (Đã XÓA 'status')
    
    created_at = models.DateTimeField("Ngày tạo", auto_now_add=True)

    # --- CÁC TRƯỜNG KHỚP VỚI REACT ---
    # Đổi 'deadline' thành 'due_at'
    due_at = models.DateTimeField("Thời hạn", null=True, blank=True)
    
    # Đổi 'reminder_time' thành 'remind_at'
    remind_at = models.DateTimeField("Thời gian nhắc nhở", null=True, blank=True)

    # Thêm trường 'completed' (boolean)
    completed = models.BooleanField(default=False)

    # Thêm trường 'tags' (dạng string)
    tags = models.CharField(max_length=255, blank=True)

    # Thêm trường nhắc hằng ngày
    daily_reminder_time = models.TimeField("Giờ nhắc hằng ngày", null=True, blank=True)


    class Meta:
        verbose_name = "Công việc"
        verbose_name_plural = "Các công việc"

    def __str__(self):
        return self.title

    def is_overdue(self):
        """Kiểm tra công việc quá hạn hay chưa"""
        # Sửa để dùng 'due_at'
        return self.due_at and self.due_at < timezone.now()