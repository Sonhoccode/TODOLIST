import os
import django
import sys

# Setup Django environment
sys.path.append(os.path.join(os.getcwd(), 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djangostart.settings')
django.setup()

from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp

def inspect_full():
    print("=== Full DB Inspection ===")
    
    print("\n--- Sites ---")
    for s in Site.objects.all():
        print(f"ID={s.id}, Domain='{s.domain}', Name='{s.name}'")
        
    print("\n--- SocialApps ---")
    apps = SocialApp.objects.all()
    if not apps.exists():
        print("No SocialApps found.")
    
    for app in apps:
        print(f"ID={app.id}")
        print(f"  Provider: '{app.provider}'")
        print(f"  Name: '{app.name}'")
        print(f"  Client ID: '{app.client_id}'")
        print(f"  Sites: {[s.id for s in app.sites.all()]}")
        print("-" * 20)

if __name__ == "__main__":
    inspect_full()
