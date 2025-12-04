import os
import django
import sys

# Setup Django environment
sys.path.append(os.path.join(os.getcwd(), 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djangostart.settings')
django.setup()

from allauth.socialaccount.adapter import get_adapter
from django.test import RequestFactory
from allauth.socialaccount.models import SocialApp

def test_get_app():
    print("=== Testing get_app ===")
    request = RequestFactory().get('/')
    adapter = get_adapter(request)
    
    print(f"Adapter: {adapter}")
    
    try:
        # Try to get app for google
        print("Attempting to get 'google' app...")
        app = adapter.get_app(request, provider='google')
        print(f"Success! Got app: {app.name} (ID={app.id})")
        print(f"Client ID: {app.client_id}")
    except Exception as e:
        print(f"FAILED: {type(e).__name__}: {e}")
        
    # Check DB directly again
    print("\nDirect DB Check:")
    apps = SocialApp.objects.filter(provider='google')
    print(f"Count: {apps.count()}")
    for a in apps:
        print(f" - {a.name} (ID={a.id}) Sites={[s.id for s in a.sites.all()]}")

if __name__ == "__main__":
    test_get_app()
