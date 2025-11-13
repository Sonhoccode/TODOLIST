from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # API (Todo/Category) của bạn
    path('api/', include('todo.urls')),
    
    # API cho Đăng nhập/Đăng xuất/Đăng ký
    path('api/auth/', include('dj_rest_auth.urls')),
    path('api/auth/registration/', include('dj_rest_auth.registration.urls')),

    # Chuyển hướng trang gốc về /api/
    path('', RedirectView.as_view(url='/api/', permanent=False)),
]