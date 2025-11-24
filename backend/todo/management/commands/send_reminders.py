from django.core.management.base import BaseCommand
from django.utils import timezone
from todo.models import NotificationSetting, SentNotification

class Command(BaseCommand):
    help = "Gửi nhắc nhở todo theo NotificationSetting"

    def handle(self, *args, **options):
        now = timezone.now()
        settings = NotificationSetting.objects.filter(enabled=True).select_related('todo', 'owner')

        for setting in settings:
            todo = setting.todo
            if not todo.due_at:
                continue

            reminder_time = todo.due_at - timezone.timedelta(minutes=setting.reminder_minutes)

            if reminder_time <= now <= todo.due_at:
                already_sent = SentNotification.objects.filter(
                    notification_setting=setting,
                    todo=todo
                ).exists()
                if already_sent:
                    continue

                # TODO: gửi email / push thực sự (hiện tại chỉ print)
                print(f"[REMINDER] Nhắc user {setting.owner.username} về task: {todo.title}")

                SentNotification.objects.create(
                    notification_setting=setting,
                    todo=todo
                )
