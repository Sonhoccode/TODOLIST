from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Todo, Category
from .serializers import TodoSerializer, CategorySerializer
from rest_framework.permissions import IsAuthenticated # <-- Đã bật


class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated] # <-- Đã bật
    
    def get_queryset(self):
        # Chỉ trả về Category của user đã đăng nhập
        return Category.objects.filter(owner=self.request.user)
        
    def perform_create(self, serializer):
        # Tự động gán owner khi tạo
        serializer.save(owner=self.request.user)


class TodoViewSet(viewsets.ModelViewSet):
    serializer_class = TodoSerializer
    permission_classes = [IsAuthenticated] # <-- Đã bật
    
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    
    # Cập nhật các trường filter để khớp với Model mới
    search_fields = ['title', 'description', 'tags']
    filterset_fields = ['created_at', 'due_at', 'priority', 'category', 'completed']
    ordering_fields = ['created_at', 'due_at', 'priority']

    def get_queryset(self):
        # Chỉ trả về Todo của user đã đăng nhập
        return Todo.objects.filter(owner=self.request.user).order_by('-created_at')

    def perform_create(self, serializer):
        # Tự động gán owner khi tạo
        serializer.save(owner=self.request.user)
    
    def list(self, request, *args, **kwargs):
        """
        Ghi đè (override) hàm 'list' (GET /api/todos/)
        Mục đích: Thêm thông tin nhắc nhở (reminder) vào data trả về.
        (Đã cập nhật để kiểm tra cả nhắc 1 lần và hằng ngày)
        """
        
        # Lấy queryset đã được lọc (chỉ của user này)
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response_data = serializer.data
        else:
            serializer = self.get_serializer(queryset, many=True)
            response_data = serializer.data

        # Lấy thời gian hiện tại theo múi giờ của server (đã set trong settings.py)
        now = timezone.localtime(timezone.now())
        
        for todo in response_data:
            reminder_found = False
            
            # 1. Kiểm tra nhắc nhở MỘT LẦN (remind_at)
            if todo['remind_at']:
                remind_at_time = timezone.datetime.fromisoformat(todo['remind_at'])
                if remind_at_time <= now:
                    todo['reminder'] = "Đã đến thời điểm nhắc nhở!"
                    reminder_found = True

            # 2. Nếu không có nhắc 1 lần, kiểm tra nhắc HẰNG NGÀY
            if not reminder_found and todo['daily_reminder_time'] and not todo['completed']:
                daily_time = timezone.datetime.strptime(todo['daily_reminder_time'], '%H:%M:%S').time()
                
                # So sánh giờ hiện tại (local) với giờ nhắc hằng ngày
                if now.time() >= daily_time:
                    todo['reminder'] = "Đã đến thời điểm nhắc nhở hằng ngày!"

        return Response(response_data)

    
    @action(detail=True, methods=['patch'], url_path='toggle-status')
    def toggle_status(self, request, pk=None):
        """
        Action này dùng để Bật/Tắt trạng thái 'completed' (boolean).
        """
        todo = self.get_object()
        
        # Sửa logic để dùng trường 'completed' (boolean)
        todo.completed = not todo.completed # Đảo ngược trạng thái
            
        todo.save()
        serializer = self.get_serializer(todo)
        return Response(serializer.data)