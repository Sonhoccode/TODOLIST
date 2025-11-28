from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
from datetime import timedelta
from django.conf import settings

User = get_user_model()
# --- CHOICES ---
PERMISSION_CHOICES = [
    ('view', 'Xem'),
    ('edit', 'Chỉnh sửa'),
]

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
        indexes = [
            models.Index(fields=['owner', '-created_at']),
            models.Index(fields=['owner', 'completed']),
            models.Index(fields=['owner', 'priority']),
            models.Index(fields=['owner', 'category']),
            models.Index(fields=['due_at']),
        ]

    def __str__(self):
        return self.title

    def is_overdue(self):
        """Kiểm tra công việc quá hạn hay chưa"""
        # Sửa để dùng 'due_at'
        return self.due_at and self.due_at < timezone.now()
    

# === 3. CHIA SẺ CÔNG VIỆC ===
class TaskShare(models.Model):
    PERMISSION_CHOICES = (
        ("view", "Chỉ xem"),
        ("edit", "Được sửa"),
    )

    task = models.ForeignKey(
        "Todo",
        on_delete=models.CASCADE,
        related_name="shares",
    )
    shared_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="task_shares_created",
    )
    shared_to = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="task_shares_received",
        null=True,
        blank=True,
    )
    permission = models.CharField(
        max_length=10,
        choices=PERMISSION_CHOICES,
        default="view",
    )
    share_link = models.CharField(
        max_length=64,
        unique=True,
        db_index=True,
    )
    accepted = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Chia sẻ công việc"
        verbose_name_plural = "Chia sẻ công việc"

    def __str__(self):
        return f"Share(task={self.task_id}, by={self.shared_by_id}, to={self.shared_to_id})"

class ExportLog(models.Model):
    """
    Lưu lại lịch sử xuất danh sách todo:
    - user: ai export
    - format: csv/json/... (hiện tại dùng 'csv')
    - file_path: tên file hoặc đường dẫn tương đối
    - exported_count: số lượng task export
    - created_at: thời gian export
    """
    FORMAT_CHOICES = (
        ("csv", "CSV"),
        ("json", "JSON"),
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="todo_export_logs",
    )
    format = models.CharField(
        max_length=20,
        choices=FORMAT_CHOICES,
        default="csv",
    )
    file_path = models.CharField(
        max_length=255,
        blank=True,
    )
    exported_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Export {self.format} by {self.user} at {self.created_at:%Y-%m-%d %H:%M}"

class NotificationSetting(models.Model):
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="notification_settings",
    )
    todo = models.ForeignKey(
        "Todo",
        on_delete=models.CASCADE,
        related_name="notification_settings",
    )

    reminder_minutes = models.PositiveIntegerField(default=60)
    channels = models.CharField(max_length=255, default="email")
    enabled = models.BooleanField(default=True)

    last_sent_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("owner", "todo")
        verbose_name = "Cấu hình nhắc nhở"
        verbose_name_plural = "Cấu hình nhắc nhở"

    def __str__(self):
        return f"NotificationSetting(todo={self.todo_id}, owner={self.owner_id})"

    def get_channels_list(self):
        if not self.channels:
            return []
        return [c.strip() for c in self.channels.split(",") if c.strip()]

class CalendarEvent(models.Model):
    """
    Sự kiện lịch gắn với một Todo.
    Dùng cho API calendar / tasks-by-date.
    """
    todo = models.ForeignKey(
        "todo.Todo",
        on_delete=models.CASCADE,
        related_name="calendar_events",
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="calendar_events",
    )
    date = models.DateField()
    start_time = models.TimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"CalendarEvent({self.todo.title} @ {self.date} {self.start_time})"


class SentNotification(models.Model):
    notification_setting = models.ForeignKey(
        NotificationSetting,
        on_delete=models.CASCADE,
        related_name='sent_notifications'
    )
    todo = models.ForeignKey(
        Todo,
        on_delete=models.CASCADE,
        related_name='sent_notifications'
    )
    sent_at = models.DateTimeField("Thời gian gửi", auto_now_add=True)

    class Meta:
        verbose_name = "Thông báo đã gửi"
        verbose_name_plural = "Thông báo đã gửi"
        unique_together = ('notification_setting', 'todo')

    def __str__(self):
        return f"{self.notification_setting} - {self.sent_at}"

    