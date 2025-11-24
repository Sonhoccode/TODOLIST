from datetime import datetime, timedelta
import csv
import io
import json
import uuid

from django.db.models import Q
from django.http import HttpResponse, JsonResponse, HttpResponseBadRequest
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import status, viewsets, filters
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from dj_rest_auth.views import LoginView
from dj_rest_auth.registration.views import RegisterView
from rest_framework.permissions import AllowAny
from rest_framework.authentication import TokenAuthentication
from django.db.models import ProtectedError



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
    permission_classes = [IsAuthenticated] # <-- Đã bật
    
    def get_queryset(self):
        # Chỉ trả về Category của user đã đăng nhập
        return Category.objects.filter(owner=self.request.user)
        
    def perform_create(self, serializer):
        # Tự động gán owner khi tạo
        serializer.save(owner=self.request.user)


class NotificationSettingViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSettingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return NotificationSetting.objects.filter(owner=self.request.user).select_related('todo')

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(detail=False, methods=['get'], url_path='by-todo')
    def by_todo(self, request):
        todo_id = request.query_params.get('todo_id')
        if not todo_id:
            return Response({'error': 'Thiếu tham số todo_id'}, status=400)

        qs = self.get_queryset().filter(todo_id=todo_id)
        data = NotificationSettingSerializer(qs, many=True, context={'request': request}).data
        return Response({'count': len(data), 'settings': data})


