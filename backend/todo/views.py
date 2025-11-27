from datetime import datetime
import csv
import io
import json
import uuid

from django.db import models
from django.db.models import Q, ProtectedError
from django.http import HttpResponse, JsonResponse, HttpResponseBadRequest
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404

from rest_framework import status, viewsets, filters
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
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


class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Category.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class NotificationSettingViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSettingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = NotificationSetting.objects.filter(owner=self.request.user)
        todo_id = self.request.query_params.get("todo")
        if todo_id:
            qs = qs.filter(todo_id=todo_id)
        return qs

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class TodoViewSet(viewsets.ModelViewSet):
    serializer_class = TodoSerializer
    permission_classes = [IsAuthenticated]

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["title", "description", "tags"]
    filterset_fields = ["created_at", "due_at", "priority", "category", "completed"]
    ordering_fields = ["created_at", "due_at", "priority"]

    def get_queryset(self):
        return Todo.objects.filter(owner=self.request.user).order_by("-created_at")

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        try:
            self.perform_destroy(instance)
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
        serializer = self.get_serializer(todo, context={"request": request})
        return Response(serializer.data)

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

        todo = get_object_or_404(Todo, id=todo_id, owner=request.user)

        if shared_to_email == request.user.email:
            return Response(
                {"error": "Không thể chia sẻ task cho chính bạn"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            shared_to_user = User.objects.get(email=shared_to_email)
        except User.DoesNotExist:
            return Response(
                {"error": "Người dùng với email này không tồn tại"},
                status=status.HTTP_404_NOT_FOUND,
            )

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

        serializer = TaskShareSerializer(task_share)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )

    @action(detail=False, methods=["get"], url_path="shared-with-me")
    def shared_with_me(self, request):
        shared_tasks = TaskShare.objects.filter(shared_to=request.user)
        serializer = TaskShareSerializer(shared_tasks, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="shared-by-me")
    def shared_by_me(self, request):
        shared_tasks = TaskShare.objects.filter(shared_by=request.user)
        serializer = TaskShareSerializer(shared_tasks, many=True)
        return Response(serializer.data)


@api_view(["GET"])
@permission_classes([AllowAny])
def share_link_view(request, share_link):
    try:
        ts = TaskShare.objects.get(share_link=share_link)
    except TaskShare.DoesNotExist:
        return Response(
            {"error": "Share link không tồn tại"}, status=status.HTTP_404_NOT_FOUND
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

class ReportViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'], url_path='progress')
    def progress_report(self, request):
        user = request.user
        todos = Todo.objects.filter(owner=user)

        total = todos.count()
        completed = todos.filter(completed=True).count()
        in_progress = total - completed

        data = {
            'total_tasks': total,
            'completed_tasks': completed,
            'incomplete_tasks': in_progress,
            'completion_rate': (completed / total * 100) if total else 0,
        }
        return Response(data)

    @action(detail=False, methods=['get'], url_path='timeline')
    def timeline_report(self, request):
        user = request.user
        # thống kê theo ngày tạo
        todos = Todo.objects.filter(owner=user).order_by('created_at')
        timeline = {}

        for t in todos:
            key = t.created_at.date().isoformat()
            if key not in timeline:
                timeline[key] = {'created': 0, 'completed': 0}
            timeline[key]['created'] += 1
            if t.completed:
                timeline[key]['completed'] += 1

        result = [
            {'date': k, 'created': v['created'], 'completed': v['completed']}
            for k, v in sorted(timeline.items())
        ]
        return Response(result)

    @action(detail=False, methods=['get'], url_path='by-priority')
    def by_priority_report(self, request):
        user = request.user
        todos = Todo.objects.filter(owner=user)

        stats = {}
        for t in todos:
            p = t.priority
            if p not in stats:
                stats[p] = {'priority': p, 'total': 0, 'completed': 0}
            stats[p]['total'] += 1
            if t.completed:
                stats[p]['completed'] += 1

        result = []
        for p, info in stats.items():
            total = info['total']
            completed = info['completed']
            info['completion_rate'] = (completed / total * 100) if total else 0
            result.append(info)

        return Response(result)

@api_view(['POST'])
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
    data = request.data

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
                "Low": 1, "low": 1,
                "Medium": 2, "medium": 2,
                "High": 3, "high": 3,
                "Urgent": 3, "urgent": 3,
            }
            return mapping.get(self.priority, 2)

    task = DummyTask(priority, estimated_duration_min)
    result = predict_task_on_time(task, extra_data=data, return_confidence=True)
    return Response(result)

@api_view(['POST'])
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

    task_data['owner'] = request.user
    task_data['completed'] = False
    task_data['tags'] = ''

    if task_data.get('due_at'):
        task_data['due_at'] = datetime.fromisoformat(task_data['due_at'])

    todo = Todo.objects.create(
        owner=request.user,
        title=task_data.get('title', 'Task mới'),
        description=task_data.get('description', ''),
        due_at=task_data.get('due_at'),
        priority=task_data.get('priority', 'Medium'),
        completed=False,
        tags='',
    )

    prediction = None
    try:
        prediction = predict_task_on_time(todo, return_confidence=True)
    except Exception as e:
        print(f"Prediction error: {e}")

    response_text = chatbot.generate_response(
        TodoSerializer(todo).data,
        prediction
    )

    return JsonResponse({
        'task': TodoSerializer(todo).data,
        'response': response_text,
        'prediction': prediction
    })

class PublicRegisterView(RegisterView):
    authentication_classes = []     
    permission_classes = [AllowAny]
    
class PublicLoginView(LoginView):
    """
    Login không yêu cầu token, cho phép anonymous.
    """
    authentication_classes = []      # TẮT TokenAuthentication ở đây
    permission_classes = [AllowAny]

