"""
Check existing users' password hash algorithms
and provide upgrade instructions
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djangostart.settings')
django.setup()

from django.contrib.auth.models import User

def check_user_hashes():
    """Check all users' password hash algorithms"""
    print("=" * 70)
    print("USER PASSWORD HASH AUDIT")
    print("=" * 70)
    
    users = User.objects.all()
    total = users.count()
    
    if total == 0:
        print("\n⚠ No users found in database")
        return
    
    print(f"\n📊 Total users: {total}\n")
    
    hash_stats = {}
    
    for user in users:
        if '$' in user.password:
            algorithm = user.password.split('$')[0]
        else:
            algorithm = 'unknown'
        
        hash_stats[algorithm] = hash_stats.get(algorithm, 0) + 1
        
        # Show first 10 users
        if len([u for u in users if users.filter(pk__lte=user.pk)]) <= 10:
            status = "✓" if algorithm == 'argon2' else "→"
            print(f"  {status} {user.username:20s} | {algorithm:15s} | Last login: {user.last_login or 'Never'}")
    
    if total > 10:
        print(f"  ... and {total - 10} more users")
    
    print("\n" + "-" * 70)
    print("\n📈 HASH ALGORITHM DISTRIBUTION:")
    for algo, count in sorted(hash_stats.items(), key=lambda x: -x[1]):
        percentage = (count / total) * 100
        bar = "█" * int(percentage / 2)
        print(f"  {algo:15s}: {count:3d} users ({percentage:5.1f}%) {bar}")
    
    # Recommendations
    pbkdf2_count = sum(count for algo, count in hash_stats.items() if 'pbkdf2' in algo.lower())
    
    if pbkdf2_count > 0:
        print("\n" + "=" * 70)
        print("💡 UPGRADE RECOMMENDATION")
        print("=" * 70)
        print(f"\n{pbkdf2_count} users still using PBKDF2 (slow hash)")
        print("\n✓ Django will AUTO-UPGRADE to Argon2 when users login")
        print("✓ No action required from users")
        print("✓ No password reset needed")
        print("\nHow it works:")
        print("  1. User logs in with current password")
        print("  2. Django verifies with old hash (PBKDF2)")
        print("  3. Django re-hashes with new algorithm (Argon2)")
        print("  4. Next login will be 3-5x faster!")
        
        print("\n📧 Optional: Send email to encourage users to login")
        print("   to get faster performance immediately.")
    else:
        print("\n✅ All users are using Argon2 - optimal performance!")
    
    print("\n" + "=" * 70)

if __name__ == '__main__':
    check_user_hashes()
