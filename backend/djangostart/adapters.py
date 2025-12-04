from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from rest_framework.authtoken.models import Token
from django.conf import settings

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def get_login_redirect_url(self, request):
        # Get the user
        user = request.user
        
        # Get or create token
        token, created = Token.objects.get_or_create(user=user)
        
        # Frontend URL (should be in settings, but hardcoding for now based on context or reading from settings)
        frontend_url = getattr(settings, 'FRONTEND_ORIGIN', 'http://localhost:3000')
        
        # Redirect with token
        return f"{frontend_url}/auth-callback?token={token.key}"
