# todo/views.py
from datetime import datetime, timedelta
import csv
import io
import json
import uuid

from django.db import models
from django.db.models import Q, ProtectedError, Count
from django.http import HttpResponse, JsonResponse, HttpResponseBadRequest
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from todo.services.email_zoho import send_email
from django.conf import settings

from rest_framework import status, viewsets, filters
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from dj_rest_auth.views import LoginView
from dj_rest_auth.registration.views import RegisterView

from django.contrib.auth.models import User

from .models import (
    Todo,
    Category,
    TaskShare,
    ExportLog,
    CalendarEvent,
    NotificationSetting,
    SentNotification,
)
from .serializers import (
    TodoSerializer,
    CategorySerializer,
    TaskShareSerializer,
    CalendarEventSerializer,
    NotificationSettingSerializer,
)
from .services.ai import predict_task_on_time
from .services.chatbot import TaskChatbot


# ============== Category ==============

class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None  # Tắt pagination cho categories

    def get_queryset(self):
        return Category.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


# ============== Notification Setting ==============

class NotificationSettingViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSettingSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None  # Tắt pagination cho notifications

    def get_queryset(self):
        qs = NotificationSetting.objects.filter(owner=self.request.user)
        todo_id = self.request.query_params.get("todo")
        if todo_id:
            qs = qs.filter(todo_id=todo_id)
        return qs

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


# ============== Todo ==============

# Custom pagination class
class TodoPagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 100


