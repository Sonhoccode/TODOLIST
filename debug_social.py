import os
import django
import sys

# Setup Django environment
sys.path.append(os.path.join(os.getcwd(), 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djangostart.settings')
django.setup()

from django.contrib.sites.models import Site
from django.conf import settings
from allauth.socialaccount.models import SocialApp
from django.urls import reverse

def debug_social_login():
    print("=== Debugging Social Login ===")
    
    # 1. Check Site
    site = Site.objects.get(id=settings.SITE_ID)
    print(f"SITE_ID: {settings.SITE_ID}")
    print(f"Site Domain: {site.domain}")
    print(f"Site Name: {site.name}")
    
    # 2. Check Settings
    print(f"ACCOUNT_DEFAULT_HTTP_PROTOCOL: {getattr(settings, 'ACCOUNT_DEFAULT_HTTP_PROTOCOL', 'Not Set')}")
    print(f"SOCIALACCOUNT_LOGIN_ON_GET: {getattr(settings, 'SOCIALACCOUNT_LOGIN_ON_GET', 'Not Set')}")
    
    # 3. Check Google Config in Settings
    providers = getattr(settings, 'SOCIALACCOUNT_PROVIDERS', {})
    google_conf = providers.get('google', {})
    app_conf = google_conf.get('APP', {})
    
    client_id = app_conf.get('client_id')
    secret = app_conf.get('secret')
    
    print(f"Google Client ID (Settings): {'Present' if client_id else 'MISSING'}")
    print(f"Google Secret (Settings): {'Present' if secret else 'MISSING'}")
    
    # 4. Check SocialApp in DB
    apps = SocialApp.objects.filter(provider='google')
    print(f"SocialApps in DB (provider='google'): {apps.count()}")
    for app in apps:
        print(f" - DB App: Name='{app.name}', ClientID='{app.client_id[:5]}...', Sites={[s.domain for s in app.sites.all()]}")
        
    # 5. Check Callback URL
    try:
        callback_path = reverse('google_callback')
        print(f"Callback Path (reverse 'google_callback'): {callback_path}")
    except Exception as e:
        print(f"Could not reverse 'google_callback': {e}")
        # Try allauth default
        try:
            from allauth.socialaccount.providers.google.urls import urlpatterns
            print("Found google provider urls.")
        except:
            pass

    # 6. Check Session Config
    print(f"SESSION_COOKIE_DOMAIN: {getattr(settings, 'SESSION_COOKIE_DOMAIN', 'Not Set')}")
    print(f"CSRF_TRUSTED_ORIGINS: {getattr(settings, 'CSRF_TRUSTED_ORIGINS', [])}")

if __name__ == "__main__":
    debug_social_login()
