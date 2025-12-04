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

def fix_duplicates():
    print("=== Fixing Duplicate SocialApps ===")
    
    try:
        site = Site.objects.get(id=settings.SITE_ID)
        print(f"Current Site: {site.domain} (ID={site.id})")
        
        apps = SocialApp.objects.filter(provider='google')
        count = apps.count()
        print(f"Found {count} Google SocialApps.")
        
        if count > 1:
            print("Duplicates detected! Cleaning up...")
            
            # Keep the one we likely just updated (or the first one)
            # We can try to find one that is already linked to this site
            
            kept_app = None
            for app in apps:
                print(f" - App ID={app.id}, Name='{app.name}', Sites={[s.id for s in app.sites.all()]}")
                
                if kept_app is None:
                    kept_app = app
                else:
                    # If we already have a kept_app, check if this one is 'better' (e.g. linked to site)
                    if site in app.sites.all() and site not in kept_app.sites.all():
                        kept_app = app
            
            print(f"Keeping App ID={kept_app.id} ('{kept_app.name}')")
            
            for app in apps:
                if app.id != kept_app.id:
                    print(f"Deleting duplicate App ID={app.id} ('{app.name}')...")
                    app.delete()
            
            # Ensure kept app is linked
            if site not in kept_app.sites.all():
                kept_app.sites.add(site)
                print("Linked site to kept app.")
                
        elif count == 1:
            print("Only 1 app found. Verifying site link...")
            app = apps.first()
            if site not in app.sites.all():
                app.sites.add(site)
                print("Linked site to app.")
            else:
                print("App is already correctly linked.")
        else:
            print("No apps found!")

        print("=== Cleanup Complete ===")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    fix_duplicates()
