# djangostart/views.py
from django.conf import settings
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from rest_framework.authtoken.models import Token

@login_required
def redirect_after_login(request):
    token, _ = Token.objects.get_or_create(user=request.user)
    frontend_url = getattr(settings, "FRONTEND_URL", "http://localhost:3000")
    redirect_url = f"{frontend_url}/home?token={token.key}"
    return redirect(redirect_url)
