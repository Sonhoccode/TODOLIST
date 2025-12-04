from datetime import timedelta

from django.core.management.base import BaseCommand
from todo.services.email_zoho import send_email
from django.utils import timezone

from todo.models import NotificationSetting


class Command(BaseCommand):
    help = "Gửi email nhắc nhở các công việc sắp đến hạn cho người dùng."

    def handle(self, *args, **options):
        now = timezone.now()
        qs = NotificationSetting.objects.select_related("todo", "owner")

        sent_count = 0
        skipped = 0

        for setting in qs:
            todo = setting.todo
            user = setting.owner

            if not setting.enabled:
                skipped += 1
                continue

            if todo.completed:
                skipped += 1
                continue

            if not todo.due_at:
                skipped += 1
                continue

            # Không nhắc nếu đã quá hạn luôn
            if now > todo.due_at:
                skipped += 1
                continue

            minutes = setting.reminder_minutes or 60
            remind_time = todo.due_at - timedelta(minutes=minutes)

            if now < remind_time:
                skipped += 1
                continue

            if setting.last_sent_at is not None:
                skipped += 1
                continue

            if not user.email:
                skipped += 1
                continue

            subject = f"Nhắc nhở công việc: {todo.title}"
            lines = [
                f"Chào {user.get_username() or user.email},",
                "",
                "Đây là email nhắc nhở công việc bạn đã bật:",
                f"- Tiêu đề: {todo.title}",
                f"- Ưu tiên: {todo.priority}",
            ]

            local_due = timezone.localtime(todo.due_at)
            lines.append(f"- Đến hạn lúc: {local_due.strftime('%d/%m/%Y %H:%M')}")

            if todo.description:
                lines.append("")
                lines.append(f"Mô tả: {todo.description}")

            lines.append("")
            lines.append("Đây là email tự động từ hệ thống quản lý công việc.")
            message = "\n".join(lines)

            try:
                send_email(
                    subject=subject,
                    text=message,
                    to=user.email,
                ) fail_silently=False,
                )
                setting.last_sent_at = now
                setting.save(update_fields=["last_sent_at"])
                sent_count += 1
            except Exception as e:
                self.stderr.write(
                    self.style.ERROR(
                        f"Lỗi gửi email cho user={user.id}, todo={todo.id}: {e}"
                    )
                )
                skipped += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Hoàn thành. Đã gửi {sent_count} email, bỏ qua {skipped} cấu hình."
            )
        )
