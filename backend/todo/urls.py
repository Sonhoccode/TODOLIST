from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    TodoViewSet,
    CategoryViewSet,
    share_link_view,
    ReportViewSet,
    NotificationSettingViewSet,
    predict_task_completion,
    chatbot_create_task,
    PublicLoginView,
    PublicRegisterView,
)

router = DefaultRouter()
router.register(r"todos", TodoViewSet, basename="todo")
router.register(r"categories", CategoryViewSet, basename="category")
router.register(r"reports", ReportViewSet, basename="report")
router.register(
    r"notifications",
    NotificationSettingViewSet,
    basename="notification",
)

urlpatterns = [
    
    path("todos/predict/", predict_task_completion, name="predict-task"),
    path("todos/chatbot/", chatbot_create_task, name="chatbot-create-task"),
    # Routers cơ bản
    path("", include(router.urls)),

    # Share link public
    path(
        "todos/share-link/<str:share_link>/",
        share_link_view,
        name="todos-share-link",
    ),
    
        # auth chuẩn
    path("dj-rest-auth/", include("dj_rest_auth.urls")),
    path("dj-rest-auth/registration/", include("dj_rest_auth.registration.urls")),

    
    path("accounts/", include("allauth.urls")),

    # Auth public (không cần token)
    path(
        "auth/login/",
        PublicLoginView.as_view(),
        name="rest_login",
    ),
    path(
        "auth/registration/",
        PublicRegisterView.as_view(),
        name="rest_register",
    ),
]
