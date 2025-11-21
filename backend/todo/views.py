from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from rest_framework.response import Response
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.http import JsonResponse, HttpResponseBadRequest
from .models import Todo, Category
from .serializers import TodoSerializer, CategorySerializer
from .services.ai import predict_task_on_time
import json


class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Category.objects.filter(owner=self.request.user)
        
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class TodoViewSet(viewsets.ModelViewSet):
    serializer_class = TodoSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description', 'tags']
    filterset_fields = ['created_at', 'due_at', 'priority', 'category', 'completed']
    ordering_fields = ['created_at', 'due_at', 'priority']

    def get_queryset(self):
        return Todo.objects.filter(owner=self.request.user).order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
    
    def list(self, request, *args, **kwargs):
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
            
            if todo['remind_at']:
                remind_at_time = timezone.datetime.fromisoformat(todo['remind_at'])
                if remind_at_time <= now:
                    todo['reminder'] = "Đã đến thời điểm nhắc nhở!"
                    reminder_found = True

            if not reminder_found and todo['daily_reminder_time'] and not todo['completed']:
                daily_time = timezone.datetime.strptime(todo['daily_reminder_time'], '%H:%M:%S').time()
                if now.time() >= daily_time:
                    todo['reminder'] = "Đã đến thời điểm nhắc nhở hằng ngày!"

        return Response(response_data)
    
    @action(detail=True, methods=['patch'], url_path='toggle-status')
    def toggle_status(self, request, pk=None):
        todo = self.get_object()
        todo.completed = not todo.completed
        todo.save()
        serializer = self.get_serializer(todo)
        return Response(serializer.data)


# AI Prediction API
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def predict_task_completion(request):
    try:
        data = json.loads(request.body.decode())
    except Exception:
        return HttpResponseBadRequest("JSON không hợp lệ")

    task_id = data.get("task_id")
    if task_id:
        try:
            task = Todo.objects.get(id=task_id, owner=request.user)
        except Todo.DoesNotExist:
            return HttpResponseBadRequest("Task không tồn tại")
        result = predict_task_on_time(task, return_confidence=True)
        return JsonResponse(result)

    if "priority" not in data:
        return HttpResponseBadRequest("Thiếu trường: priority")

    class DummyTask:
        def __init__(self, data):
            self.priority = data.get("priority", "Medium")
            self.estimated_duration_min = data.get("estimated_duration_min")
            self.planned_start_at = None
            self.created_at = timezone.now()
            
        @property
        def priority_numeric(self):
            mapping = {"Low": 1, "low": 1, "Medium": 2, "medium": 2, "High": 3, "high": 3, "Urgent": 3, "urgent": 3}
            return mapping.get(self.priority, 2)
    
    task = DummyTask(data)
    result = predict_task_on_time(task, extra_data=data, return_confidence=True)
    return JsonResponse(result)


# Chatbot API
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def chatbot_create_task(request):
    """
    Chatbot endpoint: Parse message và tạo task
    Input: { "message": "Thêm task học Python 2 tiếng chiều mai" }
    Output: { "task": {...}, "response": "...", "prediction": {...} }
    """
    from .services.chatbot import TaskChatbot
    
    message = request.data.get('message', '').strip()
    if not message:
        return HttpResponseBadRequest("Message không được trống")
    
    # Parse message thành task data
    chatbot = TaskChatbot()
    task_data = chatbot.parse_message(message)
    
    # Tạo task
    task_data['owner'] = request.user
    task_data['completed'] = False
    task_data['tags'] = ''
    
    # Convert ISO string về datetime
    if task_data.get('due_at'):
        task_data['due_at'] = timezone.datetime.fromisoformat(task_data['due_at'].replace('Z', '+00:00'))
    if task_data.get('planned_start_at'):
        task_data['planned_start_at'] = timezone.datetime.fromisoformat(task_data['planned_start_at'].replace('Z', '+00:00'))
    
    task = Todo.objects.create(**task_data)
    
    # Get AI prediction
    prediction = None
    try:
        prediction = predict_task_on_time(task, return_confidence=True)
    except Exception as e:
        print(f"Prediction error: {e}")
    
    # Generate response
    response_text = chatbot.generate_response(
        TodoSerializer(task).data,
        prediction
    )
    
    return JsonResponse({
        'task': TodoSerializer(task).data,
        'response': response_text,
        'prediction': prediction
    })
