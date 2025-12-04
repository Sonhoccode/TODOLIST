# djangostart/views.py
from django.conf import settings
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from rest_framework.authtoken.models import Token
import os

@login_required
def redirect_after_login(request):
    # Tạo / lấy token cho user
    token, _ = Token.objects.get_or_create(user=request.user)

    # URL FE – lấy từ env, default local
    frontend = os.environ.get("FRONTEND_ORIGIN", "http://localhost:3000")
    redirect_url = f"{frontend}/home?token={token.key}"

    return redirect(redirect_url)
