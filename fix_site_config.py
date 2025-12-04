import os
import django
import sys

# Setup Django environment
sys.path.append(os.path.join(os.getcwd(), 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djangostart.settings')
django.setup()

from django.contrib.sites.models import Site
from django.conf import settings

def check_and_fix_site():
    print(f"Current SITE_ID: {settings.SITE_ID}")
    
    try:
        site = Site.objects.get(id=settings.SITE_ID)
        print(f"Current Site (ID={site.id}): Domain='{site.domain}', Name='{site.name}'")
        
        # Check if we need to update
        target_domain = "localhost:8000"
        target_name = "localhost"
        
        if site.domain != target_domain:
            print(f"Updating Site domain to '{target_domain}'...")
            site.domain = target_domain
            site.name = target_name
            site.save()
            print("Site updated successfully.")
        else:
            print("Site configuration looks correct.")
            
    except Site.DoesNotExist:
        print(f"Site with ID={settings.SITE_ID} does not exist! Creating it...")
        Site.objects.create(id=settings.SITE_ID, domain="localhost:8000", name="localhost")
        print("Site created.")

if __name__ == "__main__":
    check_and_fix_site()
