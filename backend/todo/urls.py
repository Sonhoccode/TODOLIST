from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TodoViewSet, CategoryViewSet, predict_task_completion, chatbot_create_task

router = DefaultRouter()
router.register(r'todos', TodoViewSet, basename='todo')
router.register(r'categories', CategoryViewSet, basename='category')

urlpatterns = [
    path('', include(router.urls)),
    path('predict/', predict_task_completion, name='predict-task'),
    path('chatbot/', chatbot_create_task, name='chatbot-create-task'),
]