class TodoViewSet(viewsets.ModelViewSet):
    serializer_class = TodoSerializer
    permission_classes = [IsAuthenticated]

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description', 'tags']
    filterset_fields = ['created_at', 'due_at', 'priority', 'category', 'completed']
    ordering_fields = ['created_at', 'due_at', 'priority']

    def get_queryset(self):
        # Chỉ trả về Todo của user đã đăng nhập
        return Todo.objects.filter(owner=self.request.user).order_by('-created_at')

    def perform_create(self, serializer):
        # Tự động gán owner khi tạo
        serializer.save(owner=self.request.user)

    # =========== LIST + REMINDER ===========
    def list(self, request, *args, **kwargs):
        """
        GET /api/todos/
        Ghi đè để thêm thông tin nhắc nhở vào data trả về:
        - Nếu remind_at <= now => reminder = "Đã đến thời điểm nhắc nhở!"
        - Nếu daily_reminder_time <= giờ hiện tại và chưa completed => reminder = "Đã đến thời điểm nhắc nhở hằng ngày!"
        """
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response_data = serializer.data
        else:
            serializer = self.get_serializer(queryset, many=True)
            response_data = serializer.data

        now = timezone.localtime(timezone.now())

        for todo in response_data:
            reminder_found = False

            # Nhắc 1 lần
            if todo.get('remind_at'):
                remind_at_time = timezone.datetime.fromisoformat(todo['remind_at'])
                if remind_at_time <= now:
                    todo['reminder'] = "Đã đến thời điểm nhắc nhở!"
                    reminder_found = True

            # Nhắc hằng ngày
            if (
                not reminder_found
                and todo.get('daily_reminder_time')
                and not todo.get('completed')
            ):
                daily_time = timezone.datetime.strptime(
                    todo['daily_reminder_time'], '%H:%M:%S'
                ).time()

                if now.time() >= daily_time:
                    todo['reminder'] = "Đã đến thời điểm nhắc nhở hằng ngày!"

        return Response(response_data)
    def destroy(self, request, *args, **kwargs):
        """
        Custom xoá task: bắt exception và trả JSON để debug.
        """
        instance = self.get_object()
        try:
            self.perform_destroy(instance)
        except Exception as e:
            # In ra console cho dễ thấy stacktrace
            print("ERROR_WHEN_DELETING_TODO:", repr(e))

            return Response(
                {
                    "error": "Lỗi khi xoá task",
                    "detail": str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(status=status.HTTP_204_NO_CONTENT)

    # =========== TOGGLE STATUS ===========
    @action(detail=True, methods=['patch'], url_path='toggle-status')
    def toggle_status(self, request, pk=None):
        """
        PATCH /api/todos/{id}/toggle-status/
        Đảo trạng thái completed (True/False)
        """
        todo = self.get_object()
        todo.completed = not todo.completed
        todo.save()
        serializer = self.get_serializer(todo, context={'request': request})
        return Response(serializer.data)

    # =========== CHIA SẺ CÔNG VIỆC ===========
    @action(detail=False, methods=['post'], url_path='share')
    def share_task(self, request, pk=None):
        """
        POST /api/todos/share/
        body: { "todo_id": ..., "shared_to_username": "abc", "permission": "view|edit" }

        Nếu có shared_to_username => share cho user cụ thể.
        Nếu muốn để public qua link => có thể cho FE truyền shared_to_username rỗng và xử lý riêng (hoặc ta thêm flag sau).
        """
        from django.contrib.auth.models import User

        todo_id = request.data.get('todo_id')
        shared_to_username = request.data.get('shared_to_username')
        permission = request.data.get('permission', 'view')

        if not todo_id:
            return Response(
                {'error': 'todo_id là bắt buộc'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not shared_to_username:
            return Response(
                {'error': 'shared_to_username là bắt buộc'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            todo = Todo.objects.get(id=todo_id, owner=request.user)
        except Todo.DoesNotExist:
            return Response(
                {'error': 'Công việc không tồn tại hoặc bạn không có quyền'},
                status=status.HTTP_404_NOT_FOUND
            )

        share_link = str(uuid.uuid4())[:8]

        try:
            shared_to_user = User.objects.get(username=shared_to_username)
        except User.DoesNotExist:
            return Response(
                {'error': 'Người dùng không tồn tại'},
                status=status.HTTP_404_NOT_FOUND
            )

        task_share, created = TaskShare.objects.update_or_create(
            task=todo,
            shared_to=shared_to_user,
            defaults={
                'shared_by': request.user,
                'permission': permission,
                'share_link': share_link,
            }
        )

        serializer = TaskShareSerializer(task_share)
        return Response(serializer.data,
                        status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='shared-with-me')
    def shared_with_me(self, request):
        """
        GET /api/todos/shared-with-me/
        Danh sách task được chia sẻ với tôi
        """
        shared_tasks = TaskShare.objects.filter(shared_to=request.user)
        serializer = TaskShareSerializer(shared_tasks, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='shared-by-me')
    def shared_by_me(self, request):
        """
        GET /api/todos/shared-by-me/
        Danh sách task tôi đã chia sẻ cho người khác
        """
        shared_tasks = TaskShare.objects.filter(shared_by=request.user)
        serializer = TaskShareSerializer(shared_tasks, many=True)
        return Response(serializer.data)

    # =========== EXPORT / IMPORT CSV ===========
    @action(detail=False, methods=['get'], url_path='export-csv')
    def export_csv(self, request):
        """
        GET /api/todos/export-csv/
        Xuất danh sách công việc ra CSV
        """
        todos = self.get_queryset()

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="todos.csv"'

        writer = csv.writer(response)
        writer.writerow([
            'ID', 'Tiêu đề', 'Mô tả', 'Danh mục', 'Mức ưu tiên',
            'Thời hạn', 'Nhắc nhở', 'Hoàn thành', 'Tags', 'Ngày tạo'
        ])

        for todo in todos:
            writer.writerow([
                todo.id,
                todo.title,
                todo.description,
                todo.category.name if todo.category else '',
                todo.priority,
                todo.due_at.strftime('%Y-%m-%d %H:%M') if todo.due_at else '',
                todo.remind_at.strftime('%Y-%m-%d %H:%M') if todo.remind_at else '',
                'Có' if todo.completed else 'Không',
                todo.tags,
                todo.created_at.strftime('%Y-%m-%d %H:%M')
            ])

        ExportLog.objects.create(
            user=request.user,
            format='csv',
            file_path='todos.csv',
            exported_count=todos.count()
        )

        return response

    @action(detail=False, methods=['post'], url_path='import-csv')
    def import_csv(self, request):
        """
        POST /api/todos/import-csv/
        body: multipart/form-data với field 'file'
        """
        if 'file' not in request.FILES:
            return Response(
                {'error': 'Không có file'},
                status=status.HTTP_400_BAD_REQUEST
            )

        csv_file = request.FILES['file']
        decoded_file = csv_file.read().decode('utf-8').splitlines()
        reader = csv.DictReader(decoded_file)

        created_count = 0
        errors = []

        for idx, row in enumerate(reader, 1):
            try:
                category = None
                if row.get('Danh mục'):
                    category, _ = Category.objects.get_or_create(
                        owner=request.user,
                        name=row['Danh mục']
                    )

                due_at = None
                if row.get('Thời hạn'):
                    due_at = datetime.strptime(row['Thời hạn'], '%Y-%m-%d %H:%M')

                remind_at = None
                if row.get('Nhắc nhở'):
                    remind_at = datetime.strptime(row['Nhắc nhở'], '%Y-%m-%d %H:%M')

                Todo.objects.create(
                    owner=request.user,
                    title=row['Tiêu đề'],
                    description=row.get('Mô tả', ''),
                    category=category,
                    priority=row.get('Mức ưu tiên', 'Medium'),
                    due_at=due_at,
                    remind_at=remind_at,
                    completed=row.get('Hoàn thành', 'Không').lower() == 'có',
                    tags=row.get('Tags', '')
                )
                created_count += 1
            except Exception as e:
                errors.append(f"Dòng {idx}: {str(e)}")

        return Response({
            'created': created_count,
            'errors': errors
        })

    # =========== VIEW LỊCH ===========
    @action(detail=False, methods=['get'], url_path='calendar')
    def calendar_view(self, request):
        """
        GET /api/todos/calendar/?month=&year=
        Trả về các task trong tháng, group theo ngày:
        {
          "month": 11,
          "year": 2025,
          "events": {
            "2025-11-20": [list task],
            ...
          }
        }
        """
        month = request.query_params.get('month')
        year = request.query_params.get('year')

        if not month or not year:
            now = timezone.now()
            month = now.month
            year = now.year
        else:
            month = int(month)
            year = int(year)

        from datetime import date
        start_date = date(year, month, 1)

        if month == 12:
            end_date = date(year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = date(year, month + 1, 1) - timedelta(days=1)

        todos = self.get_queryset().filter(
            due_at__date__gte=start_date,
            due_at__date__lte=end_date
        )

        calendar_data = {}
        for todo in todos:
            date_key = todo.due_at.date().isoformat()
            if date_key not in calendar_data:
                calendar_data[date_key] = []
            calendar_data[date_key].append(TodoSerializer(todo).data)

        return Response({
            'month': month,
            'year': year,
            'events': calendar_data
        })

    @action(detail=False, methods=['get'], url_path='tasks-by-date')
    def tasks_by_date(self, request):
        """
        GET /api/todos/tasks-by-date/?date=YYYY-MM-DD
        """
        date_str = request.query_params.get('date')

        if not date_str:
            return Response(
                {'error': 'date query param là bắt buộc (YYYY-MM-DD)'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return Response(
                {'error': 'Định dạng date không hợp lệ (sử dụng YYYY-MM-DD)'},
                status=status.HTTP_400_BAD_REQUEST
            )

        todos = self.get_queryset().filter(
            due_at__date=target_date
        ).order_by('due_at')

        serializer = TodoSerializer(todos, many=True)
        return Response({
            'date': target_date.isoformat(),
            'tasks': serializer.data,
            'count': len(serializer.data)
        })


# === SHARE LINK VIEW (public link access) ===
@api_view(['GET'])
@permission_classes([AllowAny])
def share_link_view(request, share_link):
    """GET: xem thông tin tối giản của task được chia sẻ bởi link"""
    try:
        ts = TaskShare.objects.get(share_link=share_link)
    except TaskShare.DoesNotExist:
        return Response({'error': 'Share link không tồn tại'}, status=status.HTTP_404_NOT_FOUND)

    data = {
        'task_id': ts.task.id,
        'task_title': ts.task.title,
        'task_description': ts.task.description,
        'permission': ts.permission,
        'shared_by': ts.shared_by.username,
        'accepted': ts.accepted,
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
        task_data['due_at'] = timezone.datetime.fromisoformat(task_data['due_at'])

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

