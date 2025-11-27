from django.contrib import admin
from django.urls import path, include
from todo.views import PublicLoginView, PublicRegisterView
from .social_views import GoogleLogin, GitHubLogin

urlpatterns = [
    path('admin/', admin.site.urls),

    # API Todo
    path('api/', include('todo.urls')),

    # ==== AUTH CƠ BẢN ====
    # Login: override để dùng PublicLoginView (không dính TokenAuth)
    path('api/auth/login/', PublicLoginView.as_view(), name='rest_login'),

    # Register: override để dùng PublicRegisterView
    path('api/auth/registration/', PublicRegisterView.as_view(), name='rest_register'),

    # Các endpoint còn lại của dj-rest-auth (logout, password change, user, v.v.)
    path('api/auth/', include('dj_rest_auth.urls')),
    
    path("accounts/", include("allauth.urls")),

    # Social login
    path('api/auth/google/', GoogleLogin.as_view(), name='google_login'),
    path('api/auth/github/', GitHubLogin.as_view(), name='github_login'),
]
