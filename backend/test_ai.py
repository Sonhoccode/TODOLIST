"""
Script test nhanh cho AI prediction
Chạy: python test_ai.py
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djangostart.settings')
django.setup()

from todo.services.ai import predict_task_on_time

# Test case 1: Task có khả năng hoàn thành đúng hạn
class TestTask1:
    priority = "High"
    estimated_duration_min = 30
    
    @property
    def priority_numeric(self):
        return 3
    
    @property
    def start_hour(self):
        return 9
    
    @property
    def day_of_week(self):
        return 2
    
    @property
    def effective_duration_min(self):
        return 30

# Test case 2: Task có nguy cơ trễ hạn
class TestTask2:
    priority = "Low"
    estimated_duration_min = 180
    
    @property
    def priority_numeric(self):
        return 1
    
    @property
    def start_hour(self):
        return 22
    
    @property
    def day_of_week(self):
        return 7
    
    @property
    def effective_duration_min(self):
        return 180

print("=" * 50)
print("TEST AI PREDICTION")
print("=" * 50)

print("\n📋 Test Case 1: Task ưu tiên cao, 30 phút, bắt đầu 9h sáng thứ 2")
task1 = TestTask1()
result1 = predict_task_on_time(task1, return_confidence=True)
print(f"   Kết quả: {'✅ Đúng hạn' if result1['on_time_prediction'] == 1 else '⚠️ Trễ hạn'}")
print(f"   Độ tin cậy: {result1['confidence']*100:.1f}%")

print("\n📋 Test Case 2: Task ưu tiên thấp, 180 phút, bắt đầu 10h tối Chủ nhật")
task2 = TestTask2()
result2 = predict_task_on_time(task2, return_confidence=True)
print(f"   Kết quả: {'✅ Đúng hạn' if result2['on_time_prediction'] == 1 else '⚠️ Trễ hạn'}")
print(f"   Độ tin cậy: {result2['confidence']*100:.1f}%")

print("\n" + "=" * 50)
print("✅ Test hoàn tất!")
print("=" * 50)
