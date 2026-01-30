"""
Benchmark login performance
Tests authentication speed with current configuration
"""
import os
import sys
import django
import time
from datetime import datetime

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djangostart.settings')
django.setup()

from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.conf import settings

def get_password_hasher_name():
    """Get current password hasher"""
    hashers = settings.PASSWORD_HASHERS
    return hashers[0].split('.')[-1] if hashers else 'Unknown'

def benchmark_login(username='testuser', password='testpass123', iterations=10):
    """Benchmark login performance"""
    print("=" * 70)
    print("LOGIN PERFORMANCE BENCHMARK")
    print("=" * 70)
    
    # Get or create test user
    user, created = User.objects.get_or_create(username=username)
    if created or not user.check_password(password):
        user.set_password(password)
        user.save()
        print(f"\n✓ Test user '{username}' created/updated")
    else:
        print(f"\n✓ Using existing test user '{username}'")
    
    # Get password hasher info
    hasher_name = get_password_hasher_name()
    hash_algorithm = user.password.split('$')[0] if '$' in user.password else 'Unknown'
    
    print(f"✓ Password Hasher: {hasher_name}")
    print(f"✓ Current Hash Algorithm: {hash_algorithm}")
    
    # Check cache backend
    cache_backend = settings.CACHES['default']['BACKEND']
    cache_type = 'Redis' if 'redis' in cache_backend.lower() else 'LocMem'
    print(f"✓ Cache Backend: {cache_type}")
    
    print(f"\n→ Running {iterations} login attempts...")
    print("-" * 70)
    
    times = []
    for i in range(iterations):
        start = time.perf_counter()
        authenticated_user = authenticate(username=username, password=password)
        end = time.perf_counter()
        
        elapsed_ms = (end - start) * 1000
        times.append(elapsed_ms)
        
        status = "✓" if authenticated_user else "✗"
        print(f"  {status} Attempt {i+1:2d}: {elapsed_ms:6.2f}ms")
    
    # Calculate statistics
    avg_time = sum(times) / len(times)
    min_time = min(times)
    max_time = max(times)
    
    print("-" * 70)
    print(f"\n📊 RESULTS:")
    print(f"  • Average: {avg_time:.2f}ms")
    print(f"  • Minimum: {min_time:.2f}ms")
    print(f"  • Maximum: {max_time:.2f}ms")
    
    # Performance rating
    print(f"\n🎯 PERFORMANCE RATING:")
    if avg_time < 100:
        rating = "EXCELLENT 🚀"
        color = "green"
    elif avg_time < 200:
        rating = "GOOD ✓"
        color = "yellow"
    elif avg_time < 400:
        rating = "ACCEPTABLE ⚠"
        color = "orange"
    else:
        rating = "SLOW ✗"
        color = "red"
    
    print(f"  {rating} - Average login time: {avg_time:.2f}ms")
    
    # Recommendations
    if hash_algorithm != 'argon2':
        print(f"\n💡 RECOMMENDATION:")
        print(f"  Current hash: {hash_algorithm}")
        print(f"  → Login again to upgrade to Argon2 (3-5x faster)")
        print(f"  → Django will auto-upgrade on next successful login")
    
    print("\n" + "=" * 70)
    
    return {
        'hasher': hasher_name,
        'hash_algorithm': hash_algorithm,
        'cache_backend': cache_type,
        'avg_time': avg_time,
        'min_time': min_time,
        'max_time': max_time,
        'iterations': iterations
    }

if __name__ == '__main__':
    print(f"\n🔐 Testing login performance at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Run benchmark
    results = benchmark_login(iterations=10)
    
    print("\n✅ Benchmark completed!")
    print("\nTo see the improvement:")
    print("  1. Login via API/frontend with your account")
    print("  2. Run this script again")
    print("  3. Compare the results\n")
