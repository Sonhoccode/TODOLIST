"""
Script test chatbot parsing
Chạy: python test_chatbot.py
"""
import os
import sys
import django

sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djangostart.settings')
django.setup()

from todo.services.chatbot import TaskChatbot

chatbot = TaskChatbot()

test_messages = [
    "Thêm task học Python 2 tiếng chiều mai",
    "Tạo task họp team urgent 1 giờ hôm nay",
    "Làm báo cáo 3 tiếng vào 14h ngày mai",
    "Học tiếng Anh 45 phút sáng mai",
    "Task quan trọng: Review code 30 phút lúc 9h",
    "Tập thể dục 1 tiếng tối nay",
]

print("=" * 60)
print("TEST CHATBOT PARSING")
print("=" * 60)

for i, message in enumerate(test_messages, 1):
    print(f"\n📝 Test {i}: {message}")
    print("-" * 60)
    
    result = chatbot.parse_message(message)
    
    print(f"   Title: {result['title']}")
    print(f"   Priority: {result['priority']}")
    print(f"   Duration: {result['estimated_duration_min']} phút")
    
    if result['due_at']:
        print(f"   Due at: {result['due_at']}")
    if result['planned_start_at']:
        print(f"   Start at: {result['planned_start_at']}")

print("\n" + "=" * 60)
print("✅ Test hoàn tất!")
print("=" * 60)