class TodoViewSet(viewsets.ModelViewSet):
    serializer_class = TodoSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = TodoPagination

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    search_fields = ["title", "description", "tags"]
    filterset_fields = ["created_at", "due_at", "priority", "category", "completed"]
    ordering_fields = ["created_at", "due_at", "priority"]

    def get_queryset(self):
        # Tối ưu query với select_related
        return (
            Todo.objects.filter(owner=self.request.user)
            .select_related("category", "owner")
            .order_by("-created_at")
        )

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
        self._clear_user_cache(self.request.user.id)
    
    def perform_update(self, serializer):
        serializer.save()
        self._clear_user_cache(self.request.user.id)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        try:
            self.perform_destroy(instance)
            self._clear_user_cache(request.user.id)
        except Exception as e:
            print("ERROR_WHEN_DELETING_TODO:", repr(e))
            return Response(
                {
                    "error": "Lỗi khi xoá task",
                    "detail": str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["patch"], url_path="toggle-status")
    def toggle_status(self, request, pk=None):
        todo = self.get_object()
        todo.completed = not todo.completed
        todo.save()
        # Clear cache
        self._clear_user_cache(request.user.id)
        serializer = self.get_serializer(todo, context={"request": request})
        return Response(serializer.data)
    
    def _clear_user_cache(self, user_id):
        from django.core.cache import cache
        cache.delete(f"report_{user_id}_progress")
        cache.delete(f"report_{user_id}_priority")

    # =========== CHIA SẺ CÔNG VIỆC ===========

    @action(detail=False, methods=["post"], url_path="share")
    def share_task(self, request, pk=None):
        """
        POST /api/todos/share/
        body: {
          "todo_id": 1,
          "shared_to_email": "abc@example.com",
          "permission": "view" | "edit"
        }
        """
        todo_id = request.data.get("todo_id")
        shared_to_email = request.data.get("shared_to_email")
        permission = request.data.get("permission", "view")

        if not todo_id:
            return Response(
                {"error": "todo_id là bắt buộc"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not shared_to_email:
            return Response(
                {"error": "shared_to_email là bắt buộc"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Lấy task, đảm bảo thuộc về user đang login
        todo = get_object_or_404(Todo, id=todo_id, owner=request.user)

        # Không cho share cho chính mình
        if shared_to_email == request.user.email:
            return Response(
                {"error": "Không thể chia sẻ task cho chính bạn"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Tìm user nhận share bằng email
        try:
            shared_to_user = User.objects.get(email=shared_to_email)
        except User.DoesNotExist:
            return Response(
                {"error": "Người dùng với email này không tồn tại"},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Tạo share_link ngắn
        share_link = str(uuid.uuid4())[:8]

        task_share, created = TaskShare.objects.update_or_create(
            task=todo,
            shared_to=shared_to_user,
            defaults={
                "shared_by": request.user,
                "permission": permission,
                "share_link": share_link,
            },
        )

        # Gửi mail mời
        frontend_url = getattr(settings, "FRONTEND_URL")
        share_url = f"{frontend_url}/share/{share_link}"

        subject = f"{request.user.username} đã chia sẻ một task cho bạn"
        message = f"""
Chào {shared_to_user.username},

{request.user.username} vừa chia sẻ cho bạn một task:

- Tiêu đề: {todo.title}
- Mô tả: {todo.description}
- Quyền: {permission}

Nhấn vào link sau để xem và chấp nhận:
{share_url}
"""

        email_sent = send_email(
            subject=subject,
            text=message,
            to=shared_to_user.email,
        )

        serializer = TaskShareSerializer(task_share)
        data = serializer.data
        if not email_sent:
            data["warning"] = "Không thể gửi email thông báo. Vui lòng kiểm tra cấu hình Zoho Mail."

        return Response(
            data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )

    @action(detail=False, methods=["get"], url_path="shared-with-me")
    def shared_with_me(self, request):
        # Tối ưu với select_related
        shared_tasks = TaskShare.objects.filter(
            shared_to=request.user
        ).select_related('task', 'shared_by', 'shared_to')
        serializer = TaskShareSerializer(shared_tasks, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="shared-by-me")
    def shared_by_me(self, request):
        # Tối ưu với select_related
        shared_tasks = TaskShare.objects.filter(
            shared_by=request.user
        ).select_related('task', 'shared_by', 'shared_to')
        serializer = TaskShareSerializer(shared_tasks, many=True)
        return Response(serializer.data)


# ============== Share link public & accept ==============

@api_view(["GET"])
@permission_classes([AllowAny])
def share_link_view(request, share_link):
    try:
        ts = TaskShare.objects.get(share_link=share_link)
    except TaskShare.DoesNotExist:
        return Response(
            {"error": "Share link không tồn tại"},
            status=status.HTTP_404_NOT_FOUND,
        )

    data = {
        "task_id": ts.task.id,
        "task_title": ts.task.title,
        "task_description": ts.task.description,
        "permission": ts.permission,
        "shared_by": ts.shared_by.username,
        "accepted": ts.accepted,
    }
    return Response(data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def accept_share(request, share_link):
    try:
        ts = TaskShare.objects.get(share_link=share_link, shared_to=request.user)
    except TaskShare.DoesNotExist:
        return Response(
            {"error": "Share link không hợp lệ hoặc không thuộc về bạn"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    ts.accepted = True
    ts.save()

    return Response({"status": "accepted"})


# ============== Report ==============

class ReportViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    
    def get_cache_key(self, user_id, report_type):
        return f"report_{user_id}_{report_type}"

    @action(detail=False, methods=["get"], url_path="progress")
    def progress_report(self, request):
        from django.core.cache import cache
        
        user = request.user
        cache_key = self.get_cache_key(user.id, 'progress')
        
        # Try cache first
        cached = cache.get(cache_key)
        if cached:
            return Response(cached)
        
        # Calculate if not cached
        stats = Todo.objects.filter(owner=user).aggregate(
            total=Count('id'),
            completed=Count('id', filter=Q(completed=True))
        )
        
        total = stats['total']
        completed = stats['completed']
        in_progress = total - completed

        data = {
            "total_tasks": total,
            "completed_tasks": completed,
            "incomplete_tasks": in_progress,
            "completion_rate": (completed / total * 100) if total else 0,
        }
        
        # Cache for 60 seconds
        cache.set(cache_key, data, 60)
        return Response(data)

    @action(detail=False, methods=["get"], url_path="timeline")
    def timeline_report(self, request):
        user = request.user
        todos = (
            Todo.objects.filter(owner=user)
            .only("id", "created_at", "completed")
            .order_by("created_at")
        )
        timeline = {}

        for t in todos:
            key = t.created_at.date().isoformat()
            if key not in timeline:
                timeline[key] = {"created": 0, "completed": 0}
            timeline[key]["created"] += 1
            if t.completed:
                timeline[key]["completed"] += 1

        result = [
            {"date": k, "created": v["created"], "completed": v["completed"]}
            for k, v in sorted(timeline.items())
        ]
        return Response(result)

    @action(detail=False, methods=["get"], url_path="by-priority")
    def by_priority_report(self, request):
        from django.core.cache import cache
        
        user = request.user
        cache_key = self.get_cache_key(user.id, 'priority')
        
        # Try cache first
        cached = cache.get(cache_key)
        if cached:
            return Response(cached)
        
        # Calculate if not cached
        stats = Todo.objects.filter(owner=user).values('priority').annotate(
            total=Count('id'),
            completed=Count('id', filter=Q(completed=True))
        )

        result = []
        for stat in stats:
            total = stat['total']
            completed = stat['completed']
            result.append({
                'priority': stat['priority'],
                'total': total,
                'completed': completed,
                'completion_rate': (completed / total * 100) if total else 0
            })

        # Cache for 60 seconds
        cache.set(cache_key, result, 60)
        return Response(result)


# ============== AI Predict ==============

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def predict_task_completion(request):
    """
    Dự đoán khả năng hoàn thành task đúng hạn:
    - Nếu gửi task_id: lấy task của user rồi predict
    - Nếu gửi dữ liệu rời: dùng DummyTask để predict thử
    """
    try:
        data = json.loads(request.body.decode())
    except Exception:
        return HttpResponseBadRequest("JSON không hợp lệ")

    task_id = data.get("task_id")
    if task_id:
        try:
            task = Todo.objects.get(id=task_id, owner=request.user)
        except Todo.DoesNotExist:
            return Response(
                {"error": "Task không tồn tại"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        result = predict_task_on_time(task, return_confidence=True)
        return Response(result)

    priority = data.get("priority", "Medium")
    estimated_duration_min = data.get("estimated_duration_min")

    if estimated_duration_min is None:
        return Response(
            {"error": "Thiếu estimated_duration_min"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    class DummyTask:
        def __init__(self, priority, estimated_duration_min):
            self.priority = priority
            self.estimated_duration_min = estimated_duration_min
            self.created_at = timezone.now()
            self.planned_start_at = None

        @property
        def priority_numeric(self):
            mapping = {
                "Low": 1,
                "low": 1,
                "Medium": 2,
                "medium": 2,
                "High": 3,
                "high": 3,
                "Urgent": 3,
                "urgent": 3,
            }
            return mapping.get(self.priority, 2)

    task = DummyTask(priority, estimated_duration_min)
    result = predict_task_on_time(task, extra_data=data, return_confidence=True)
    return Response(result)


# ============== AI Scheduler ==============

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def schedule_tasks_today(request):
    """
    AI auto-schedule tasks for today
    POST /api/schedule/today/
    Body: { "available_hours": 8, "start_hour": 9 }
    """
    from todo.services.scheduler import AITaskScheduler
    
    available_hours = request.data.get("available_hours", 8)
    start_hour = request.data.get("start_hour", 9)
    
    scheduler = AITaskScheduler(request.user)
    result = scheduler.schedule_today(available_hours, start_hour)
    
    return Response(result)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def schedule_tasks_week(request):
    """
    AI auto-schedule tasks for the week
    POST /api/schedule/week/
    Body: { "hours_per_day": 6 }
    """
    from todo.services.scheduler import AITaskScheduler
    
    hours_per_day = request.data.get("hours_per_day", 6)
    
    scheduler = AITaskScheduler(request.user)
    result = scheduler.schedule_week(hours_per_day)
    
    return Response(result)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def apply_schedule(request):
    """
    Apply suggested schedule to tasks
    POST /api/schedule/apply/
    Body: { "schedule": [...] }
    """
    schedule = request.data.get("schedule", [])
    
    if not schedule:
        return Response(
            {"error": "No schedule provided"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Update tasks with scheduled times
    updated_count = 0
    for item in schedule:
        try:
            task = Todo.objects.get(id=item['task_id'], owner=request.user)
            task.due_at = datetime.fromisoformat(item['end_time'])
            task.save()
            updated_count += 1
        except Todo.DoesNotExist:
            continue
    
    return Response({
        "success": True,
        "updated_count": updated_count
    })


# ============== Chatbot tạo task ==============

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def chatbot_create_task(request):
    """
    Chatbot endpoint:
    Input:  { "message": "Thêm task học Python 2 tiếng chiều mai" }
    Output: { "task": {...}, "response": "...", "prediction": {...} }
    """
    message = request.data.get("message")
    if not message:
        return HttpResponseBadRequest("Message không được trống")

    chatbot = TaskChatbot()
    task_data = chatbot.parse_message(message)

    # Parse due_at - FIXED: Handle timezone properly
    due_at = None
    if task_data.get("due_at"):
        try:
            # Parse ISO string and ensure it's timezone-aware
            due_at_str = task_data["due_at"]
            if 'T' in due_at_str:
                due_at = datetime.fromisoformat(due_at_str.replace('Z', '+00:00'))
            else:
                # If no time component, parse as date only
                due_at = datetime.fromisoformat(due_at_str)
            
            # Make timezone-aware if needed
            if due_at.tzinfo is None:
                due_at = timezone.make_aware(due_at)
        except Exception as e:
            print(f"Error parsing due_at: {e}, value: {task_data.get('due_at')}")
            pass

    todo = Todo.objects.create(
        owner=request.user,
        title=task_data.get("title", "Task mới"),
        description=task_data.get("description", ""),
        due_at=due_at,
        priority=task_data.get("priority", "Medium"),
        completed=False,
        tags="",
    )

    prediction = None
    try:
        prediction = predict_task_on_time(todo, return_confidence=True)
    except Exception as e:
        print(f"Prediction error: {e}")

    response_text = chatbot.generate_response(
        TodoSerializer(todo).data,
        prediction,
    )

    return JsonResponse(
        {
            "task": TodoSerializer(todo).data,
            "response": response_text,
            "prediction": prediction,
        }
    )


# ============== Public Auth Views ==============

class PublicRegisterView(RegisterView):
    authentication_classes = []
    permission_classes = [AllowAny]


class PublicLoginView(LoginView):
    """
    Login không yêu cầu token, cho phép anonymous.
    """
    authentication_classes = []
    permission_classes = [AllowAny]
