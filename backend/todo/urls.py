# todo/urls.py
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
    accept_share,
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
    # API AI - PHẢI ĐẶT TRƯỚC router để tránh conflict
    path(
        "todos/predict/",
        predict_task_completion,
        name="predict-task",
    ),
    path(
        "todos/chatbot/",
        chatbot_create_task,
        name="chatbot-create-task",
    ),

    # Share link public – xem thông tin share (không cần login)
    path(
        "todos/share-link/<str:share_link>/",
        share_link_view,
        name="todos-share-link",
    ),

    # Accept share (phải login)
    path(
        "todos/share-link/<str:share_link>/accept/",
        accept_share,
        name="todos-share-accept",
    ),

    # Routers cơ bản (CRUD todo, category, report, notification)
    path("", include(router.urls)),

    # Auth chuẩn (token, password reset, social, ...)
    path("dj-rest-auth/", include("dj_rest_auth.urls")),
    path("dj-rest-auth/registration/", include("dj_rest_auth.registration.urls")),

    # Auth public (login/register REST, không cần token sẵn)
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
