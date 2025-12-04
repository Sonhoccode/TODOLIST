from rest_framework import serializers
from .models import (
    Todo,
    Category,
    TaskShare,
    ExportLog,
    CalendarEvent,
    NotificationSetting,
)


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"
        read_only_fields = ["owner"]

    def validate_name(self, value):
        user = self.context["request"].user
        qs = Category.objects.filter(owner=user, name=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("Danh mục đã tồn tại.")
        return value


class TagsField(serializers.Field):
    def to_representation(self, value):
        if not value:
            return []
        return [tag.strip() for tag in value.split(",") if tag.strip()]

    def to_internal_value(self, data):
        if not isinstance(data, list):
            raise serializers.ValidationError("Tags phải là một mảng (array).")
        return ", ".join(tag.strip() for tag in data if tag.strip())


class TodoSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)
    tags = TagsField(required=False)

    class Meta:
        model = Todo
        fields = [
            "id",
            "title",
            "description",
            "category",
            "priority",
            "created_at",
            "due_at",
            "remind_at",
            "completed",
            "tags",
            "category_name",
            "daily_reminder_time",
            "owner",
        ]
        read_only_fields = ["owner", "created_at", "category_name"]


# === SHARE TASK ===
class TaskShareSerializer(serializers.ModelSerializer):
    shared_by_username = serializers.SerializerMethodField(read_only=True)
    shared_to_username = serializers.SerializerMethodField(read_only=True)
    task_title = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = TaskShare
        fields = [
            "id",
            "task",
            "shared_by",
            "shared_to",
            "permission",
            "created_at",
            "accepted",
            "share_link",
            "shared_by_username",
            "shared_to_username",
            "task_title",
        ]
        read_only_fields = ["shared_by", "created_at", "share_link"]

    def get_shared_by_username(self, obj):
        try:
            return obj.shared_by.username if obj.shared_by else None
        except Exception:
            return None

    def get_shared_to_username(self, obj):
        try:
            return obj.shared_to.username if obj.shared_to else None
        except Exception:
            return None

    def get_task_title(self, obj):
        try:
            return obj.task.title if obj.task else None
        except Exception:
            return None

    def validate(self, attrs):
        request = self.context.get("request")
        user = getattr(request, "user", None)

        task = attrs.get("task")
        if not task:
            raise serializers.ValidationError({"task": "task field is required."})

        if user and task.owner != user:
            raise serializers.ValidationError(
                {"task": "Bạn không có quyền chia sẻ công việc này."}
            )

        return attrs

    def create(self, validated_data):
        import uuid

        request = self.context.get("request")
        user = getattr(request, "user", None)

        task = validated_data.get("task")
        shared_to = validated_data.get("shared_to", None)
        permission = validated_data.get("permission", "view")

        # Tăng độ dài share_link lên 32 ký tự để bảo mật hơn
        share_link = str(uuid.uuid4()).replace('-', '')[:32]

        ts = TaskShare.objects.create(
            task=task,
            shared_by=user,
            shared_to=shared_to,
            permission=permission,
            share_link=share_link,
        )
        return ts


# === LỊCH ===
class ExportLogSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = ExportLog
        fields = ["id", "user", "username", "format", "file_path", "exported_count", "created_at"]
        read_only_fields = ["user", "file_path", "exported_count", "created_at"]


class CalendarEventSerializer(serializers.ModelSerializer):
    task_title = serializers.CharField(source="todo.title", read_only=True)
    task_description = serializers.CharField(source="todo.description", read_only=True)
    task_priority = serializers.CharField(source="todo.priority", read_only=True)
    task_completed = serializers.BooleanField(source="todo.completed", read_only=True)

    class Meta:
        model = CalendarEvent
        fields = [
            "id",
            "todo",
            "user",
            "date",
            "start_time",
            "created_at",
            "updated_at",
            "task_title",
            "task_description",
            "task_priority",
            "task_completed",
        ]
        read_only_fields = ["user", "created_at", "updated_at"]


# === THÔNG BÁO / NHẮC VIỆC ===
class NotificationSettingSerializer(serializers.ModelSerializer):
    todo_title = serializers.CharField(source="todo.title", read_only=True)
    channels_list = serializers.SerializerMethodField()

    class Meta:
        model = NotificationSetting
        fields = [
            "id",
            "todo",
            "todo_title",
            "reminder_minutes",
            "channels",
            "channels_list",
            "enabled",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["owner", "created_at", "updated_at"]

    def get_channels_list(self, obj):
        return obj.get_channels_list()

    def validate_todo(self, value):
        user = self.context["request"].user
        if value.owner != user:
            raise serializers.ValidationError("Bạn không có quyền tạo nhắc nhở cho Todo này.")
        return value
