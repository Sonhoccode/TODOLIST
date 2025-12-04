from django.contrib import admin
from django.urls import path, include
from todo.views import PublicLoginView, PublicRegisterView
from .social_views import GoogleLogin, GitHubLogin
from .views import redirect_after_login   # <--- thêm

urlpatterns = [
    path('admin/', admin.site.urls),

    path('api/', include('todo.urls')),

    path('api/auth/login/', PublicLoginView.as_view(), name='rest_login'),
    path('api/auth/registration/', PublicRegisterView.as_view(), name='rest_register'),
    path('api/auth/', include('dj_rest_auth.urls')),

    # redirect sau khi allauth login xong
    path(
        "accounts/redirect-after-login/",
        redirect_after_login,
        name="redirect_after_login",
    ),

    path("accounts/", include("allauth.urls")),

    path('api/auth/google/', GoogleLogin.as_view(), name='google_login'),
    path('api/auth/github/', GitHubLogin.as_view(), name='github_login'),
]
