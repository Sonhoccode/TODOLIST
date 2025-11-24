from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User 

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

    def __str__(self):
        return self.title

    def is_overdue(self):
        """Kiểm tra công việc quá hạn hay chưa"""
        # Sửa để dùng 'due_at'
        return self.due_at and self.due_at < timezone.now()
    

# === 3. CHIA SẺ CÔNG VIỆC ===
class TaskShare(models.Model):
    """Model để chia sẻ công việc với những người dùng khác"""
    
    task = models.ForeignKey(Todo, on_delete=models.CASCADE, related_name='shares')
    shared_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shared_tasks_from')
    # Cho phép NULL để hỗ trợ link chia sẻ công khai (không chỉ định người nhận)
    shared_to = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shared_tasks_to', null=True, blank=True)
    
    permission = models.CharField(
        "Quyền",
        max_length=10,
        choices=PERMISSION_CHOICES,
        default='view'
    )
    
    created_at = models.DateTimeField("Ngày chia sẻ", auto_now_add=True)
    accepted = models.BooleanField("Đã chấp nhận", default=False)
    share_link = models.CharField("Link chia sẻ", max_length=255, unique=True, null=True, blank=True)
    
    class Meta:
        verbose_name = "Chia sẻ công việc"
        verbose_name_plural = "Chia sẻ công việc"
        unique_together = ('task', 'shared_to')
    
    def __str__(self):
        return f"{self.shared_by.username} chia sẻ '{self.task.title}' cho {self.shared_to.username}"


# === 4. XUẤT / NHẬP DANH SÁCH ===
class ExportLog(models.Model):
    """Theo dõi lịch sử xuất công việc"""
    
    EXPORT_FORMAT_CHOICES = [
        ('csv', 'CSV'),
        ('excel', 'Excel'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='export_logs')
    format = models.CharField("Định dạng", max_length=10, choices=EXPORT_FORMAT_CHOICES)
    file_path = models.CharField("Đường dẫn file", max_length=255)
    exported_count = models.IntegerField("Số công việc xuất")
    created_at = models.DateTimeField("Ngày xuất", auto_now_add=True)
    
    class Meta:
        verbose_name = "Nhật ký xuất"
        verbose_name_plural = "Nhật ký xuất"
    
    def __str__(self):
        return f"{self.user.username} - {self.format} - {self.created_at}"


# === 5. TÍCH HỢP LỊCH ===
class CalendarEvent(models.Model):
    """Sự kiện trên lịch (liên kết với Todo)"""
    
    todo = models.OneToOneField(Todo, on_delete=models.CASCADE, related_name='calendar_event')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='calendar_events')
    
    # Ngày tháng năm từ due_at
    date = models.DateField("Ngày sự kiện")
    start_time = models.TimeField("Giờ bắt đầu", null=True, blank=True)
    
    created_at = models.DateTimeField("Ngày tạo", auto_now_add=True)
    updated_at = models.DateTimeField("Ngày cập nhật", auto_now=True)
    
    class Meta:
        verbose_name = "Sự kiện lịch"
        verbose_name_plural = "Sự kiện lịch"
    
    def __str__(self):
        return f"{self.todo.title} - {self.date}"
    
class NotificationSetting(models.Model):
    CHANNEL_CHOICES = [
        ('email', 'Email'),
        ('push', 'Push Notification'),
    ]

    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notification_settings')
    todo = models.ForeignKey(Todo, on_delete=models.CASCADE, related_name='notification_settings')

    # Nhắc trước deadline bao nhiêu phút
    reminder_minutes = models.IntegerField("Nhắc trước (phút)", default=60)

    # Lưu kênh thông báo dạng "email,push"
    channels = models.CharField("Kênh thông báo", max_length=255, default='email')

    enabled = models.BooleanField("Bật nhắc nhở", default=True)
    created_at = models.DateTimeField("Ngày tạo", auto_now_add=True)
    updated_at = models.DateTimeField("Ngày cập nhật", auto_now=True)

    class Meta:
        verbose_name = "Cài đặt nhắc nhở"
        verbose_name_plural = "Cài đặt nhắc nhở"

    def __str__(self):
        return f"{self.owner.username} - {self.todo.title} - {self.reminder_minutes} phút trước"

    def get_channels_list(self):
        if not self.channels:
            return []
        return [c.strip() for c in self.channels.split(',') if c.strip()]


class SentNotification(models.Model):
    notification_setting = models.ForeignKey(NotificationSetting, on_delete=models.CASCADE, related_name='sent_notifications')
    todo = models.ForeignKey(Todo, on_delete=models.CASCADE, related_name='sent_notifications')
    sent_at = models.DateTimeField("Thời gian gửi", auto_now_add=True)

    class Meta:
        verbose_name = "Thông báo đã gửi"
        verbose_name_plural = "Thông báo đã gửi"
        unique_together = ('notification_setting', 'todo')

    def __str__(self):
        return f"{self.notification_setting} - {self.sent_at}"
