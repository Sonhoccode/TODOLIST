# todo/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    PublicRegisterView,
    TodoViewSet, CategoryViewSet, share_link_view,
    ReportViewSet, NotificationSettingViewSet,
    predict_task_completion, chatbot_create_task,
)

router = DefaultRouter()
router.register(r'todos', TodoViewSet, basename='todo')
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'reports', ReportViewSet, basename='report')
router.register(r'notifications', NotificationSettingViewSet, basename='notification')

urlpatterns = [
    # ====== API AI, share-link, v.v. ĐỂ TRƯỚC ROUTER ======
    path('todos/predict/', predict_task_completion, name='predict-task'),
    path('todos/chatbot/', chatbot_create_task, name='chatbot-create-task'),
    path('todos/share-link/<str:share_link>/', share_link_view, name='todos-share-link'),

    # ====== ROUTER ĐỂ SAU CÙNG ======
    path('', include(router.urls)),

    # Đăng ký (nếu còn cần để ở đây, nếu không thì xoá, vì đã có trong djangostart/urls.py)
    path('auth/registration/', PublicRegisterView.as_view(), name='rest_register'),
]
