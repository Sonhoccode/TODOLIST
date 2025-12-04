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

def fix_social_app():
    print("=== Fixing SocialApp Configuration ===")
    
    try:
        site = Site.objects.get(id=settings.SITE_ID)
        print(f"Current Site: {site.domain} (ID={site.id})")
        
        # Get settings config
        providers = getattr(settings, 'SOCIALACCOUNT_PROVIDERS', {})
        google_conf = providers.get('google', {})
        app_conf = google_conf.get('APP', {})
        
        env_client_id = app_conf.get('client_id')
        env_secret = app_conf.get('secret')
        
        if not env_client_id or not env_secret:
            print("ERROR: Google Client ID or Secret missing in settings/env!")
            return

        # Find or Create SocialApp
        # We search by provider.
        apps = SocialApp.objects.filter(provider='google')
        
        if apps.exists():
            app = apps.first()
            print(f"Found existing SocialApp: {app.name}")
        else:
            print("No SocialApp found in DB. Creating one...")
            app = SocialApp(provider='google', name='Google')
        
        # Update credentials from env
        if app.client_id != env_client_id or app.secret != env_secret:
            print("Updating SocialApp credentials to match .env/settings...")
            app.client_id = env_client_id
            app.secret = env_secret
            app.name = "Google (Synced)"
            app.save()
        else:
            print("SocialApp credentials match settings.")
            
        # Link Site
        if not app.sites.filter(id=site.id).exists():
            print(f"Linking Site {site.domain} to SocialApp...")
            app.sites.add(site)
            print("Site linked.")
        else:
            print("Site already linked.")
            
        print("=== Fix Complete ===")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    fix_social_app()
